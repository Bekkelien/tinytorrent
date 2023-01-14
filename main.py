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
TEST = False # Only test first torrent in files list
INDEX = 50 # Try to get data from n peers 

if __name__ == '__main__':
    iprint("Starting TinyTorrent client with peer id:", config['client']['peer_id'])

    PATH = Path('./src/files/')
    files = ['gimp.torrent','tails.torrent', 'ubuntu.torrent','single.torrent','slackware.torrent', 'kalilinux.torrent','altlinux.torrent', 'wired-cd.torrent']
    files = ['pi.torrent']

    for file in files:
        # Move, 3 tings for one "thing" how is this normally done to reduce dependencies? -- 

        ### Get Metadata from torrent file ###
        file = TorrentFile(PATH / file)
        file.read_torrent_file() # TODO: fix temp all the way through
        metadata = file.parse_torrent_file()

        ### Get peers IP addresses ###
        tracker = TrackerManager(metadata)
        client_addresses = tracker.get_clients()
        dprint(client_addresses)

        ### Connect to peers and download data from torrent ###
        peer_wire = PeerWire(metadata)
        for index, client_address in enumerate(client_addresses, start=1):
            iprint("TEST CONNECTION:", index, color='blue')
            #TODO:
            peer_wire.handshake(client_address)

            if index >= INDEX:
                break

        if TEST:
            break

