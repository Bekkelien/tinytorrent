
# Internals
from src.read_file import TorrentFile
from src.tracker_udp import UdpTracker, EventUdp
from src.tracker_http import HttpTracker, EventHttp
from src.tcp import PeerWire

from src.helpers import iprint, eprint, wprint, dprint, timer

if __name__ == '__main__':

    # Note this will only be for one torrent

    # For testing TODO: Make testing loop 
    #file = TorrentFile('./src/files/tails.torrent')
    #file = TorrentFile('./src/files/multi_file.torrent')
    #file = TorrentFile('./src/files/ChiaSetup-1.6.1.exe.torrent')
    file = TorrentFile('./src/files/slackware.torrent')

    #iprint("Announce: ",torrent['announce'])
    # Handle Announce list 
    # iprint("Announce List: ",torrent['announce-list'])


    torrent, info_hash = file.read_torrent_file()
    if 'udp' in torrent['announce']:
        udp_connection = UdpTracker(torrent, info_hash)
        udp_connection.connect() 
        client_addresses = udp_connection.announce(EventUdp.none.value) 
        udp_connection.scrape()
    
    elif any(protocol in torrent['announce'] for protocol in ['http', 'https']):
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


