
import socket

import asyncio
import socket
from struct import pack, unpack
from src.old.protocol import Handshake
from bitstring import BitArray
from src.config import Config

# Configuration settings
config = Config().get_config()

peer_ip_handshake_ok = []

def handshake_validate(response, info_hash=b'\x86"kA\x98Z$Z\xc0\xc9\xa8\x94n\x1emfC\xffd\xf3')-> bool:
    if 49 <= len(response) <= 67:
        print("Handshake response of type: compact peer formate is not supported")
    
    elif len(response) >= 68:
        response = unpack('>1s19s8s20s20s', response[0:68])

        # Parse handshake response (Bytes) b'data'
        handshake_pstrlen = response[0]
        handshake_pstr = response[1]
        handshake_reserved = response[2] # TODO            
        handshake_info_hash = response[3]
        handshake_client_id = response[4] # TODO
        
        if (Handshake.pstrlen + Handshake.pstr) != handshake_pstrlen + handshake_pstr:
            print("Handshake response failed unknown protocol:", handshake_pstr.decode("utf-8", "ignore"))
            return False


        # Validate
        if info_hash == handshake_info_hash:
            print("Handshake accepted")
            return True


async def handshake_tasks(peer_ips, metadata, peer_id) -> None:

    print("Sending handshake to peers:", len(peer_ips))

    message = pack('>1s19s8s20s20s', Handshake.pstrlen,
                                        Handshake.pstr,
                                        Handshake.reserved,
                                        metadata['info_hash'],
                                        peer_id.encode())

    tasks = []
    for peer_ip in peer_ips:
        tasks.append(asyncio.create_task(handshake_send_recv(peer_ip, message)))

    await asyncio.gather(*tasks)


async def handshake_send_recv(peer_ip, message) -> bytes:

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(config['tcp']['timeout'])

    #print("Connecting to peer:", peer_ip[0], "::" , peer_ip[1])

    try:

        reader, writer = await asyncio.wait_for(asyncio.open_connection(*peer_ip), timeout=config['tcp']['timeout'])
        writer.write(message) # Response from server
        response_handshake = await asyncio.wait_for(reader.read(config['tcp']['handshake_buffer']), timeout=config['tcp']['timeout'])
        print(response_handshake)


         #A bit messy to have 2 recv in one function
        try:
            writer.write(message) # Response from server
            response_bitfield = await asyncio.wait_for(reader.read(config['tcp']['handshake_buffer']), timeout=config['tcp']['timeout'])
            bitfield_id = unpack('>b', response_bitfield[4:5])[0]

        except:
            bitfield_id = None

        # TODO CLEANUP THIS
        if handshake_validate(response_handshake):

            if bitfield_id == 5:
                bitfield_payload = response_bitfield[5:]

                # Test if this is working
                if len(BitArray(bitfield_payload).bin) == metadata['bitfield_length']:
                    if BitArray(bitfield_payload).bin.count('1') == metadata['pieces']:
                        print('seeder') # Peer has 100% of data 
                    else:
                        print('leecher') # Peer has x% of data 

        peer_ip_handshake_ok.append(peer_ip)


    except asyncio.TimeoutError:
        print("Connection to peer timed out")

    except Exception as ConnectionError:
        print("Connection to peer failed", ConnectionError)

async def run_handshakes(peer_ips, metadata):
    await handshake_tasks(peer_ips, metadata, peer_id="-TI2080-MH5k6JGjhlNb")


# TESTING
from src.manager import TrackerManager
from src.read_torrent import TorrentFile
from pathlib import Path

PATH = Path('./src/files/')
#file = 'gimp.torrent'
file = 'pi.torrent'

metadata = TorrentFile(PATH / file).read()
tracker = TrackerManager(metadata)
peer_ips = tracker.get_clients()


asyncio.run(run_handshakes(peer_ips,metadata))
print(peer_ip_handshake_ok)

