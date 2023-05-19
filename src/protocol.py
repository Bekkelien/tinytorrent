import json
import socket
import math
from enum import Enum
from struct import pack, unpack
from dataclasses import dataclass
from bitstring import BitArray
#from functools import lru_cache

# Internals
from src.config import Config
from src.helpers import iprint, eprint, wprint, dprint, timer

# Configuration settings
config = Config().get_config()

class Message(Enum):
    choke = 0
    unchoke = 1
    interested = 2
    notinterested = 3
    have = 4
    bitfield = 5
    request = 6
    piece = 7
    cancel = 8
    port = 9

@dataclass
class Handshake: 
    pstrlen = b'\x13'                
    pstr =  b'BitTorrent protocol' 
    reserved = b'\x00\x00\x00\x00\x00\x00\x00\x00'
    #reserved = b'\x00\x00\x00\x00\x00\x10\x00\x00'

@dataclass
class Extensions:
    fast_extensions = b'\x04' # Not implemented
    exception_protocol = 16 # == b'\x10'== BEP 10

@dataclass
class Clients:
    clients = json.load(open('./src/clients.json'))
    def _peer_client_software(self, peer_id):
        client_id = peer_id[1:3].decode("utf-8", "ignore") 

        if Clients.clients.get(client_id) == None:
            wprint("Unknown client software for peer id:", peer_id, "TODO: Implement some verification here?")
        else:
            iprint("Peer client:", Clients.clients[client_id])
 
class PeerMessage():
    def __init__(self, clientSocket):
        self.clientSocket = clientSocket
    
    # TODO: Rename function 
    def state_message(self, message, length=1) -> str:
        # NOTE: Currently assuming we are choked if we don't get a state message back from the peer
        if message.value >= 0:
            iprint("Sending an:", message, "message to peer")

            # Send message to peer 
            message = pack('>Ib', length, message.value)
            self.clientSocket.send(message)

            # Response from peer TODO:
            try:
                response = self.clientSocket.recv(config['tcp']['state_message_buffer']) 
            except:
                return Message.choke.value  # NOTE:

            if len(response) == 5: # TODO: Improve error handling
                response = unpack('>Ib', response)

            else:
                wprint("Peer state message can't be unpacked, response not correct length")
                return Message.choke.value # NOTE: If we get here we will fail later due to assuming unchoke

            # Validation NOTE: not really a validation function just checks the response length
            if response[0] == length:
                #iprint("Peer response:", Message(response[1]).name) # BUG: Fail if response is not a int
                peer_state = Message(response[1]).value
                return peer_state # TODO:::

            else:
                wprint("Peer message failed, unknown prefix/length")

        else:
            eprint("Keep alive message not supported for this client ATM") 

        return Message.choke.value  # TODO:::

    # TODO: Function to handle the peer response -> Currently assuming that we get an unchoke on interested message
    # Merge else statements 


    def bitfield(clientSocket, response = []) -> bytes:
        """ 
        Receives a bitfield response and validates it 
        Returns empty bit array if invalid 

        """
        try:
            response = clientSocket.recv(4096) # TODO: Set buffer in config 
            bitfield_id = unpack('>b', response[4:5])[0]

        except:
            wprint("Peer did not send a bitfield message in a timely manner")
            return b''

        if bitfield_id == Message.bitfield.value:
            bitfield_payload = response[5:]
            iprint("Bitfield received")
            return bitfield_payload

        else:
            wprint("Bitfield message invalid")
            return b''

    def bitfield_status(bitfield_payload, metadata) -> str:

        dprint("Bitfield payload from peer:", BitArray(bitfield_payload).bin)
        
        if bitfield_payload:
            if metadata['bitfield_expectation'] == BitArray(bitfield_payload).bin:
                return 'seeder' # Peer has 100% of data 
        
        return 'leecher' # Peer has x % of data 


