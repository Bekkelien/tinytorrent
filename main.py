
# Internals
from src.read_file import TorrentFile
from src.tracker_udp import UdpTracker, EventUdp
from src.tracker_http import HttpTracker, EventHttp
from src.tcp import PeerWire
from pathlib import Path
from src.helpers import iprint, eprint, wprint, dprint, timer

if __name__ == '__main__':

    PATH = Path('./src/files/')
    files = ['kalilinux.torrent', 'ubuntu.torrent', 'altlinux.torrent', 'slackware.torrent']

    for file in files:
        file = TorrentFile(PATH / file)
        
        torrent, info_hash = file.read_torrent_file()

        # Integrate list solution 
        announce = torrent['announce']

        if announce.startswith('udp'):
            udp_connection = UdpTracker(torrent, info_hash)
            udp_connection.connect() 
            client_addresses = udp_connection.announce(EventUdp.none.value) 
            udp_connection.scrape()
        
        elif any(announce.startswith(x) for x in ['http', 'https']):
            trackers = HttpTracker(torrent, info_hash)
            if trackers.announce(EventHttp.started):
                client_addresses = trackers.tracker_response()
                trackers.scrape()
                
                
        else:
            raise Exception("Unknown tracker protocol")

        peer_wire = PeerWire(info_hash, torrent)
        for index, client_address in enumerate(client_addresses, start=1):
            iprint("TEST CONNECTION:", index, color='blue')
            peer_wire.handshake(client_address)

            # TESTING
            if index > 5:
                break


