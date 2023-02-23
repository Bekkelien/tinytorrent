import json
import socket
import asyncio

from enum import Enum
from struct import pack, unpack
from dataclasses import dataclass
from bitstring import BitArray

# Internals
from src.config import Config
from src.helpers import iprint, eprint, wprint, dprint, timer

# Configuration settings
config = Config().get_config()

@dataclass
class Clients:
    clients = json.load(open('./src/clients.json'))


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

class PeerMessage():
    def __init__(self):
        pass
    
    # TODO: Rename function 
    async def state_message(self, reader, writer, message, length=1) -> str:

        # BUG: HAX for now
        response = []

        # NOTE: Currently assuming we are choked if we don't get a state message back from the peer
        if message.value >= 0:

            iprint("Sending an:", message, "message to peer")
            message = pack('>Ib', length, message.value)

            # TODO: This is used many places should be a class or generic function ?? and de dont have reader writer stored HOW TODO::

            try:
                writer.write(message)
                response = await asyncio.wait_for(reader.read(config['tcp']['state_message_buffer']), timeout=config['tcp']['timeout'])
            
            except asyncio.TimeoutError:
                wprint("Connection to peer timed out")

            except Exception as ConnectionError:
                wprint("Connection to peer:", ConnectionError)

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

class Handshake: 
    def __init__(self, metadata):
        """ Handshake: <pstrlen><pstr><reserved><info_hash><peer_id> """

        self.metadata = metadata

        self.pstrlen = b'\x13'                
        self.pstr =  b'BitTorrent protocol' 
        self.reserved = b'\x00\x00\x00\x00\x00\x00\x00\x00'
        # metadata['info_hash']
        self.peer_id = config['client']['peer_id'].encode()

        # Bad place?
        self.peers_metadata = [] # Make a dictionary?
        self.connections = {}

    # Here or outside function?
    @staticmethod
    def client_software(client_id) -> None:
        client_id = client_id[1:3].decode("utf-8", "ignore") 

        if Clients.clients.get(client_id) == None:
            wprint("Unknown client software for peer id:", client_id, "TODO: Implement some verification here?")
        else:
            iprint("Peer client:", Clients.clients[client_id])

    async def close_connection(self, ip, writer):
        self.connections.pop(ip)
        writer.close()
        await writer.wait_closed()

    def validate(self, response) -> bool:

        if len(response) < 68:
            wprint("Handshake response too short")
            return False
    
        elif len(response) >= 68:
            response = unpack('>1s19s8s20s20s', response[0:68])

            # Parse handshake response (Bytes) b'data'
            pstrlen = response[0]
            pstr = response[1]
            reserved = response[2]            
            info_hash = response[3]
            client_id = response[4]
            
            if (self.pstrlen + self.pstr) != pstrlen + pstr:
                wprint("Handshake response failed unknown protocol:", pstr.decode("utf-8", "ignore"))
                return False

            # Validate
            if self.metadata['info_hash'] == info_hash:
                iprint("Handshake accepted, info hash match")
                self.client_software(client_id)
                return True
            
            return False

    async def bitfield(self, peer_ip, response) -> bytes:
        # Validate handshake
        if response:
            if self.validate(response):
                
                reader, writer = self.connections[peer_ip[0]]
                # Look for bitfield
                try: 
                    response = await asyncio.wait_for(reader.read(config['tcp']['handshake_buffer']), timeout=config['tcp']['timeout'])
                    
                    return response  
                except Exception:
                    wprint("Bitfield not received")
        
        return b''
            
    def validate_bitfield(self, response) -> list:

        if len(response) < 5:
            return []
        
        bitfield_payload = response[5:]
        bitfield_payload_big_endian = BitArray(bitfield_payload).bin

        # Check bitfield length
        if len(BitArray(bitfield_payload).bin) == metadata['bitfield_length']:
            # Check if spare bitfield are zero
            if bitfield_payload_big_endian[-self.metadata['bitfield_spare']:].count('0') == self.metadata['bitfield_spare']:
                
                iprint("Bitfield accepted")
                return bitfield_payload_big_endian
            
            else:
                wprint("Spare bitfield bytes not: 0")

        return []
        

    async def message(self, peer_ip, message) -> bytes:
            response = b''

            try:
                reader, writer = await asyncio.wait_for(asyncio.open_connection(*peer_ip), timeout=config['tcp']['timeout'])

                writer.write(message) # Response from server
                response = await asyncio.wait_for(reader.read(config['tcp']['handshake_buffer']), timeout=config['tcp']['timeout'])
                
                # VALID CHECKS?
                # Store all connections 
                self.connections[peer_ip[0]] = (reader, writer) 
            
            except asyncio.TimeoutError:
                wprint("Connection to peer timed out")

            except Exception as ConnectionError:
                wprint("Connection to peer:", ConnectionError)

            return response

    async def connect(self, peer_ip, message):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(config['tcp']['timeout'])

        # Handshake message
        response = await self.message(peer_ip, message)

        # Bitfield message
        response = await self.bitfield(peer_ip, response)
        pieces = self.validate_bitfield(response)

        # Filtering of connections are not good

        # NOTE:: Tis is a mess to have connections outside the class in other class!
        if pieces:
            reader, writer = self.connections[peer_ip[0]] # HAX
            message_state = await PeerMessage().state_message(reader, writer, Message.interested) # HAX
            self.peers_metadata.append([peer_ip, Message(message_state).name, pieces])

        # Does not close all connections so just leaving open for now
        #else: 
        #    if peer_ip[0] in self.connections:
        #        reader, writer = self.connections[peer_ip[0]] # HAX
        #        await self.close_connection(peer_ip[0], writer)

        
        # TODO: NOTE: Currently only storing peers that respond with a valid bitfield of pieces



    async def manager(self, peer_ips):
        iprint("Sending handshake to peers:", len(peer_ips))
        
        message = pack('>1s19s8s20s20s', 
                        self.pstrlen,
                        self.pstr,
                        self.reserved,
                        self.metadata['info_hash'],
                        self.peer_id)
        tasks = []
        for peer_ip in peer_ips:
            tasks.append(asyncio.create_task(self.connect(peer_ip, message)))

        await asyncio.gather(*tasks)

    async def run(self, peer_ips):
        await self.manager(peer_ips)
        print(self.peers_metadata)
        #print(self.connections)
        #print(len(self.connections))

if __name__ == '__main__':

    ##
    # async def close_connection(self, peer_ip):
     #   reader, writer = self.connections.pop(peer_ip)
     #   writer.close()
    #    await writer.wait_closed()

    # TESTING
    from src.manager import TrackerManager
    from src.read_torrent import TorrentFile
    from pathlib import Path

    PATH = Path('./src/files/')
    file = 'gimp.torrent'
    #file = 'pi.torrent'

    metadata = TorrentFile(PATH / file).read()
    tracker = TrackerManager(metadata)
    peer_ips = tracker.get_clients()

    asyncio.run(Handshake(metadata).run(peer_ips))