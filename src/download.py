import time
import math
import hashlib

from struct import pack, unpack

# Internals
from src.config import Config
from src.read_torrent import TorrentFile
from src.helpers import iprint, eprint, wprint, dprint
from src.protocol import Message

# Configuration settings
config = Config().get_config()

FACTOR = 0.01
BLOCK_SIZE = 2**14

# NOTE: Current index and rest pieces are a bit messy 
class Download:
    def __init__(self, metadata) -> None:
        self.metadata = metadata
        self.index = self.metadata['pieces_downloaded'].count('1')
        self.remaining_pieces = self.metadata['pieces_downloaded'].count('0')
        self.block_size_last =  (metadata['size']%metadata['piece_length']) % BLOCK_SIZE 

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

    def _piece_last_check(self):
        if self.index == self.metadata['pieces_count'] - 1:  
            return True
    
        return False


    def linear_download_piece(self, client_socket): # Bytes,bool how to do two return stuff thing
        # piece:    <len=0009+X><id=7><index><begin><block>
        # request:  <len=0013><id=6><index><begin><length>
        blocks = self._linear_piece_manager() # Piece to download
        dprint(client_socket)
        
        piece_data = b''
        piece_time_start = time.time()
        for block in range(blocks):
            if self.remaining_pieces == 1 and blocks == block + 1:
                print("Trying to download the last block:", blocks, "in piece:", self.index, "with a size of:", self.block_size_last)
                request_message = pack('>IBIII', 13, Message.request.value, self.index, block*BLOCK_SIZE, self.block_size_last) 
            else:
                request_message = pack('>IBIII', 13, Message.request.value, self.index, block*BLOCK_SIZE, BLOCK_SIZE)
            
            try:
                #iprint("Requesting block:", block+1, "from peer")
                client_socket.send(request_message)

                response = b''
                start = time.time()
                while True:
                    time.sleep(FACTOR) # NOTE:HAX
                    # BUG: recv can read buffer before it has all data which is tits down not up
                    response = client_socket.recv(13 + BLOCK_SIZE) # Make buffer size correct length                     
                    message = unpack('>IBII', response[0:13]) # Unpacking transaction "Header"

                    message_block_size = message[0] - 9 # TODO: Fix hardcoding 
                    message_id = message[1]
                    message_index = message[2]
                    message_begin = message[3] # TODO :: (This is the offset to the next block we are looking for)

                    # Validates if a incoming message are a piece message
                    if message_block_size == BLOCK_SIZE and message_id == Message.piece.value and message_index == self.index:
                        # TEST HAX START: (If not full data look again in buffer)
                        hax = 0
                        while True:
                            # SUPERHAX START
                            if self.remaining_pieces == 1 and blocks == block + 1: 
                                response = response + client_socket.recv(13 + self.block_size_last - len(response))
                                time.sleep(0.05)
                                hax += 1
                                if hax > 4:
                                    break # Should then move to next not continue to download BUG
                            # SUPERHAX END
                            if len(response) < 13 + BLOCK_SIZE:
                                #dprint("TEST:", len(response), "Expected:", 13 + BLOCK_SIZE)
                                response = response + client_socket.recv(13 + BLOCK_SIZE - len(response))
                                time.sleep(0.05)
                                hax += 1
                                if hax > 4:
                                    break # Should then move to next not continue to download BUG
                            else:
                                break
                            
                            
                        # TEST HAX END:
                        iprint("Peer response:", message, "adding data to piece")
                        #dprint(len(response[13:]))
                        piece_data = piece_data + response[13:] 
                        break
                    
                    else:
                        dprint("Not a piece message")

                    # After time t break out and move to next peer NOTE: do we ever get here even?
                    if (time.time() - start)  >= 1: # 500ms
                        print("Peer did not send a valid piece message within the alloted time")
                        return b'', False

            except Exception as e:
                eprint("Cant download piece:", e)
                return b'', False
        
        # We are faster but still slow as
        # TESTING TO COMPUTE THE DOWNLOAD SPEEEEEEEEEEEEEEEEEEEED :)
        piece_time_end = time.time()

        iprint("Download rate for piece:", self.index, "->" , ((blocks * BLOCK_SIZE) / (piece_time_end - piece_time_start))/(1024*1024), "MB/s")

        piece_data = self._piece_validation(piece_data)
        flag = self._piece_last_check()

        return piece_data, flag


if __name__ == '__main__':
    # Used for testing
    multitorrent = './test/torrents/multi.torrent'
    singeltorrent = './test/torrents/single.torrent'
    metadata = TorrentFile(singeltorrent).read()
