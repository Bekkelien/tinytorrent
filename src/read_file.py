import copy
import hashlib

from pathlib import Path
from pprint import pprint
from bencoding import bdecode, bencode 

# Internals
from src.helpers import iprint, eprint, wprint, dprint, tprint, timer

# INFO:
# https://en.wikipedia.org/wiki/Torrent_file
# https://bencoding.readthedocs.io/en/latest/quickstart.html#decode-data
# https://stackoverflow.com/questions/46025771/python3-calculating-torrent-hash


class TorrentFile():
    def __init__(self, torrent_file):
        self.data = {}
        self.file_path = Path(torrent_file)

    #@timer
    def read_torrent_file(self):

        iprint("Reading in torrent file:", self.file_path.name)

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

        # NOTE: -> if files are name of single file name of data then this will lead to wrong mapping
        if b'files' in data[b'info']: 
            paths = data[b'info'][b'files']

            if len(paths[0][b'path']) == 1:
                files = []
                for i in range(len(paths)):
                    files.append({'length': paths[i][b'length'], 'path': [paths[i][b'path'][0].decode()]})
            else:
                eprint("Reading torrent file failed: multiple paths within one file path") # NOTE: Overkill error handling? Maybe this never happens?

            self.data['info'] = {'files': files, 'name': name, 'piece_length': piece_length, 'pieces': pieces}

        else:
            length = data[b'info'][b'length']
            self.data['info'] = {'length': length, 'name': name, 'piece_length': piece_length, 'pieces': pieces}

        iprint("New torrent:", self.data['info']['name'], color="green")

        # NOTE: Leave this on or debug only?
        # Print the header of a torrent file
        info_temp = copy.deepcopy(self.data)
        del info_temp['info']['pieces']
        tprint(info_temp)
        del info_temp

        return self.data, info_hash

    
    def parse_torrent_file(self, block_size=20):
        if 'announce-list' in self.data:
            announce_list = set(self.data['announce-list'] + [self.data['announce']])
        else:
            announce_list = [self.data['announce']]
        
        pieces = int(len(self.data['info']['pieces'])/block_size)
        size = self.data['info']['piece_length'] * pieces

        iprint("Trackers:", announce_list)
        iprint("Piece size:", self.data['info']['piece_length']/1024, "KB") # ALWAYS use ceil?
        iprint("Number of pieces:", pieces)
        iprint("Torrent size:", size/1024/1024, "MB")

        return announce_list

if __name__ == '__main__':
    """ TESTING TESTING TESTING TESTING TESTING TESTING TESTING TESTING """

    PATH = Path('./src/files/')
    files = ['tails.torrent','ChiaSetup-1.6.1.exe.torrent','ubuntu.torrent','big-buck-bunny.torrent']

    for file in files:
        file = TorrentFile(PATH / file)

        torrent, info_hash = file.read_torrent_file()

        # Removing hashes for pieces to se info in torrent file data
        del torrent['info']['pieces']
        pprint(torrent)
        iprint("File:", torrent['info']['name'] ,"info hash:", info_hash)