class PeerWire():
    def __init__(self, metadata):
        self.metadata = metadata
        self.peers_connected = [] # NOTE: This is not really a good solution to store in a list, hard to remove invalid peers or update status
        self.piece_hax = [] # TODO: HAX TEMP
        self.torrent_data = b''

    def _extensions(self, reserved):
        if reserved[5]  == Extensions.exception_protocol:
            iprint("Peer support extension protocol: BEP 10 - Extension Protocol for Peers to Send Arbitrary Data")

    def _peer_client_software(self, peer_id):
        client_id = peer_id[1:3].decode("utf-8", "ignore") 

        if Clients.clients.get(client_id) == None:
            wprint("Unknown client software for peer id:", peer_id, "TODO: Implement some verification here?")
        else:
            iprint("Peer client:", Clients.clients[client_id])

    @timer
    def handshake(self, peer_ip, haxhax): 
        """ 
        'BitTorrent protocol' 1.0

        Handshake:
        <len(pstr)><pstr><reserved><info_hash><peer_id> 
        
        """
        # HAX: client_address NOTE: new all adresses for testing
        peer_ip = peer_ip[haxhax]

        message = pack('>1s19s8s20s20s',Handshake.pstrlen,
                                        Handshake.pstr,
                                        Handshake.reserved, \
                                        self.metadata['info_hash'], 
                                        config['client']['peer_id'].encode())
        
        # Network setup TCP socket
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.settimeout(config['tcp']['timeout'])

        try:  
            iprint("Connecting to peer:", peer_ip[0], "::" , peer_ip[1])

            clientSocket.connect((tuple(peer_ip)))
            clientSocket.send(message)
            response = clientSocket.recv(config['tcp']['handshake_buffer']) 

            iprint("Connected to peer", peer_ip[0], "::" , peer_ip[1])

        
        except Exception as e: # TODO Improve this
            dprint("Connect to peer failed with exception:", e)
            return False
        
        # TODO :: Create a function for this!

        # Verify that the handshake response is of the expected type
        if 49 <= len(response) <= 67:
            wprint("Handshake response of type: compact peer formate is not supported")
    
        elif len(response) >= 68:
            response = unpack('>1s19s8s20s20s', response[0:68])

            # Parse handshake response (Bytes) b'data'
            handshake_pstrlen = response[0]
            handshake_pstr = response[1]
            handshake_reserved = response[2]            
            handshake_info_hash = response[3]
            handshake_client_id = response[4]
            
            if (Handshake.pstrlen + Handshake.pstr) != handshake_pstrlen + handshake_pstr:
                wprint("Handshake response failed unknown protocol:", handshake_pstr.decode("utf-8", "ignore"))
                return False

            # Validate
            if self.metadata['info_hash'] == handshake_info_hash:
                iprint("Handshake accepted")
                self._extensions(handshake_reserved) # NOTE: No handling ATM
                self._peer_client_software(handshake_client_id)

                # Check for bitfield response
                bitfield_payload = PeerMessage.bitfield(clientSocket)
                bitfield_status = PeerMessage.bitfield_status(bitfield_payload, self.metadata)

                # Send interested message to try to unchoke the peer
                message_state = PeerMessage(clientSocket).state_message(Message.interested) # TODO Fix function allot 

                iprint("Peer responded with:", Message(message_state).name)

                # Error print just used for debugging ATM
                if bitfield_status == 'seeder' and Message(message_state).name == Message.unchoke.name:

                #if bitfield_status == 'seeder': # Optimistic to request data from possible choked seeder (NOTE: TESTING)
                    dprint("TESTING seeder with current state:", Message(message_state).name)
                    return clientSocket #, [peer_ip, bitfield_status, Message(message_state).name]

            return ''
                
                # TODO: Make a system to keep track of peers and their status
                # NOTE: Client sockets are not closed? 
                # TODO: Make async 
                # STOP FUNCTION HERE