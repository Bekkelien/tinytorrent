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
        self.peer_ip = []
        self.peers = 0

    def _tracker_http(self, announce, scrape=False):
            tracker = TrackerConnectionHttp(self.metadata, announce)
            peer_ip = tracker.announce(EventHttp.started) # NOTE:: EVENT not yet "supported"
            if scrape:
                tracker.scrape()
            
            return peer_ip

    def _tracker_udp(self, announce, scrape=False):
        peer_ip = [] # BUGFIX a bit nasty, but returns None if not connected to udp tracker
        tracker = UdpTracker(self.metadata, announce)
        try:  # HAX for now refix
            if tracker.connect():
                peer_ip = tracker.announce(EventUdp.started.value) # NOTE:: EVENT not yet "supported"
                if scrape:
                    tracker.scrape()
                tracker.close()
        
        except:
            pass
        return peer_ip

    def get_clients(self):
        # New version fetches all clients from the peers, NOTE: Reduce client amount should not be here because this is fast!
        for announce in self.metadata['announce_list']:

            if 'ipv6' in announce:
                wprint("IPv6 is currently not supported") 
                peer_ip = []

            elif announce.startswith('udp'):
                peer_ip = self._tracker_udp(announce)
            
            elif any(announce.startswith(x) for x in ['http', 'https']):
                peer_ip = self._tracker_http(announce)
            
            else:
                wprint("Unknown tracker protocol", announce[:announce.rfind(':')], "for tracker:", announce) # Typical wss or so
                peer_ip = []

            if peer_ip:
                self.peer_ip = self.peer_ip + peer_ip
                self.peer_ip = [list(x) for x in set(tuple(x) for x in self.peer_ip)] # Remove duplicates
                self.peers += len(self.peer_ip)
            
        iprint("BUG: NOT DISPLAYING CORRECTLY ::: Get clients resulted in:", self.peers, "Peers/Client addresses")
        return self.peer_ip
