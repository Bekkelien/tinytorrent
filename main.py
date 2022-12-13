# Internals
from src.config import Config
from src.read_file import TorrentFile
from src.tracker_udp import UdpTracker, EventUdp
from src.tracker_http import HttpTracker, EventHttp
from src.tcp import PeerWire
from pathlib import Path
from src.helpers import iprint, eprint, wprint, dprint, timer

# Configuration settings
config = Config().get_config()

if __name__ == '__main__':

    PATH = Path('./src/files/')
    files = ['kalilinux.torrent', 'ubuntu.torrent', 'altlinux.torrent', 'slackware.torrent']

    
    for file in files:
        file = TorrentFile(PATH / file)
        
        torrent, info_hash = file.read_torrent_file()

        announce_list = set(torrent['announce-list'] + [torrent['announce']])
        iprint("Trackers:", announce_list)

        # NOTE: START LOGIC TEST 
        peers = 0
        client_addresses = []
        for announce in announce_list:
            iprint("Announce address:", announce)

            if 'ipv6' in announce: 
                wprint("IPv6 is not currently supported") 
                break

            if announce.startswith('udp'):
                udp_connection = UdpTracker(torrent, info_hash, announce)
                udp_connection.connect() 
                client_addresses_temp = udp_connection.announce(EventUdp.none.value)
                udp_connection.scrape()
            
            elif any(announce.startswith(x) for x in ['http', 'https']):
                trackers = HttpTracker(torrent, info_hash, announce)
                if trackers.announce(EventHttp.started):
                    client_addresses_temp = trackers.tracker_response() 
                    #trackers.scrape() # TODO:
            else:
                raise Exception("Unknown tracker protocol")

            if client_addresses_temp:
                client_addresses = client_addresses + client_addresses_temp
                peers += len(client_addresses)

            if peers >= config['http']['peer_limit']:
                break
        

        if peers >= config['http']['peer_limit']:
            iprint("Peer amount:", peers, "accepted with minimum limit of:", config['http']['peer_limit'])

        elif peers == 0:
            wprint("No peers found")
        else:
            iprint("Low amount of peers, found only:", peers, "peers")

        #NOTE: END LOGIC TEST 

        peer_wire = PeerWire(info_hash, torrent)
        for index, client_address in enumerate(client_addresses, start=1):
            iprint("TEST CONNECTION:", index, color='blue')
            peer_wire.handshake(client_address)

            # TESTING
            #if index > 5:
            #    break


