# TESTING 

import time
import math
import socket

import hashlib

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

    # NOTE:: just for one socket ATM
    def linear_test(self, current_peer): # Just for seeding for now
        # INDEXING DOES NOT MAKE ANY SENS
        piece_current =  self.metadata['pieces_downloaded'].count('1')
        piece_left = self.metadata['pieces_downloaded'].count('0')
        dprint("Piece left:", self.metadata['pieces_downloaded'])
        iprint("Trying to downloaded pieces:", piece_current, "pieces left:", piece_left) # HAX
        
        blocks = math.ceil(self.metadata['piece_length'] / self.block_size) 
        
        # Overwrite expression for last pice
        if piece_left == 1:
            blocks = math.ceil((self.metadata['size']-self.metadata['piece_length']*piece_current) / self.block_size) 
        
        iprint("Blocks in current piece:", blocks)

        for _ in range(piece_left): # Indexing needs to be better overall TODO:::TODO
            factor = 1
            block_data = b''
            flag = False
            for block in range(blocks):
                # pice index stuff is bad as always 
                if piece_left == 1 and blocks == block + 1: # Indexing is a bit messy with 0/1 indexing  # TODO IMPROVE THIS
                    dprint("Last piece HAX, piece number:", piece_current)
                  
                    last_block_size =(self.metadata['size']%self.metadata['piece_length'])%self.block_size #Make block size "global"
                    dprint("Last piece size test:", last_block_size)

                    hax = pack('>IBIII', 13, 6, piece_current, block*self.block_size, last_block_size) 
                else:
                    hax = pack('>IBIII', 13, 6, piece_current, block*self.block_size, self.block_size)
                    #print(unpack('>IBIII',hax))
                
                try:
                    current_peer.send(hax)
                    # ADD Handler within each piece 
                    # Dumbest shit ever:: just wait to response is hit
                    time.sleep(factor) # NOTE:HAX
                    response = current_peer.recv(24576) # Find a good buffer size
                    #print(response)
                    msg = unpack('>IBII',response[0:13])
                    print(msg)
                    print(msg[0])
                    print(len(response[13:]))
                    block_data = block_data + response[13:] 
                    #print(response[17:])
                except Exception as e:
                    eprint("Error downloading piece TESTING:", e)
                
            hash = hashlib.sha1(block_data).digest()
            dprint("Hash of piece:", hash)
            dprint("Expected hash of piece:", self.metadata['pieces'][(piece_current*20):20 +(piece_current*20)])

            if hash == self.metadata['pieces'][(piece_current*20):20 +(piece_current*20)]: # Make this easier to index?
                iprint("Piece:", piece_current, "downloaded success" , color="green")
                

                if factor > 0.2: factor = factor - 0.1

                # NOTE: this was a bad idea since strings in python are immutable but lets go with it for now
                self.metadata['pieces_downloaded'] = self.metadata['pieces_downloaded'][:piece_current] + '1' + self.metadata['pieces_downloaded'][piece_current + 1:]
                
                if piece_current == self.metadata['pieces_count'] -1:  # Make index system better
                    flag = True

                print(len(block_data), flag)
                return block_data, flag
            
            else: 
                wprint("Piece:", piece_current, "download did not match the hash")
                block_data = b''
                print(len(block_data), flag)
                return block_data, flag           


if __name__ == '__main__':
    pass