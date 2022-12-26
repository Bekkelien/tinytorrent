from urllib import parse
from bencoding import bdecode
from dataclasses import dataclass

# Internals 
from src.config import Config
from src.helpers import iprint, eprint, wprint, dprint
from src.networking import tracker_addresses_to_array, get_request

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
        self.peers = b'' # TODO: RENAME
        self.hostname = announce
        self.announce_response = None
        self.client_addresses = b''

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

        self.announce_response = get_request(self.hostname, parse.urlencode(params), message="announce")

        if self.announce_response:
            if b'failure' in self.announce_response:
                wprint("Tracker HTTP announce response failed with reason:", self.announce_response) 
                return self.client_addresses

            elif b'warning' in self.announce_response:
                wprint("Tracker HTTP announce response warning:", self.announce_response)  
                return self.client_addresses

            iprint("Tracker HTTP announce response accepted") 
            self.client_addresses = TrackerConnectionHttp._tracker_response(self)

            if self.client_addresses:
                iprint("Tracker responded HTTP/HTTPS, complete:", self.complete, "incomplete:", self.incomplete, \
                                                        "interval:", self.interval, "peers:",len(self.client_addresses))
                return self.client_addresses
        
        wprint("Tracker HTTP announce failed")
        return self.client_addresses
        
    def _tracker_response(self):
        """ Parse tracker response if tracker responds to the announce request"""

        temp = bdecode(self.announce_response)
        self.complete = temp[b'complete'] if b'complete' in temp else wprint("Tracker did not send complete response")
        self.incomplete = temp[b'incomplete'] if b'incomplete' in temp else wprint("Tracker did not send incomplete response")
        self.interval = temp[b'interval'] if b'interval' in temp else wprint("Tracker did not send interval response")
        self.peers = temp[b'peers'] if b'peers' in temp else wprint("Tracker did not send peers response")
        
        # Convert to ip and ports
        client_addresses = tracker_addresses_to_array(self.peers)

        return client_addresses
        

    # NOTE: Does really not do "anything"
    def scrape(self): 

        iprint("Tracker HTTP scraping")

        index_last_endpoint = self.hostname.rfind('/')
        
        if not 'announce' in self.hostname[index_last_endpoint:]:
            wprint("Tracker HTTP scrape not supported for:", self.hostname)
            return 
        
        # NOTE: Single tracker supports only
        params= {'info_hash': self.metadata['info_hash']}

        self.scrape_response = get_request(self.hostname + '?', parse.urlencode(params), message="scrape")

        # TODO: Parse response
        if self.scrape_response:
            iprint("Tracker scrape response HTTP/HTTPS:", self.scrape_response)
            return

        wprint("Tracker HTTP scraping failure:", self.scrape_response)
