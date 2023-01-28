# Internals
from src.config import Config
from src.tracker_udp import UdpTracker, EventUdp
from src.tracker_http import TrackerConnectionHttp, EventHttp
from src.helpers import iprint, eprint, wprint, dprint, timer

from src.config import Config

# Configuration settings
config = Config().get_config()

class TrackerManager():
    def __init__(self, metadata):
        self.metadata = metadata
        self.client_addresses = []
        self.peers = 0

    def _tracker_http(self, announce, scrape=False):
            tracker = TrackerConnectionHttp(self.metadata, announce)
            client_addresses = tracker.announce(EventHttp.started) # NOTE:: EVENT not yet "supported"
            if scrape:
                tracker.scrape()
            
            return client_addresses

    def _tracker_udp(self, announce, scrape=False):
        client_addresses = [] # BUGFIX a bit nasty, but returns None if not connected to udp tracker
        tracker = UdpTracker(self.metadata, announce)
        if tracker.connect():
            client_addresses = tracker.announce(EventUdp.started.value) # NOTE:: EVENT not yet "supported"
            if scrape:
                tracker.scrape()
            tracker.close()
        
        return client_addresses

    def get_clients(self):
        # New version fetches all clients from the peers, NOTE: Reduce client amount should not be here because this is fast!
        for announce in self.metadata['announce_list']:

            if 'ipv6' in announce:
                wprint("IPv6 is currently not supported") 
                client_addresses = []

            elif announce.startswith('udp'):
                client_addresses = self._tracker_udp(announce)
            
            elif any(announce.startswith(x) for x in ['http', 'https']):
                client_addresses = self._tracker_http(announce)
            
            else:
                wprint("Unknown tracker protocol", announce[:announce.rfind(':')], "for tracker:", announce) # Typical wss or so
                client_addresses = []

            if client_addresses:
                self.client_addresses = self.client_addresses + client_addresses
                self.client_addresses = [list(x) for x in set(tuple(x) for x in self.client_addresses)] # Remove duplicates
                self.peers += len(self.client_addresses)
            
        iprint("Get clients resulted in:", self.peers, "Peers/Client addresses")

        return self.client_addresses
