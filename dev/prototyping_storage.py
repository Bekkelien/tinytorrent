from pathlib import Path

from src.read_torrent import TorrentFile

PATH = Path('./src/files/')

files = ['wired-cd.torrent']

for file in files:
    metadata = TorrentFile(PATH / file).read()

    with open("./testb.bin", "rb") as file:
        data = file.read()
        print(len(data))
        
    # Multi indexing not good rewrite
    start_index = 0
    for index, file in enumerate(metadata['files']):
        print("Saving file:", file['path'][0], "of size:", file['length'])
        print(start_index,start_index+file['length'])
        file_data = data[start_index:start_index+file['length']]
        start_index = sum([metadata['files'][i]['length'] for i in range(index+1)])
        
        with open("./download/" + file['path'][0], 'wb') as file:
            file.write(file_data)