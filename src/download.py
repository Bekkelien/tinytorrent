import time
import math
import hashlib

from struct import pack, unpack

# Internals
from src.config import Config
from src.read_torrent import TorrentFile, MetadataStorage
from src.helpers import iprint, eprint, wprint, dprint
from src.protocol import MessageType, PeerMessage

# Configuration settings
config = Config().get_config()

FACTOR = 0.01
BLOCK_SIZE = 2**14

# NOTE: Current index and rest pieces are a bit messy 
class Download:
    def __init__(self, client_socket) -> None:
        self.metadata = MetadataStorage().metadata
        self.client_socket = client_socket
        self.index = self.metadata['pieces_downloaded'].count('1')
        self.remaining_pieces = self.metadata['pieces_downloaded'].count('0')
        self.block_size_last =  (self.metadata['size'] % self.metadata['piece_length']) % BLOCK_SIZE 

    def _linear_piece_manager(self) -> int:
        self.index  = self.metadata['pieces_downloaded'].count('1')
        self.remaining_pieces = self.metadata['pieces_downloaded'].count('0')
        
        blocks = math.ceil(self.metadata['piece_length'] / BLOCK_SIZE) 
        
        # Overwrite expression for last pice
        if self.remaining_pieces == 1:
            blocks = math.ceil((self.metadata['size']-self.metadata['piece_length']*self.index ) / BLOCK_SIZE) 
        
        iprint("Trying to downloaded pieces:", self.index , "blocks:", blocks, "remaining pieces:", self.remaining_pieces) # HAX
        return blocks


    def _piece_validation(self, piece_data) -> bytes:
        dprint("Piece validation data length TEST:", len(piece_data))
        piece_hash = hashlib.sha1(piece_data).digest()

        if piece_hash == self.metadata['pieces'][(self.index*20):20 +(self.index*20)]: # Make this easier to index?
            iprint("Piece:", self.index, "hash is verified" , color="green")

            # TODO: Update metadata Downloaded well that is hard without storing it to file (NOTE: make metadata a file?), left also download speed for this piece here

            # NOTE: this was a bad idea since strings in python are immutable but lets go with it for now
            self.metadata['pieces_downloaded'] = self.metadata['pieces_downloaded'][:self.index] + '1' + self.metadata['pieces_downloaded'][self.index + 1:]

            return piece_data
    
        else: 
            wprint("Piece:", self.index, "hash verification failed")
            return  b''        

    def _piece_last_check(self) -> bool:
        if self.index == self.metadata['pieces_count'] - 1:  
            return True
    
        return False

    # TODO PRE SEND AND READ SOCKET FOR EACH CONN AND PEER AND MESSAGE TYPE
    def linear_download_piece(self): # Bytes,bool how to do two return stuff thing
        # piece:    <len=0009+X><id=7><index><begin><block>
        # request:  <len=0013><id=6><index><begin><length>
        blocks = self._linear_piece_manager() # Piece to download
        flag = None
        piece_data = b''
        #piece_time_start = time.time()
        for block in range(blocks):
            #dprint("BLOCK:", block)
            #time_block_start = time.time()
            if self.remaining_pieces == 1 and blocks == block + 1:
                print("Trying to download the last block:", blocks, "in piece:", self.index, "with a size of:", self.block_size_last)
                hax_current_block_size = self.block_size_last
            else:
                hax_current_block_size = BLOCK_SIZE
            
            #print(self.index, block*BLOCK_SIZE, hax_current_block_size)
            PeerMessage(self.client_socket).send_request(self.index, block*BLOCK_SIZE, hax_current_block_size) # TODO: MAKE PAYLOAD Stuff more intuitive 

        time.sleep(0.3)
        for block in range(blocks):
        # BUG THIS IS JUST BAD IN EVERY WAY and does not work:)
            piece = True
            hax = 1
            block_data = b''
            
            while piece:
                time.sleep(0.05)
                # This is messy 
                peer = PeerMessage(self.client_socket)
                peer.receive()
                message_type = peer.last_message  
                if message_type == MessageType.piece.name:
                    iprint("Peer did send a piece message")
                    block_data = block_data + peer.receive_block(hax_current_block_size)
                    piece = False
                
                else:
                    eprint("MESSAGE:", message_type)
                    hax += 1
                    if hax == 10:
                        return b'', False 
                #if (time.time() - time_block_start)  >= 0.5: # 500ms
                #    print("Peer does not respond with a piece message")
                #    return b'', False
            piece_data = piece_data + block_data

        # We are faster but still slow as
        # TESTING TO COMPUTE THE DOWNLOAD SPEEEEEEEEEEEEEEEEEEEED :)
        #piece_time_end = time.time()
        #if piece_time_end - piece_time_start != 0: # BUG
        #    iprint("Download rate for piece:", self.index, "->" , ((blocks * BLOCK_SIZE) / (piece_time_end - piece_time_start))/(1024*1024), "MB/s")

        piece_data = self._piece_validation(piece_data)

        # BUG DOES NOT WORK OR DOES IT?!!!
        #if piece_data: # Making sure we have valid piece data before flagging last piece # TODO: Messy 
        flag = self._piece_last_check()

        return piece_data, flag 


if __name__ == '__main__':
    # Used for testing
    multitorrent = './test/torrents/multi.torrent'
    singeltorrent = './test/torrents/single.torrent'
    metadata = TorrentFile(singeltorrent).read()
