import copy
import math
import hashlib

from pathlib import Path
from bencoding import bdecode, bencode 

# Internals
from src.helpers import iprint, eprint, tprint #,timer

class TorrentFile():
    def __init__(self, torrent_file):
        self.data = {}
        self.file_path = Path(torrent_file)

    #@timer
    def read_torrent_file(self):

        iprint("New torrent file:", self.file_path.name, color="green")

        with open(self.file_path, 'rb') as file:
            data = bdecode(file.read())
        
        info_hash = hashlib.sha1(bencode(data[b'info'])).digest()

        if b'announce' in data:
            self.data['announce'] = data[b'announce'].decode()

        if b'announce-list' in data:
            self.data['announce-list'] = [x[0].decode() for x in data[b'announce-list']]
                   
        name = data[b'info'][b'name'].decode()
        piece_length = data[b'info'][b'piece length']
        pieces = data[b'info'][b'pieces']

        if b'files' in data[b'info']: 
            paths = data[b'info'][b'files']

            if len(paths[0][b'path']) == 1:
                files = []
                for i in range(len(paths)):
                    files.append({'length': paths[i][b'length'], 'path': [paths[i][b'path'][0].decode()]})
            else:
                eprint("Reading torrent file failed: multiple paths within one file path") # NOTE: Overkill error handling? Maybe this ''never'' happens?

            self.data['info'] = {'files': files, 'name': name, 'piece_length': piece_length, 'pieces': pieces}

        else:
            length = data[b'info'][b'length']
            self.data['info'] = {'length': length, 'name': name, 'piece_length': piece_length, 'pieces': pieces}

        return self.data, info_hash

    
    def parse_torrent_file(self, _print=True, block_size = 20):

        if 'announce-list' in self.data:
            announce_list = set(self.data['announce-list'] + [self.data['announce']])
        else:
            announce_list = set([self.data['announce']])

        pieces = int(len(self.data['info']['pieces'])/block_size)
        size = self.data['info']['piece_length'] * pieces

        # ALL of this is temp stuff 
        # TODO: Hax'y solution
        if _print:
            temp_dict = copy.deepcopy(self.data)
            temp_dict['announce-list'] = announce_list
            temp_dict['pieces'] = pieces
            temp_dict['size'] = size         

            tprint(temp_dict)
            # TESTING'
            del temp_dict['info']['pieces']
            # TESTING
            
        bitfield_spare_bits = 8 * math.ceil(pieces/8) - pieces
        bitfield_length = pieces + bitfield_spare_bits
        iprint("TEMP bitfield_spare_bits:",bitfield_spare_bits)
        iprint("TEMP bitfield_length:",bitfield_length)
        print("Make a new dict with all info need for torrent n?")

        temp_dict['bitfield_spare_bits'] = bitfield_spare_bits
        temp_dict['bitfield_length'] = bitfield_length
        print(temp_dict)

        del temp_dict
        return announce_list