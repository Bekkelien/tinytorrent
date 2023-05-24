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

FACTOR = 0.5 # Dumb hax 
BLOCK_SIZE = 2**14

# NOTE: Current index and rest pieces are a bit messy 
class Download:
    def __init__(self, metadata) -> None:
        self.metadata = metadata
        self.current_piece_index = self.metadata['pieces_downloaded'].count('1')
        self.remaining_pieces = self.metadata['pieces_downloaded'].count('0')
        self.block_size_last =  (metadata['size']%metadata['piece_length']) % BLOCK_SIZE 

        # Downloaded data:
        self.factor = FACTOR # TODO: current hax to wait for data 

    def _linear_piece_manager(self) -> int:
        self.current_piece_index  = self.metadata['pieces_downloaded'].count('1')
        self.remaining_pieces = self.metadata['pieces_downloaded'].count('0')
        
        blocks = math.ceil(self.metadata['piece_length'] / BLOCK_SIZE) 
        
        # Overwrite expression for last pice
        if self.remaining_pieces == 1:
            blocks = math.ceil((self.metadata['size']-self.metadata['piece_length']*self.current_piece_index ) / BLOCK_SIZE) 
        
        iprint("Trying to downloaded pieces:", self.current_piece_index , "blocks:", blocks, "remaining pieces:", self.remaining_pieces) # HAX
        return blocks


    def _piece_validation(self, piece_data) -> bytes:
        piece_hash = hashlib.sha1(piece_data).digest()

        if piece_hash == self.metadata['pieces'][(self.current_piece_index*20):20 +(self.current_piece_index*20)]: # Make this easier to index?
            iprint("Piece:", self.current_piece_index, "hash is verified" , color="green")

            # TODO: Update metadata Downloaded well that is hard without storing it to file (NOTE: make metadata a file?), left also download speed for this piece here

            if self.factor > 0.2: self.factor = self.factor - 0.1 # NOTE:: The most dumb speed adjuster for downloading in the history of downloading (how to know when peer responds with data?)

            # NOTE: this was a bad idea since strings in python are immutable but lets go with it for now
            self.metadata['pieces_downloaded'] = self.metadata['pieces_downloaded'][:self.current_piece_index] + '1' + self.metadata['pieces_downloaded'][self.current_piece_index + 1:]

            return piece_data
    
        else: 
            wprint("Piece:", self.current_piece_index, "hash verification failed")
            self.factor = FACTOR
            iprint("Restoring factor back to:", FACTOR)
            return  b''        

    def _piece_last_check(self):
        if self.current_piece_index == self.metadata['pieces_count'] - 1:  
            return True
    
        return False


    def linear_download_piece(self, current_peer): # Bytes,bool how to do two return stuff thing
        blocks = self._linear_piece_manager() # Piece to download
        dprint(current_peer)
        
        piece_data = b''
        timeout_hax = 0
        piece_start_time = time.time()
        for block in range(blocks):
            if self.remaining_pieces == 1 and blocks == block + 1:
                print("Trying to download the last block:", blocks, "in piece:", self.current_piece_index, "with a size of:", self.block_size_last)
                request_message = pack('>IBIII', 13, Message.request.value, self.current_piece_index, block*BLOCK_SIZE, self.block_size_last) 
            else:
                request_message = pack('>IBIII', 13, Message.request.value, self.current_piece_index, block*BLOCK_SIZE, BLOCK_SIZE)
            
            try:
                looking_hax = True
                while looking_hax:
                    current_peer.send(request_message)
                    time.sleep(self.factor) # NOTE:HAX
                    response = current_peer.recv(24576) # Find a good buffer size
                    message = unpack('>IBII', response[0:13]) # Unpacking transaction "Header"

                    if message[0] == BLOCK_SIZE + 9 and message[1] == Message.piece.value and message[2] == self.current_piece_index:
                        #if message[3] == self.block_size_last or message[3] == BLOCK_SIZE: #TODO later
                        iprint("Peer response:", message, "adding data to piece")
                        piece_data = piece_data + response[13:] 
                        looking_hax = False
                        #else:
                        #    wprint("Payload size in this block is invalid cant download piece")
                        #    looking_hax = False
                        #    break
                        
                    else: # If not a piece message look again -> HAX ATM as we are not handling incoming messages NOTE::TODO
                        wprint("Unknown message from peer:", message)
                        looking_hax = True
                        timeout_hax += 1
                        if timeout_hax >= 2:
                            wprint("Since we do not handle incoming messages from peers timeout has ocurred")
                            return b'', False

            except Exception as e:
                eprint("Cant download piece:", e)
                return b'', False
        
        piece_data = self._piece_validation(piece_data)
        flag = self._piece_last_check()

        if piece_data and not flag:
            piece_download_rate = (time.time() - piece_start_time) / ((blocks * BLOCK_SIZE) / 1024 / 1024)
            iprint("Piece download rate:", piece_download_rate, "MB/s")

        return piece_data, flag


if __name__ == '__main__':
    # Used for testing
    multitorrent = './test/torrents/multi.torrent'
    singeltorrent = './test/torrents/single.torrent'
    metadata = TorrentFile(singeltorrent).read()
