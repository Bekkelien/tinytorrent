from pathlib import Path

# Internals
from src.config import Config
from src.read_torrent import TorrentFile
from src.manager import TrackerManager
from src.protocol import PeerWire
from src.helpers import iprint, eprint, wprint, dprint, timer

# Configuration settings
config = Config().get_config()

# TEST PARAMS 
TEST = False # Only test first torrent in files list
INDEX = 50 # Try to get data from n peers 

if __name__ == '__main__':
    iprint("Starting TinyTorrent client with peer id:", config['client']['peer_id'])

    PATH = Path('./src/files/')
    #files = ['gimp.torrent','tails.torrent', 'ubuntu.torrent','single.torrent','slackware.torrent', 'kalilinux.torrent','altlinux.torrent', 'wired-cd.torrent']
    #files = ['pi.torrent']
    files = ['gimp.torrent']

    for file in files:
        metadata = TorrentFile(PATH / file).read()

        ### Get peers IP addresses ###
        tracker = TrackerManager(metadata)
        peer_ips = tracker.get_clients()
        dprint(peer_ips)

        ### Connect to peers and download data from torrent ###
        peer_wire = PeerWire(metadata)

        test = []
        for i in range(100): # HAX
            for index, _ in enumerate(peer_ips, start=0):
                iprint("TEST CONNECTION:", index, color='blue')
            #TODO:
                peer_wire.handshake(peer_ips, index, test)
            
            break


        #if index >= INDEX:
        #    break

       # if TEST:
       #     break

