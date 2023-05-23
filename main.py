from pathlib import Path

# Internals
from src.config import Config
from src.read_torrent import TorrentFile
from src.manager import TrackerManager
from src.protocol import PeerWire
from src.download import Download
from src.helpers import iprint, eprint, wprint, dprint, timer

# Configuration settings
config = Config().get_config()

# TEST PARAMS 
TEST = False # Only test first torrent in files list
INDEX = 50 # Try to get data from n peers 


#NOTE: :: :ONLY SINGLE FILES ATM
if __name__ == '__main__':
    iprint("Starting TinyTorrent client with peer id:", config['client']['peer_id'])

    PATH = Path('./src/files/')
    #files = ['gimp.torrent','tails.torrent', 'ubuntu.torrent','single.torrent','slackware.torrent', 'kalilinux.torrent','altlinux.torrent', 'wired-cd.torrent']
    files = ['wired-cd.torrent']

    for file in files:
        metadata = TorrentFile(PATH / file).read()

        ### Get peers IP addresses ###
        tracker = TrackerManager(metadata)
        peer_ips = tracker.get_clients()
        #dprint(peer_ips)

        ### Connect to peers and download data from torrent ###
        peer_wire = PeerWire(metadata)
        download = Download(metadata) 

        # hax
        #print(peer_ips[::-1])
        #peer_ips = peer_ips[::-1] 

        data = b''
        for i in range(100): # HAX
            for index, _ in enumerate(peer_ips, start=0):
                iprint("TEST CONNECTION:", index, color='blue')
            #TODO:
                current_peer = peer_wire.handshake(peer_ips, index)
                if current_peer:
                    state = True
                    # Jumps peer for each piece 
                    while state: # Hax to avoid jumpig for each piece
                        block_data, flag = download.linear_test(current_peer) 
                        
                        if block_data:
                            data = data + block_data
                            size_bytes = len(data)
                            #size_mb = size_bytes / (1024*1024)
                            print(size_bytes)

                        else:
                            state = False
                
                        if flag:
                            if 'files' in metadata: # Hax for now (no folders ATM)
                                start_index = 0
                                for index, file in enumerate(metadata['files']):
                                    print("Saving file:", file['path'][0], "of size:", file['length'])
                                    print(start_index,start_index+file['length'])
                                    file_data = data[start_index:start_index+file['length']]
                                    start_index = sum([metadata['files'][i]['length'] for i in range(index+1)])
                                    
                                    with open("./download/" + file['path'][0], 'wb') as file:
                                        file.write(file_data)
                                        
                            else:
                                iprint("File downloaded")
                                with open("./download/" + metadata['files'][0]['path'][0], 'wb') as file:
                                    file.write(data)

                            # Save bin used for testing
                            #with open("./dev/testb.bin", "wb") as file:
                            #    file.write(data)

                            # DONE
                            raise NotImplementedError