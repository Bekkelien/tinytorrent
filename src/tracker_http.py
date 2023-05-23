from urllib import parse
from bencoding import bdecode
from dataclasses import dataclass

# Internals 
from src.config import Config
from src.helpers import iprint, eprint, wprint, dprint
from src.networking import parse_tracker_peers_ip, http_tracker_requests, http_tracker_response_verify

# Configuration settings
config = Config().get_config()

@dataclass
class EventHttp():
    started = 'started'
    stopped = 'stopped'
    completed = 'completed'

class TrackerConnectionHttp:
    def __init__(self, metadata, announce):
        self.metadata = metadata

        self.complete = None
        self.incomplete = None
        self.interval = None
        self.peers = b'' 
        self.hostname = announce

    def announce(self, event):

        params = {  'info_hash': self.metadata['info_hash'],
                    'peer_id': config['client']['peer_id'], 
                    'uploaded': self.metadata['uploaded'],               
                    'downloaded': self.metadata['downloaded'],              
                    'port': config['http']['port'], 
                    'left': self.metadata['left'],             
                    'compact': config['http']['compact'],
                #   'no_peer_id': 0,   older version, compact is now used instead
                    'event': event,
                    'numwant': config['http']['numwant'],
                    'key': config['client']['key']  
                 }


        response = http_tracker_requests(self.hostname, parse.urlencode(params), message="announce")
        response = http_tracker_response_verify(response)

        if response:
            return TrackerConnectionHttp._http_parse_response(self, response)
        
        else:
            wprint("Tracker HTTP announce, could not find any peers from tracker:", self.hostname)
            return []
        
    def _http_parse_response(self, response):
        """ Parse tracker response if tracker responds to the announce request"""

        try:
            temp = bdecode(response)

            # Parse the tracker OrderedDict response
            self.complete = temp[b'complete'] if b'complete' in temp else wprint("Tracker did not send complete response")
            self.incomplete = temp[b'incomplete'] if b'incomplete' in temp else wprint("Tracker did not send incomplete response")
            self.interval = temp[b'interval'] if b'interval' in temp else wprint("Tracker did not send interval response")
            self.peers = temp[b'peers'] if b'peers' in temp else wprint("Tracker did not send peers response")
            
            peer_ip_addresses = parse_tracker_peers_ip(self.peers)
            iprint("HTTP Announce OK, complete:", self.complete, "incomplete:", self.incomplete, "interval:", self.interval, "peers:", len(peer_ip_addresses))

            return peer_ip_addresses

        except Exception as e: #TODO::
            wprint("Cant parse http tracker response:", e)

    # NOTE: This function is not implemented fully yet
    def scrape(self): 

        iprint("Tracker HTTP scraping")

        index_last_endpoint = self.hostname.rfind('/')
        
        if not 'announce' in self.hostname[index_last_endpoint:]:
            wprint("Tracker HTTP scrape not supported for:", self.hostname)
            return 
        
        # NOTE: Single tracker supports only
        params= {'info_hash': self.metadata['info_hash']}

        self.scrape_response = http_tracker_requests(self.hostname + '?', parse.urlencode(params), message="scrape")

        # TODO: Parse response
        if self.scrape_response:
            iprint("Tracker scrape response HTTP/HTTPS:", self.scrape_response)
            return

        wprint("Tracker HTTP scraping failure:", self.scrape_response)
