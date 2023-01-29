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
    # keepalive = -1 #BUG
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

 
class PeerMessage():
    def __init__(self, clientSocket):
        self.clientSocket = clientSocket
    
    # TODO: Rename function 
    def state_message(self, message, length=1) -> str:
        
        if message.value >= 0:
            iprint("Sending an:", message, "message to peer")

            # Send message to peer 
            message = pack('>Ib', length, message.value)
            self.clientSocket.send(message)

            # Response from peer
            response = self.clientSocket.recv(config['tcp']['state_message_buffer']) 
            if len(response) == 5: # TODO: Improve error handling
                response = unpack('>Ib', response)

            else:
                wprint("Peer state message can't be unpacked, response not correct length")
                return # NOTE: If we get here we will fail later due to assuming unchoke

            # Validation NOTE: not really a validation function just checks the response length
            if response[0] == length:
                #iprint("Peer response:", Message(response[1]).name) # BUG: Fail if response is not a int
                peer_state = Message(response[1]).value
                return peer_state # TODO:::

            else:
                wprint("Peer message failed, unknown prefix/length")

        else:
            eprint("Keep alive message not supported for this client ATM") 

        return None # TODO:::
    # TODO: Function to handle the peer response -> Currently assuming that we get an unchoke on interested message
    # Merge else statements 



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
    def handshake(self, client_address, haxhax) -> bool: 
        """ 
        'BitTorrent protocol' 1.0

        Handshake:
        <len(pstr)><pstr><reserved><info_hash><peer_id> 
        
        """
        # HAX: client_address NOTE: new all adresses for testing
        client_address = client_address[haxhax]

        message = pack('>1s19s8s20s20s',Handshake.pstrlen,
                                        Handshake.pstr,
                                        Handshake.reserved, \
                                        self.metadata['info_hash'], 
                                        config['client']['peer_id'].encode())
        
        #print(message)

        # Network setup TCP socket
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.settimeout(config['tcp']['timeout'])

        try:  
            iprint("Connectig to peer:", client_address[0], "::" , client_address[1])

            clientSocket.connect((tuple(client_address)))
            clientSocket.send(message)
            response = clientSocket.recv(config['tcp']['handshake_buffer']) 

            iprint("Connected")

        
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
                # BITFIELD MESSAGE