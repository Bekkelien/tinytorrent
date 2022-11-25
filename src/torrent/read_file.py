
import hashlib

from pathlib import Path
from pprint import pprint
from bencoding import bdecode, bencode 

from helpers import timer

# NOTE's:
# https://bencoding.readthedocs.io/en/latest/quickstart.html#decode-data
# https://stackoverflow.com/questions/46025771/python3-calculating-torrent-hash


class TorrentFile():
    def __init__(self, torrent_file):
        self.decoded = {}
        self.file = Path(torrent_file)

    @timer
    def read_torrent_file(self):

        with open(self.file, 'rb') as f:
            self.data = bdecode(f.read())
        
        self.info_hash = hashlib.sha1(bencode(self.data[b'info'])).digest() 

        self.decoded['announce'] = self.data[b'announce'].decode()

        name = self.data[b'info'][b'name'].decode()
        piece_length = self.data[b'info'][b'piece length']
        pieces = self.data[b'info'][b'pieces']

        # If torrent contains multiple files # BUG if single name filename is files -> Unlikely but possible 
        if b'files' in self.data[b'info']: 
            paths = self.data[b'info'][b'files']

            files = []
            for index in range(len(paths)):
                files.append({'length': paths[index][b'length'], 'path': [str(paths[index][b'path'])[3:-2]]})
            self.decoded['info'] = {'files': files, 'name': name, 'piece_length': piece_length, 'pieces': pieces}

        else:
            length = self.data[b'info'][b'length']
            self.decoded['info'] = {'length': length, 'name': name, 'piece_length': piece_length, 'pieces': pieces}

        return self.decoded, self.info_hash

if __name__ == '__main__':
    #file = TorrentFile('./src/files/ubuntu.torrent')
    #file = TorrentFile('./src/files/tails.torrent')
    file = TorrentFile('./src/files/multi_file.torrent')
    #file = TorrentFile('./src/files/ChiaSetup-1.6.1.exe.torrent')

    torrent, info_hash = file.read_torrent_file()

    pprint(torrent)
    print(info_hash)

   