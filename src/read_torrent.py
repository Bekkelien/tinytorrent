import math
import hashlib

from pathlib import Path
from bitstring import BitArray
from bencoding import bdecode, bencode 

# Internals
from src.helpers import iprint, tprint

BLOCK_SIZE = 20

class TorrentFile:
    def __init__(self, file):
        self.file_path = Path(file)

    def read(self) -> dict:
        """ Read a new torrent file and return a dictionary of metadata """

        metadata = {}

        iprint("New torrent file:", self.file_path.name, color="green")

        with open(self.file_path, 'rb') as file:
            torrent = bdecode(file.read())
        
        metadata['info_hash'] = hashlib.sha1(bencode(torrent[b'info'])).digest()

        if b'announce' in torrent: metadata['announce_list'] = [torrent[b'announce'].decode()]
        if b'announce-list' in torrent: metadata['announce_list'] = [x[0].decode() for x in torrent[b'announce-list']]

        if b'files' in torrent[b'info']:
            metadata['size'] = sum(file[b'length'] for file in torrent[b'info'][b'files'])
            metadata['files'] = [{'length': path[b'length'], 'path': [path[b'path'][0].decode()]} for path in torrent[b'info'][b'files']]
        else:
            metadata['size'] = torrent[b'info'][b'length'] 
            metadata['files'] = [{'length': torrent[b'info'][b'length'], 'path': [torrent[b'info'][b'name'].decode()]}]

        metadata['name'] = torrent[b'info'][b'name'].decode()
        metadata['pieces'] = torrent[b'info'][b'pieces']  
        metadata['piece_length'] = torrent[b'info'][b'piece length']
        metadata['pieces_count'] = int(len(torrent[b'info'][b'pieces'])/BLOCK_SIZE)
        metadata['bitfield_spare'] = 8 * math.ceil(metadata['pieces_count']/8) - metadata['pieces_count']
        metadata['bitfield_length'] = metadata['pieces_count'] + metadata['bitfield_spare']
        metadata['left'] = metadata['size']
        metadata['downloaded'] = 0
        metadata['uploaded'] = 0

        metadata['pieces_downloaded'] = BitArray([0] * (metadata['bitfield_length'] - metadata['bitfield_spare'])).bin
        metadata['bitfield'] = BitArray([1] * (metadata['bitfield_length'] - metadata['bitfield_spare']) + [0] * metadata['bitfield_spare']).bin
        tprint(metadata) 
 
        return metadata

# add to one class? TODO
class MetadataStorage:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
        
if __name__ == '__main__':
        PATH = Path('./src/files/')
        file_1 = 'gimp.torrent'

        # Parse a torrent files
        metadata_dict = TorrentFile(PATH / file_1).read()
        MetadataStorage = metadata_dict # Can we do this more clean? 
        print(MetadataStorage)



