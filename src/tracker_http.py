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

# TODO: ADD INN SUPPORT FOR stats downloaded uploaded ++ (None or 0)
class HttpTracker:
    def __init__(self, metadata, announce):
        self.metadata = metadata
        self.complete = None
        self.incomplete = None
        self.interval = None
        self.peers = b'' # TODO: RENAME
        self.hostname = announce
        self.announce_response = None
        
        self.content = None # TODO: Better name

    def announce(self, event, port=6881, compact=1):

        params = {  'info_hash': self.metadata['info_hash'],
                    'peer_id': config['client']['peer_id'], 
                    'uploaded': self.metadata['uploaded'],               
                    'downloaded': self.metadata['downloaded'],              
                    'port': port, 
                    'left': self.metadata['left'],             
                    'compact': compact,
                    #'no_peer_id': 0,
                    'event': event,
                    #'numwant': 50,
                    #'key': 'asdsa24324'    # Important FOR SOME TRACKERS!! # NOTE: FIXED? What format an gen this on startup for client user n - ? 
                 }                          # NOTE: unless fixed ? 2022-12-03 00:04:55.662889 [ERROR] Failed to get peers from tracker, reason: b'd14:failure reason87:Your client\'s "key" paramater and the key we have for you in our database do not match.e'

        self.announce_response = get_request(self.hostname, parse.urlencode(params), message="announce")

        if self.announce_response:
            iprint("Tracker HTTP/HTTPS response accepted, announce ok") 
            return True
            
        return False
        
    # Improve prints (Quite similar to scrape this is now just used for announce)
    def tracker_response(self):
        content = bdecode(self.announce_response)
        self.complete = content[b'complete'] if b'complete' in content else wprint("Tracker did not send complete response")
        self.incomplete = content[b'incomplete'] if b'incomplete' in content else wprint("Tracker did not send incomplete response")
        self.interval = content[b'interval'] if b'interval' in content else wprint("Tracker did not send interval response")
        self.peers = content[b'peers'] if b'peers' in content else wprint("Tracker did not send peers response")
        
        client_addresses = tracker_addresses_to_array(self.peers)
        
        if client_addresses:
            iprint("Tracker responded HTTP/HTTPS, complete:", self.complete, "incomplete:", self.incomplete, \
                                                            "interval:", self.interval, "peers:",len(client_addresses))
            return client_addresses

        # TODO: handel this
    

    # NOTE: This is not really important ATM, due to low tracker support and many conventions
    def scrape(self): 
        # Check if tracker supports scrape
        index_last_endpoint = self.hostname.rfind('/')
        
        if not 'announce' in self.hostname[index_last_endpoint:]:
            wprint("Tracker:", self.hostname,  "does not support scrape")
            return 
        
        # TODO: No support for tracking multiple torrents from same tracker ATM
        params= {'info_hash': self.metadata['info_hash']}

        self.scrape_response = get_request(self.hostname + '?', parse.urlencode(params), message="scrape")

        # TODO: Parse response
        if self.scrape_response:
            iprint("Tracker scrape response HTTP/HTTPS:", self.scrape_response)

        # TODO: handel this
