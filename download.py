

# Used for testing downloading of files from a torrent when conneted to a seeder with 
# 100 % of the data in unchoked state, running linear ATM

import time
import math
import socket

from struct import pack, unpack


# Internals
from src.config import Config
from src.helpers import iprint, eprint, wprint, dprint, timer

# Configuration settings
config = Config().get_config()

from src.read_torrent import TorrentFile


# Used for testing
multitorrent = './test/torrents/multi.torrent'
singeltorrent = './test/torrents/single.torrent'
metadata = TorrentFile(singeltorrent).read()


class Download:
    def __init__(self, metadata) -> None:
        self.metadata = metadata
        self.block_size = 2**14
        self.data = b''

    # NOTE:: just for one socket ATM
    def linear_test(self, peer_socket): # Just for seeding for now
        # Needs to be in the download loop just testing one peer for now
        #try:
        #    peer_socket = socket.fromfd(socket_connection_id, socket.AF_INET, socket.SOCK_STREAM)
        #except Exception as e:
        #    dprint("Connection dead", e)
        #    return
    


        for piece in range(self.metadata['pieces_count']):
            dprint("Trying to download pice:", piece)
            blocks = math.ceil(self.metadata['piece_length'] / 2**14) #
            
            for block in range(blocks):
                dprint("Downloading piece:", piece, "block:", block)
                if piece == self.metadata['pieces_count'] - 1 and blocks == block + 1: # Indexing is a bit messy with 0/1 indexing  
                    dprint("Last piece HAX ")
                    # PI last piece size = (354404132%131072)%2**14 -> 1828
                    # GIMP last piece size = (265283496%262144)%2**14 -> 10152
                    hax = pack('>IBIII', 13, 6, piece, block*self.block_size, 10152) 
                    peer_socket.send(hax)
                else:
                    
                    hax = pack('>IBIII', 13, 6, piece, block*self.block_size, self.block_size)
                    #print(unpack('>IBIII',hax))
                    peer_socket.send(hax)

            # Dumbest shit ever::
            time.sleep(0.5)
            response = peer_socket.recv(24576) # Find a good buffer size
            try:
                msg = unpack('>IBII',response[0:13])
                print(msg)
                print(msg[0])
                print(len(response[13:]))
                self.data = self.data + response[13:] 
                #print(response[17:])
            except Exception as e:
                eprint("Error downloading piece TESTING:", e)

            if hash == self.metadata['pieces'][(piece*20):20 +(piece*20)]:
                iprint("Piece:", piece, "downloaded success" , color="green")



if __name__ == '__main__':
    socket_connection_id = 1568
    test = Download(metadata).linear_test(socket_connection_id)