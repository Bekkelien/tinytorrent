from pathlib import Path

# Internals
from src.config import Config
from src.read_file import TorrentFile
from src.tracker_udp import UdpTracker, EventUdp
from src.tracker_http import HttpTracker, EventHttp
from src.tcp import PeerWire
from src.manager import test
from src.helpers import iprint, eprint, wprint, dprint, timer

# Configuration settings
config = Config().get_config()

# ADD TO Configs

if __name__ == '__main__':
    iprint("Starting TinyTorrent client with peer id:", config['client']['peer_id'])

    PATH = Path('./src/files/')
    files = ['ubuntu.torrent','single.torrent','slackware.torrent','kalilinux.torrent', 'altlinux.torrent','tails.torrent', 'wired-cd.torrent']

    
    for file in files:
        # Move, 3 tings for one "thing" how is this normally done to reduce dependencies? -- 
        file = TorrentFile(PATH / file)
        file.read_torrent_file()
        metadata = file.parse_torrent_file()

        # TODO: Compute last piece size, or check in logic?

        # NOTE: START LOGIC TEST 
        client_addresses = test(metadata)
        #NOTE: END LOGIC TEST 

        peer_wire = PeerWire(metadata)
        for index, client_address in enumerate(client_addresses, start=1):
            iprint("TEST CONNECTION:", index, color='blue')
            peer_wire.handshake(client_address)

            # TESTING
            #if index > 5:
            #    break


