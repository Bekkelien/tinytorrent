from socket import socket, SOCK_STREAM, AF_INET
from struct import pack, unpack
from dataclasses import dataclass

# Internals
from helpers import iprint, eprint, wprint, dprint, timer
from config import Config

# Configuration settings
config = Config().get_config()


@dataclass
class Handshake: 
    pstrlen = b'\x13'                
    pstr =  b'BitTorrent protocol' 
    reserved = b'\x00' * 8
    #reserved_extensions = b'\x00\x00\x00\x00\x00\x10\x00\x00' https://www.bittorrent.org/beps/bep_0010.html

class PeerWire():
    def __init__(self, info_hash, torrent):
        self.info_hash = info_hash
        self.torrent = torrent

    def handshake(self, client_address): 
        """ 
        'BitTorrent protocol' 1.0
        <len(pstr)><pstr><reserved><info_hash><peer_id> 
        
        """
        # NOTE:
        message = pack('>1s19s8s20s20s',Handshake.pstrlen,Handshake.pstr,Handshake.reserved, \
                                            self.info_hash, config['client']['peer_id'].encode())


        # Network setup TCP socket
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.settimeout(config['tcp']['timeout'])

        try:  
            iprint("Connectig to peer:", client_address[0], "::" , client_address[1])
            # Connect to peer
            clientSocket.connect((tuple(client_address)))

            # Send message to peer 
            clientSocket.send(message)

            # Fetch response from peer
            response = clientSocket.recv(config['tcp']['handshake_buffer']) 
        
        except:
            dprint("Connect to peer failed:", client_address[0], "::" , client_address[1])
            return

        if Handshake.pstrlen + Handshake.pstr == response[0:20] and len(response) >= 68:

            response = unpack('>1s19s8s20s20s', response[0:68])
            response_pstr, response_reserved, response_info_hash = response[1],response[2],response[3]

            dprint("Peer handshake response protocol version:", response_pstr.decode(), ",reserve:", response_reserved.decode(), response_reserved)
            
            # Validate
            if self.info_hash == response_info_hash:
                response_peer_id = response[4]
                iprint("Connected to peer with peer client ID:", response_peer_id, "IMPORTANT -> Add check for response peer ID")

            else:
                wprint("Invalid info has ID response")
        
        else:
            wprint("Peer handshake failed for peer:", client_address[0], "::" , client_address[1])
    

    
  