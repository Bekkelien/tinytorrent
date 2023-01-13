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
    def state_message(self, message, length=1):
        
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
                iprint("Peer response:", Message(response[1])) # BUG: Fail if response is not a int

            else:
                wprint("Peer message failed, unknown prefix/length")

        else:
            eprint("Keep alive message not supported for this client ATM") 
    
    # TODO: Function to handle the peer response -> Currently assuming that we get an unchoke on interested message
    # Merge else statements 

class PeerWire():
    def __init__(self, metadata):
        self.metadata = metadata
        self.peers_connected = [] # NOTE: This is not really a good solution to store in a list, hard to remove invalid peers or update status

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
    def handshake(self, client_address) -> bool: 
        """ 
        'BitTorrent protocol' 1.0
        <len(pstr)><pstr><reserved><info_hash><peer_id> 
        
        """
        # NOTE:
        message = pack('>1s19s8s20s20s',Handshake.pstrlen,Handshake.pstr,Handshake.reserved, \
                                            self.metadata['info_hash'], config['client']['peer_id'].encode())

        # Network setup TCP socket
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.settimeout(config['tcp']['timeout'])

        try:  
            iprint("Connectig to peer:", client_address[0], "::" , client_address[1])
            # Connect to peer
            clientSocket.connect((tuple(client_address)))

            # Send message to peer 
            clientSocket.send(message)

            # Fetch response from peer
            response = clientSocket.recv(config['tcp']['handshake_buffer']) 
            response_length = len(response)
        
        except:
            dprint("Connect to peer failed:", client_address[0], "::" , client_address[1])
            return False
                 
        if Handshake.pstrlen + Handshake.pstr == response[0:20] and len(response) >= 68:

            response = unpack('>1s19s8s20s20s', response[0:68])
            response_pstr, response_reserved, response_info_hash = response[1],response[2],response[3]

            dprint("Peer handshake response | protocol version:", response_pstr.decode("utf-8", "ignore"), \
                                    ",reserve:", response_reserved.decode("utf-8", "ignore"), response_reserved, "response length:", response_length, "bytes")
            
            # Validate
            if self.metadata['info_hash'] == response_info_hash:
                response_peer_id = response[4]
                iprint("Connected to peer with peer client ID:", response_peer_id)
                self._extensions(response_reserved) # NOTE: No handling ATM
                self._peer_client_software(response_peer_id)

                #TESTING NOTE:TESTING NOTE:TESTING NOTE:TESTING NOTE:TESTING NOTE:TESTING NOTE:TESTING NOTE:TESTING NOTE:
                while True:
                    try:
                        response = clientSocket.recv(4096)
                        #  Testing
                        iprint("Response length:",len(response))
                        if len(response) >= 5:
                            message_id = unpack('>b', response[4:5])[0]
                            dprint(message_id)
                            dprint("RESPONSE TEST:", Message(message_id).name)
                            # HAX Testing
                            if Message(message_id).name == Message.bitfield.name:
                                dprint("PAYLOAD Length:", len(BitArray(response[5:]).bin))

                                if len(BitArray(response[5:]).bin) == self.metadata['bitfield_length']:
                                    dprint("Bitfield OK")
                                    #dprint("PAYLOAD:", BitArray(response[5:]).bin)
                                    # Check if full bitfield (Store it? or only store partials?)

                                    # Check if full bitfield (Seeder)
                                    if all(BitArray(response[5:]).bin[0:self.metadata['bitfield_length']-self.metadata['bitfield_spare_bits']]):
                                        peer_status = 'seeder' # 100%¨
                                    else:
                                        # NOTE: Does leachers 'never' send bitfield response after handshake ?
                                        peer_status = 'leecher' # Unknown ATM TODO:
                                    
                                    self.peers_connected.append([client_address[0],client_address[1],peer_status])
                                    
                                    dprint(self.peers_connected)
                                        
                                    # # TODO: Make logic that drops invalid connections

                        else:
                            wprint("HAX ERROR HANDLING")   
                        
                    except Exception as e:
                        eprint(e)
                        break
                
                    # TODO: remove this from class, should be separate 
                    try:
                        # TODO: Reimplement this!
                        one_peer_connected_test = PeerMessage(clientSocket)
                        one_peer_connected_test.state_message(Message.interested)
                        #one_peer_connected_test.have_message(0)
                        #one_peer_connected_test.have_message(1)

                        # Just testing more nesting :)
                        print(self.metadata['pieces'])

                        #for piece in range(self.metadata['pieces']):
                        #    dprint("Trying to download piece:", piece)
                        #    for block in range(math.ceil(self.metadata['piece_length'] / 16384)): # Make sure this is a integer
                        #        dprint("Downloading block:", block, "from piece:", piece)
                        #        hax = pack('>IBIII', 13, 6, piece, 0 + (block*16384), 16384)
                        #        clientSocket.send(hax)
                        #
                        #        response = clientSocket.recv(24576) 
                        #        print(len(response))
                        #        print(response)
                        #        break
                        #    break
                        
                    except:
                        print("THIS IS A BAD IDEA")


                return True # BUG: We are assuming that that the peer is unchoked here but that is optimistic 

            else:
                wprint("Invalid Peer ID response")
        
        else:
            wprint("Peer handshake failed for peer:", client_address[0], "::" , client_address[1])

        # Unless ok Validation, handshake has failed 

        return False



        

            

