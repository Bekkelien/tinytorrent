from pathlib import Path

from src.read_torrent import TorrentFile
from src.helpers import iprint, dprint

from pathlib import Path

from src.read_torrent import TorrentFile, MetadataStorage

PATH = Path('./src/files/')

files = ['wired-cd.torrent']

class StoreDownload:
    """ Stores a full torrent that are living in memory """
    def __init__(self) -> None:
        self.path = "./download/" # TODO make a config 
        self.metdata = MetadataStorage().metadata

    def _to_disk(self, file, data):
        with open(self.path + file, 'wb') as file:
            file.write(data)

    def save(self, data) -> None:
        """ Save torrent from memory to disk when done downloading """
        
        file_index_start = 0
        for index, _ in enumerate(self.metadata['files']):
            file = self.metadata['files'][index]['path'][0]
            file_size = self.metadata['files'][index]['length']
            file_index_stop = file_index_start+self.metadata['files'][index]['length']

            #dprint(file_index_start, file_index_stop)
            iprint("Saving:", file, "to disk of size:", file_size)
            #dprint(file_index_stop-file_index_start, file_size)


            assert (file_index_stop-file_index_start) == file_size
            file_data = data[file_index_start:file_index_start+self.metadata['files'][index]['length']]
            
            # Update index for next file
            file_index_start = sum([self.metadata['files'][i]['length'] for i in range(index+1)])

            self._to_disk(file, file_data)

if __name__=='__main__':

    for file in files:
        metadata = TorrentFile(PATH / file).read()

        with open("./dev/testb.bin", "rb") as file:
            data = file.read()
            print(len(data))
            
        StoreDownload(metadata).save(data)