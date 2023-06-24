import json
import socket
import math
import time

from typing import List, Tuple
from enum import Enum
from struct import pack, unpack
from dataclasses import dataclass
from bitstring import BitArray
from collections import Counter
#from functools import lru_cache

# Internals
from src.config import Config
from src.helpers import iprint, eprint, wprint, dprint, timer, pprint

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

    response_length = 68
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
    
    # TODO: Rename function (NOTE: cleaner to make a function for each message then making a complex generic one)
    def state_message(self, message, length=1) -> str:
        # NOTE: Currently assuming we are choked if we don't get a state message back from the peer
        if message.value >= 0:
            iprint("Sending an:", message, "message to peer")

            # Send message to peer 
            message = pack('>Ib', length, message.value)
            # Response from peer TODO:
            try:
                self.clientSocket.send(message)
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


# NOTE: Metadata should be stored to a file to avoid passing to every func 

class Bitfield: 
    def __init__(self, client_socket: socket.socket, metadata: dict) -> None:
        self.metadata: dict = metadata
        self.peer_status: str = 'leecher'
        self.client_socket: socket.socket = client_socket
        self.bitfield_payload: str = ''
        self.peer_data_percentage: int = -1 # -1 = N/A, 0 - 100 = 0-100%

    def _receive(self) -> None:
        """ bitfield: <len=0001+X><id=5><bitfield> """

        try:
            response = self.client_socket.recv(4096) # TODO: compute the buffer length in the future 
            bitfield_id  = unpack('>b', response[4:5])[0]

        except Exception as e: # TODO::
            dprint("Peer did not send a bitfield message:", e)
            return

        if bitfield_id  == Message.bitfield.value: # Check what we have correct bitfield id=5
            if len(self.metadata['bitfield']) == len(str(BitArray(response[5:]).bin)): # Using data instead of first 4 bytes of response here 
                iprint("Valid bitfield received from peer")
                self.bitfield_payload = str(BitArray(response[5:]).bin)

        dprint("Invalid bitfield response from peer")

    def _determine_peer_status(self) -> None:
        dprint("Bitfield payload from peer:", self.bitfield_payload)
        
        if self.bitfield_payload:
            if self.metadata['bitfield'] == self.bitfield_payload:
                self.peer_status = 'seeder' # Peer has 100% of data 
                self.peer_data_percentage = 100

            else:
                self.peer_data_percentage = int(Counter(self.metadata['bitfield'])['1'] - Counter(self.bitfield_payload)['1'])

        dprint("Peer has:", self.peer_data_percentage, "% of data")
    # TODO :: Add in piece to keep track

    def consume(self) -> str:
        self._receive()
        self._determine_peer_status()

        return self.peer_status, self.peer_data_percentage


class PeerWire():
    def __init__(self, metadata, peer_addresses):
        self.metadata = metadata
        self.peer_addresses = peer_addresses


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
    def _handshake(self, peer_address: Tuple) -> list: # TODO Separate this code further 
        """ 
        'BitTorrent protocol' 1.0

        Handshake:
        <len(pstr)><pstr><reserved><info_hash><peer_id> 
        """
        peer = []


        message = pack('>1s19s8s20s20s',Handshake.pstrlen,
                                        Handshake.pstr,
                                        Handshake.reserved, \
                                        self.metadata['info_hash'], 
                                        config['client']['peer_id'].encode())

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.settimeout(config['tcp']['timeout'])

        try:  
            iprint("Establishing connection to peer:", peer_address)

            self.client_socket.connect((peer_address))
            self.client_socket.send(message)
            response = self.client_socket.recv(config['tcp']['handshake_buffer']) 

            iprint("Connected to peer:", peer_address)

        except Exception as e: # TODO Improve this
            dprint("Connect to peer failed with exception:", e)
            return peer
        
        if len(response) >= Handshake.response_length:
            response = unpack('>1s19s8s20s20s', response[0:Handshake.response_length])
            
            pstrlen, pstr, reserved, info_hash, client_id = response[0:5]

            if (Handshake.pstrlen + Handshake.pstr) != pstrlen + pstr:
                wprint("Handshake response failed unknown protocol:", pstr.decode("utf-8", "ignore"))
                return peer

            # Validate
            if self.metadata['info_hash'] == info_hash:
                iprint("Handshake accepted")
                self._extensions(reserved) # NOTE: No handling ATM
                self._peer_client_software(client_id) # NOTE: No handling ATM

                # Check for bitfield response
                peer_status, peer_data_percentage = Bitfield(self.client_socket, self.metadata).consume()

                # Send interested message to try to unchoke the peer
                message_state = PeerMessage(self.client_socket).state_message(Message.interested) # TODO Fix function allot 
                iprint("Peer responded with:", Message(message_state).name)

                peer = [self.client_socket, peer_status, peer_data_percentage, Message(message_state).name]
                # TODO :: List datatype is probably a bad idea here since we need to keep track of indexes ?
                #dprint(peer)
                #eprint(peer[0].getpeername())
                return peer

        elif len(response) < Handshake.response_length:
            wprint("Handshake response length invalid")
        
        return peer
                
                # TODO: Make a system to keep track of peers and their status
                # NOTE: Client sockets are not closed? 
                # TODO: Make async 
                # STOP FUNCTION HERE



    def _rank_peers(self, peer_address_connected): 
        peer_address_connected = sorted(peer_address_connected, key=lambda x: (x[3] == 'unchoke', x[2]))[::-1]
        return peer_address_connected

    def connect(self): # Make peer limit to config TODO: 
        
        peer_address_connected=[]
        for peer_address in self.peer_addresses:
            peer = self._handshake(peer_address)

            if peer: peer_address_connected.append(peer)
            else: self.client_socket.close()

            # TESTING::: START
            pprint(self._rank_peers(peer_address_connected)) # debugging 
            # TESTING::: END

            # HAX
            MAX_PEER_CONNECTED = 25
            if len(peer_address_connected) >= MAX_PEER_CONNECTED:
                return peer_address_connected
            
            # TODO: Remove "bad" peers 

        peer_address_connected = self._rank_peers(peer_address_connected)
        pprint(peer_address_connected)
        return peer_address_connected
    
