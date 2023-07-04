import json
import socket
import math
import time

from enum import Enum
from typing import List, Tuple, Optional 
from struct import pack, unpack
from dataclasses import dataclass
from bitstring import BitArray
from collections import Counter

#from functools import lru_cache # NOTE: Caching

# Internals
from src.config import Config
# from src.networking import PeerCommunication TODO:
from src.helpers import iprint, eprint, wprint, dprint, timer, pprint
from src.clients import Client

# Configuration settings
config = Config().get_config()

class MessageType(Enum): # NOT sure i like Enums or am I using them wrong?
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


# Use this more places TODO:: client sockets are store in to many classes for same peer
class PeerCommunication():
    def __init__(self, client_socket: socket.socket):
        self.client_socket = client_socket
        self.ip = client_socket.getpeername()[0]
        self.port = client_socket.getpeername()[1]

    def receive_header(self, buffer_size=5) -> str:
        message_type = "Unknown"
        # "Send keep alive is not implemented"
        try:
            data = self.client_socket.recv(buffer_size)
            message_type = int.from_bytes(data[4:5], byteorder='big')
        except:
            wprint("Failed to receive or/no message from peer:", self.ip)
       
        if message_type in [i.value for i in MessageType]: #TODO 
            return MessageType(message_type).name
        
        return message_type
    
    def receive_data(self, buffer_size) -> bytes:
        data = b''
        try:
            data = self.client_socket.recv(buffer_size)

        except:
            wprint("Could not receive data from peer:", self.ip)
        return data

    def send(self, data) -> None:
        if len(data) >= 5:
            message_type = int.from_bytes(data[4:5], byteorder='big') # UNPACK INSTEAD
        else:
            wprint("Send keep alive is not implemented")
        if message_type in [i.value for i in MessageType]: #TODO 
            try:
                self.client_socket.send(data)
            except Exception as e:
                eprint("Failed to send:", MessageType(message_type).name, "to peer:", self.ip ,"Error:", e)

        else:
            eprint(self.__class__.__name__, "| cant send message to peer:", self.ip, "Unknown message")


class PeerMessage():
    def __init__(self, clientSocket, metadata):
        self.metadata = metadata
        self.client_socket = clientSocket
        self.last_message = None # NAH hax
    
        # keep alive:       <len=0000> 
        # --------- Peer Communication Status
        # choke:            <len=0001>   <id=0>
        # unchoke:          <len=0001>   <id=1>
        # interested:       <len=0001>   <id=2>
        # not interested:   <len=0001>   <id=3>
        # ---------
        # TODO # have:      <len=0005>   <id=4> <piece index>
        # TODO # bitfield:  <len=0001+X> <id=5> <bitfield>
        # request:          <len=0013>   <id=6> <piece index>         <begin>   <length>
        # TODO# piece:      <len=0009+X> <id=7> <piece index>         <begin>   <block>
        # TODO# cancel:     <len=0013>   <id=8> <piece index>         <begin>   <length>
        # TODO# port:       <len=0003>   <id=9> <listen-port>


    def send_keepalive(self):
        data = pack('>i', 0)
        PeerCommunication(self.client_socket).send(data)
        
    def send_choke(self) -> None: 
        data = pack('>ib', 1, MessageType.choke.value)
        PeerCommunication(self.client_socket).send(data)

    def send_unchoke(self) -> None: 
        data = pack('>ib', 1, MessageType.unchoke.value)
        PeerCommunication(self.client_socket).send(data)

    def send_interested(self) -> None: 
        data = pack('>ib', 1, MessageType.interested.value)
        PeerCommunication(self.client_socket).send(data)

    def send_notinterested(self) -> None: 
        data = pack('>ib', 1, MessageType.notinterested.value)
        PeerCommunication(self.client_socket).send(data)

    def send_request(self, piece_index: int, begin: int, length: int) -> None:
        data = pack('>ibiii', 13, MessageType.request.value, piece_index, begin, length)
        PeerCommunication(self.client_socket).send(data)

    # TODO Make a receive of incoming messages and handle clients/peers better rename
    # TODO :: HMM
    # BUG :: Does not work as we need to know when an incoming message are on the way
    # For now it just do yolo, so reading memory random data from memory if no message? 
    # Make this an generic receive:
    def receive(self) -> Optional[bytes]: # This is kinda dups HAX: TODO: Metadata improvements needed
        peer = PeerCommunication(self.client_socket)
        time.sleep(1)
        self.last_message = peer.receive_header() 
        eprint(self.last_message)
        if not self.last_message:
            return None 

        if self.last_message == MessageType.bitfield.name:
            iprint("Received bitfield message from peer:", peer.ip)
            data = peer.receive_data(int(self.metadata['bitfield_length'] / 8))
            dprint("Bitfield message from peer:", peer.ip, "bitfield:", data)
            return data


    def receive_block(self, block_size: int) -> bytes:
        block_data = b''
        remaining_payload = block_size + 13 - 5 # Bad solution
        hax = PeerCommunication(self.client_socket)

        try:
            while remaining_payload > 0: # BUG: Can this become infinite?
                time.sleep(0.001) # TODO .: Remove
                dprint("Remaining block payload:", remaining_payload)
                block_data = block_data + hax.receive_data(remaining_payload)
                remaining_payload -= len(block_data)
        
        except Exception as e:
            eprint("Reading message payload failed:", e)
        print(unpack('>ii', block_data[:8]))
        return block_data[8:] # Hardcoded

