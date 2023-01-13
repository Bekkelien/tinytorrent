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
        """ Uses the convention from: https://en.wikipedia.org/wiki/Torrent_file#cite_note-bep0003-1 """

        iprint("New torrent file:", self.file_path.name, color="green")

        with open(self.file_path, 'rb') as file:
            data = bdecode(file.read())
        
        self.info_hash = hashlib.sha1(bencode(data[b'info'])).digest()

        if b'announce' in data:
            self.data['announce'] = data[b'announce'].decode()

        if b'announce-list' in data:
            self.data['announce-list'] = [x[0].decode() for x in data[b'announce-list']]
                   
        name = data[b'info'][b'name'].decode()
        piece_length = data[b'info'][b'piece length']
        pieces = data[b'info'][b'pieces']

        # BUG (For instance single torrent has name files in it, although this is very unlikely in practice)
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

        #print(self.data)
        #return self.data, self.info_hash

    
    def parse_torrent_file(self, block_size = 20):
        """ Uses custom TinyTorrent convention """
        self.metadata = {}

        if 'announce-list' in self.data:
            self.metadata['announce-list'] = set(self.data['announce-list'] + [self.data['announce']])
        else:
            self.metadata['announce-list'] = set([self.data['announce']])

        pieces = int(len(self.data['info']['pieces'])/block_size)
        size = self.data['info']['piece_length'] * pieces

        self.metadata['piece_length'] = self.data['info']['piece_length']
        self.metadata['pieces'] = pieces
        self.metadata['size'] = size         
        
        # Kinda fixes the BUG in read torrent
        if 'files' in self.data['info']: 
            temp = []
            for i in range(len(self.data['info']['files'])):
                temp.append(self.data['info']['files'][i])

            self.metadata['files'] = temp
        else:                
            self.metadata['files'] = [{'length': self.data['info']['length'], 'path': [self.data['info']['name']]}]
        bitfield_spare_bits = 8 * math.ceil(pieces/8) - pieces

        self.metadata['bitfield_spare_bits'] = bitfield_spare_bits
        self.metadata['bitfield_length'] = pieces + bitfield_spare_bits


        self.metadata['downloaded'] = 0
        self.metadata['uploaded'] = 0

        # Kinda fixes the BUG in read torrent
        if 'files' in self.data['info']:
            left = 0
            for file in self.metadata['files']:
                left += file['length']
            
            self.metadata['left'] = left

        else:
            self.metadata['left'] = self.data['info']['length']

        self.metadata['info_hash'] = self.info_hash
        self.metadata['name'] = self.data['info']['name']

        tprint(self.metadata)
        return self.metadata
