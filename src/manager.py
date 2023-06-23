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
            if scrape: tracker.scrape()
            return peer_ip

    def _tracker_udp(self, announce, scrape=False):
        peer_ip = [] # BUGFIX a bit nasty, but returns None if not connected to udp tracker
        tracker = UdpTracker(self.metadata, announce)
        try:  # HAX for now refix
            if tracker.connect():
                peer_ip = tracker.announce(EventUdp.started.value) # NOTE:: EVENT not yet "supported"
                if scrape: tracker.scrape()
                tracker.close()

        except:
            pass
        return peer_ip

    def get_clients(self):
        for announce in self.metadata['announce_list']:

            # TODO
            if 'ipv6' in announce:
                wprint("IPv6 is currently not supported") 
                peer_ip = []

            # Tracker is UDP
            elif announce.startswith('udp'):
                peer_ip = self._tracker_udp(announce)
            
            # Tracker is HTTPS
            elif any(announce.startswith(x) for x in ['http', 'https']):
                peer_ip = self._tracker_http(announce)
            
            # Unknown tracker protocol for tinytorrent (wss++)
            else:
                wprint("Tracker protocol:", announce[:announce.rfind(':')], "for tracker:", announce, "not supported") 
                peer_ip = []

            if peer_ip:
                self.peer_ip = self.peer_ip + peer_ip
                self.peer_ip = [tuple(x) for x in set(tuple(x) for x in self.peer_ip)] # Remove duplicates

    
        iprint("Get clients resulted in:", len(self.peer_ip), "Peers/Client addresses")
        return self.peer_ip
