
from src.helpers import iprint, dprint
from src.read_torrent import MetadataStorage

class StoreDownload:
    """ Stores a full torrent that are living in memory """
    def __init__(self) -> None:
        self.path = "./download/" # TODO make a config 
        self.metadata = MetadataStorage().metadata

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
            #dprint(file_index_stop-file_index_start, file_size)

            assert (file_index_stop-file_index_start) == file_size
            file_data = data[file_index_start:file_index_start+self.metadata['files'][index]['length']]
            
            # Update index for next file
            file_index_start = sum([self.metadata['files'][i]['length'] for i in range(index+1)])

            self._to_disk(file, file_data)

            iprint("Saved:", file, "to disk of size:", file_size)