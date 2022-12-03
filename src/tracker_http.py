import requests

from urllib import parse
from pathlib import Path
from pprint import pprint
from struct import pack, unpack
from dataclasses import dataclass
from bencoding import bdecode, bencode 
from socket import socket ,inet_ntoa, gethostbyname, AF_INET, SOCK_DGRAM

# Internals 
from config import Config
from read_file import TorrentFile
from networking import tracker_addresses_to_array
from helpers import iprint, eprint, wprint, dprint, timer

# Configuration settings
config = Config().get_config()

@dataclass
class EventHttp():
    started = 'started'
    stopped = 'stopped'
    completed = 'completed'

# 6881-6889 Ports
# TODO: ADD INN SUPPORT FOR stats downloaded uploaded ++

class HttpTracker:
    def __init__(self, torrent, info_hash): 
        self.name = torrent['info']['name']
        self.info_hash = info_hash
        self.hostname = torrent['announce'] # Dose not support announce-list
        

    def announce(self, event, port = 6881, compact = 1):

        self.content = None # TODO: Better name

        # TODO: Implement for all ports? iterator?
        params = {
                    'info_hash': self.info_hash,
                    'peer_id': config['client']['peer_id'], # BUG: Cant be in config since should be unique 
                    'uploaded': 0,
                    'downloaded': 0,
                    'port': port, 
                    'left': 1028128,                   # BUG: GET actual number 
                    'compact': compact,
                    #'no_peer_id': 0,
                    'event': event,
                    #'numwant': 50,
                    'key': 'asdsa24324'    # Important FOR SOME TRACKERS!! # NOTE: FIXED? What format an gen this on startup for client user n - ? 
                 }                          # NOTE: unless fixed ? 2022-12-03 00:04:55.662889 [ERROR] Failed to get peers from tracker, reason: b'd14:failure reason87:Your client\'s "key" paramater and the key we have for you in our database do not match.e'

        response = requests.get(self.hostname, params=parse.urlencode(params), timeout=config['http']['timeout'])

        if response.status_code == 200: # REFACTOR
            if 'failure' in str(response.content): # NOTE: Not an insane good solution, TODO: warning message handling of these as well
                eprint("Failed to get peers from tracker: ", response.content)
            
            else:
                iprint("Tracker HTTP/HTTPS response accepted") # Make more error stuff
                self.content = response.content
                return True

        else:
            eprint("Failed to get peers from tracker with status code:", response.status_code)
        
        return False
    
    #content TODO: Rename
    # Improve prints
    def tracker_response(self):
        # Wrong place to set it?
        # Default's
        self.complete = None
        self.incomplete = None
        self.interval = None
        self.peers = b'' # TODO: RENAME

        content = bdecode(self.content)
        self.complete = content[b'complete'] if b'complete' in content else wprint("Tracker did not send complete response")
        self.incomplete = content[b'incomplete'] if b'incomplete' in content else wprint("Tracker did not send incomplete response")
        self.interval = content[b'interval'] if b'interval' in content else wprint("Tracker did not send interval response")
        self.peers = content[b'peers'] if b'peers' in content else wprint("Tracker did not send peers response")
        
        client_addresses = tracker_addresses_to_array(self.peers)
        
        if client_addresses:
            iprint("Tracker responded HTTP/HTTPS, complete:", self.complete, "incomplete:", self.incomplete, \
                                                            "interval:", self.interval, "peers:",len(client_addresses))
            return client_addresses

        # handel this
    
    def scrape(self): 
        # This adds more or less just total downloaded and reduce bandwidth of tracker
        # but seems to have low support or many conventions? 
        
        # Check if tracker supports scrape
        index_last_endpoint = self.hostname.rfind('/')
        
        if not 'announce' in self.hostname[index_last_endpoint:]:
            wprint("Tracker:", self.hostname,  "does not support scrape")
            return 
        
        # NOTE: Can be used for multiple torrents from same tracker: ?info_hash=aa&info_hash=bb&info_hash=cc
        # Currently only support for one
        params= {
                'info_hash': self.info_hash,             
                 }
        #response = requests.get(self.hostname, params=parse.urlencode(params), timeout=config['http']['timeout'])
        response = requests.get(self.hostname + '?', params= parse.urlencode(params), timeout=config['http']['timeout'])
        dprint(self.hostname + '?' + parse.urlencode(params))
        
        if response.status_code != 200:
            wprint("Failed to scrape from tracker:", self.hostname)
            return
        
        if 'failure' in str(response.content):
            wprint("Failed to scrape from tracker:", self.hostname, "reason:", response.content)
            return
        
        # NOTE: Assuming we are good here but we can be here with bad response
        # Add handling 
        iprint(bdecode(response.content))




#b"d8:intervali1800e12:min intervali300e5:peers84:K!\x9f\x1b\xc8\xd5.'\xff\xebl\x8cXY\x08\xfe\x1a\xe1[2_\xd4\x81\xaa\\\xbak\x05\xea\xaaU\xdd\x83\xf0-\xec.'\xff\xebl\x8cXY\x08\xfe\x1a\xe1zn\x87\xa7\xff\xdeXY\x08\xfe\x1a\xe1XY\x08\xfe\x1a\xe1Q3\xb0\xb9\xcd\x05\x18\x14\x1a\xa7\xc4\xebK!\x9f\x1b\xc8\xd510:tracker id5:84822e"

# BUG UBUNTU dose not give many or any peers back!
if __name__ == '__main__':
    """ TESTING TESTING TESTING TESTING TESTING TESTING TESTING TESTING """

    PATH = Path('./src/files/')
    files = ['kalilinux.torrent', 'ubuntu.torrent', 'altlinux.torrent', 'slackware.torrent']
    #files = [ 'ubuntu.torrent', 'altlinux.torrent', 'slackware.torrent']
    

    for file in files:
        file = TorrentFile(PATH / file)
        torrent, info_hash = file.read_torrent_file()

        # TODO: Fix this for list as well 
        if any(protocol in torrent['announce'] for protocol in ['http', 'https']):
            trackers = HttpTracker(torrent, info_hash)
            if trackers.announce(EventHttp.started):
                client_addresses = trackers.tracker_response()
                trackers.scrape()
            
