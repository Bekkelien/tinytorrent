import json
import socket
import math
from enum import Enum
from struct import pack, unpack
from dataclasses import dataclass
from bitstring import BitArray
#from functools import lru_cache
import asyncio
# Internals
from src.config import Config
from src.helpers import iprint, eprint, wprint, dprint, timer

# Configuration settings
config = Config().get_config()


@dataclass
class Clients:
    clients = json.load(open('./src/clients.json'))

class Messages():
    def __init__(self):
        pass

    def interested(self):
        pass


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
        self.peers_metadata = []

    # Here or outside function?
    @staticmethod
    def client_software(client_id) -> None:
        client_id = client_id[1:3].decode("utf-8", "ignore") 

        if Clients.clients.get(client_id) == None:
            wprint("Unknown client software for peer id:", client_id, "TODO: Implement some verification here?")
        else:
            iprint("Peer client:", Clients.clients[client_id])

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
            response = None

            try:
                reader, writer = await asyncio.wait_for(asyncio.open_connection(*peer_ip), timeout=config['tcp']['timeout'])
                writer.write(message) # Response from server
                response = await asyncio.wait_for(reader.read(config['tcp']['handshake_buffer']), timeout=config['tcp']['timeout'])
            
            except asyncio.TimeoutError:
                wprint("Connection to peer timed out")

            except Exception as ConnectionError:
                wprint("Connection to peer:", ConnectionError)

            # Validate handshake
            if response:
                if self.validate(response):

                    # Look for bitfield
                    try: 
                        response = await asyncio.wait_for(reader.read(config['tcp']['handshake_buffer']), timeout=config['tcp']['timeout'])
                        return response  

                    except Exception:
                        wprint("Bitfield not received")

            return b''

    async def connect(self, peer_ip, message):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(config['tcp']['timeout'])

        # Handshake message
        response = await self.message(peer_ip, message)

        # Bitfield message
        pieces = self.validate_bitfield(response)

        # TODO: NOTE: Currently only storing peers that respond with a valid bitfield of pieces
        if pieces: self.peers_metadata.append([peer_ip,pieces])


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


if __name__ == '__main__':
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