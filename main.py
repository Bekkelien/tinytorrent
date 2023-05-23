from pathlib import Path

# Internals
from src.config import Config
from src.read_torrent import TorrentFile
from src.manager import TrackerManager
from src.protocol import PeerWire
from src.download import Download
from src.storage import StoreDownload
from src.helpers import iprint

# Configuration settings
config = Config().get_config()


if __name__ == '__main__':
    iprint("Starting TinyTorrent client with peer id:", config['client']['peer_id'])

    PATH = Path('./src/files/')
    #files = ['gimp.torrent','tails.torrent', 'ubuntu.torrent','single.torrent','slackware.torrent', 'kalilinux.torrent','altlinux.torrent', 'wired-cd.torrent']
    files = ['gimp.torrent']

    for file in files:
        metadata = TorrentFile(PATH / file).read()

        ### Get peers IP addresses ### NOTE:: We only get peers when program starts ATM
        tracker = TrackerManager(metadata)
        peer_ips = tracker.get_clients()
        #dprint(peer_ips)

        ### Object for one peer_wire connection ATM
        peer_wire = PeerWire(metadata)

        # Object for one download ATM
        download = Download(metadata) 

        data = b''
        for i in range(100): # HAX
            for index, _ in enumerate(peer_ips, start=0):
                iprint("TEST CONNECTION:", index, color='blue')
            #TODO: We are doing handshake every time ATM 
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
                            StoreDownload().save(data)
    
                            raise NotImplementedError