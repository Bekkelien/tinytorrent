import socket
# Internals
from src.config import Config
from src.read_file import TorrentFile
from src.tracker_udp import UdpTracker, EventUdp
from src.tracker_http import TrackerConnectionHttp, EventHttp
from src.tcp import PeerWire
from pathlib import Path
from src.helpers import iprint, eprint, wprint, dprint, timer

from src.config import Config

# Configuration settings
config = Config().get_config()

# Make this to a class

def test(metadata):
    peers = 0
    client_addresses, client_addresses_temp = [], []
    for announce in metadata['announce-list']:
        iprint("Announce address:", announce)#, "ip:", socket.getaddrinfo(announce))

        #if 'ipv6' in announce:
        #    # TODO move into tracker protocol 
        #    wprint("IPv6 is not currently supported") 
        #    break

        if announce.startswith('udp'):
            dprint("disabled for testing") #NOTE::
            #udp_connection = UdpTracker(metadata, announce)
            #if udp_connection.connect():
            #    client_addresses_temp = udp_connection.announce(EventUdp.none.value)
            #    #udp_connection.scrape()

        elif any(announce.startswith(x) for x in ['http', 'https']):
            tracker = TrackerConnectionHttp(metadata, announce)
            client_addresses_temp = tracker.announce(EventHttp.started)
            # tracker.scrape()

        else:
            index = announce.rfind(':')
            wprint("Unknown tracker protocol:", announce[:index])

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
    
    return client_addresses