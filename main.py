from pathlib import Path

# Internals
from src.config import Config
from src.read_file import TorrentFile
from src.manager import TrackerManager
from src.tcp import PeerWire
from src.helpers import iprint, eprint, wprint, dprint, timer

# Configuration settings
config = Config().get_config()

# TEST PARAMS 
TEST = True # Only test first torrent in files list
INDEX = 10 # Try to get data from 5 peers 

if __name__ == '__main__':
    iprint("Starting TinyTorrent client with peer id:", config['client']['peer_id'])

    PATH = Path('./src/files/')
    files = ['gimp.torrent', 'ubuntu.torrent','single.torrent','slackware.torrent','kalilinux.torrent', 'altlinux.torrent','tails.torrent', 'wired-cd.torrent']
    

    for file in files:
        # Move, 3 tings for one "thing" how is this normally done to reduce dependencies? -- 

        ### Get Metadata from torrent file ###
        file = TorrentFile(PATH / file)
        file.read_torrent_file()
        metadata = file.parse_torrent_file()

        # TODO: Compute last piece size, or check in logic?

        ### Get peers IP addresses ###
        tracker = TrackerManager(metadata)
        client_addresses = tracker.get_clients()
        dprint(client_addresses)

        ### Connect to peers and download data from torrent ###
        peer_wire = PeerWire(metadata)
        for index, client_address in enumerate(client_addresses, start=1):
            iprint("TEST CONNECTION:", index, color='blue')
            peer_wire.handshake(client_address)

            if index >= INDEX:
                break

        if TEST:
            break

