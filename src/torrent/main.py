
# Internals
from read_file import TorrentFile
from tracker_udp import UdpTracker, Event
from tcp import PeerWire

from helpers import iprint, eprint, wprint, dprint, timer

if __name__ == '__main__':

    # Note this will only be for one torrent

    # For testing TODO: Make testing loop 
    file = TorrentFile('./src/files/tails.torrent')
    #file = TorrentFile('./src/files/multi_file.torrent')
    #file = TorrentFile('./src/files/ChiaSetup-1.6.1.exe.torrent')

    #iprint("Announce: ",torrent['announce'])
    # Handle Announce list 
    # iprint("Announce List: ",torrent['announce-list'])


    torrent, info_hash = file.read_torrent_file()
    udp_connection = UdpTracker(torrent, info_hash)
    udp_connection.connect() 
    client_addresses = udp_connection.announce(Event.none.value) 
    udp_connection.scraping()

    peer_wire = PeerWire(info_hash, torrent)
    for index, client_address in enumerate(client_addresses, start=1):
        iprint("TEST CONNECTION:", index, color='blue')
        peer_wire.handshake(client_address)