# NOTE: Metadata should be stored to a file to avoid passing to every func 
# TODO use peer messages here we are a bit messy now to much here and there
# Class for socket so we can inherent socket for all function that need a socket 
class Bitfield: 
    def __init__(self, client_socket: socket.socket, metadata: dict) -> None:
        self.metadata: dict = metadata
        self.peer_status: str = 'leecher'
        self.client_socket: socket.socket = client_socket
        self.bitfield_payload: str = ''
        self.peer_data_percentage: int = -1 # -1 = N/A, 0 - 100 = 0-100%

    # TODO:: should be in receive now and in future we should handle all incoming msg.
    def _receive(self) -> None:

        data = PeerMessage(self.client_socket, self.metadata).receive() # Should be unnecessary to pass client_socket everywhere 
 
        if len(self.metadata['bitfield']) == len(str(BitArray(data).bin)): # Using data instead of first 4 bytes of response here 
            iprint("Valid bitfield received from peer")
            self.bitfield_payload = str(BitArray(data).bin)
            return

    def _determine_peer_status(self) -> None:
        if self.bitfield_payload:
            if self.metadata['bitfield'] == self.bitfield_payload:
                self.peer_status = 'seeder' # Peer has 100% of data 
                self.peer_data_percentage = 100

            else:
                self.peer_data_percentage = int(Counter(self.metadata['bitfield'])['1'] - Counter(self.bitfield_payload)['1'])

        #dprint("Peer has:", self.peer_data_percentage, "% of data")
    # TODO :: Add in piece to keep track

    def consume(self) -> str:
        self._receive()
        self._determine_peer_status()

        return self.peer_status, self.peer_data_percentage


class PeerWire():
    def __init__(self, metadata, peer_addresses):
        self.metadata = metadata
        self.peer_addresses = peer_addresses

    @timer
    def _handshake(self, peer_address: Tuple) -> list: # TODO Separate this code further 
        """ 
        'BitTorrent protocol' 1.0
        Handshake: <len(pstr)><pstr><reserved><info_hash><peer_id> 
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
            
            pstrlen, pstr, reserved, info_hash, peer_identifier = response[0:5]

            if (Handshake.pstrlen + Handshake.pstr) != pstrlen + pstr:
                wprint("Handshake response failed unknown protocol:", pstr.decode("utf-8", "ignore"))
                return peer

            # Validate  # NOTE :: Messy
            if self.metadata['info_hash'] == info_hash:
                iprint("Handshake accepted")
                # TODO: Dup calls, how to remove these and keep clean syntax
                Client().extensions(reserved)
                client_name = Client().software(peer_identifier)

                peer_status, peer_data_percentage = Bitfield(self.client_socket, self.metadata).consume() # Calling Bitfield consume can be other messages as we just parse the first one

                # Send interested message to try to unchoke the peer TODO: messy to use and create a million objects
                PeerMessage(self.client_socket, self.metadata).send_interested() 
                iprint("Peer responded with:", peer_status)

                peer = [self.client_socket, peer_status, peer_data_percentage, "NotImplemented", client_name]
                return peer

        elif len(response) < Handshake.response_length:
            wprint("Handshake response length invalid")
        
        return peer
                
                # TODO: Make a system to keep track of peers and their status
                # NOTE: Client sockets are not closed? 
                # TODO: Make async 
                # STOP FUNCTION HERE


    def _rank_peers(self, connected_peers: list) -> list:
        connected_peers = sorted(connected_peers, key=lambda x: (x[3] == 'unchoke', x[2]))[::-1]
        return connected_peers

    def connect(self) -> list:
        connected_peers=[]
        for peer_address in self.peer_addresses:
            if config['peer']['max_connected'] <= len(connected_peers): 
                break
            
            peer = self._handshake(peer_address)
            
            if peer: 
                connected_peers.append(peer)
                iprint("Connected to:", len(connected_peers), "peers")
            else: 
                self.client_socket.close()

        connected_peers = self._rank_peers(connected_peers)
        pprint(connected_peers)
        return connected_peers
    
