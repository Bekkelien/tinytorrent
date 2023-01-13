import random
import socket 

from enum import Enum
from struct import pack, unpack
from urllib.parse import urlparse

# Internal 
from src.config import Config
from src.read_file import TorrentFile
from src.networking import parse_tracker_peers_ip, udp_tracker_response
from src.helpers import iprint, eprint, wprint, dprint, timer

# Configuration settings
config = Config().get_config()

class Action(Enum):
    connect = 0
    announce = 1
    scrape = 2 
    error = 3

class EventUdp(Enum):
    none = 0
    completed = 1
    started = 2
    stopped = 3

class UdpTracker:
    def __init__(self, metadata, announce): 

        self.hostname = announce
        self.metadata = metadata
        self.client_addresses = []

        try:
            self.tracker_ip = socket.gethostbyname(urlparse(self.hostname).hostname) 
            self.tracker_port = urlparse(self.hostname).port
        
        # TODO: Terminate if we lost connection to network, improve solution 
        except Exception as sockerr:
            eprint("UDP Tracker network error:",sockerr)
            eprint("Terminating TinyTorrent")
            raise SystemExit

        # Network settings UDP
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clientSocket.settimeout(config['udp']['timeout'])
    
    #@timer
    def connect(self) -> bool:

        # Send connection message
        transaction_id = random.getrandbits(32)
        message = pack('>QII', 0x41727101980, Action.connect.value , transaction_id)
        self.clientSocket.sendto(message, (self.tracker_ip, self.tracker_port)) 

        response = udp_tracker_response(self.clientSocket, config['udp']['connection_buffer'])

        # NOTE: create a better error message?
        if response and len(response[0]) == 16 and response[1] == (self.tracker_ip, self.tracker_port):
            response = unpack('>IIQ',response[0])
            response_action, response_transaction_id = response[0], response[1]
            
            # Validation
            if Action.connect.value == response_action and transaction_id == response_transaction_id:
                self.connection_id = response[2]
                iprint("Connected to UDP tracker:", self.hostname) 
                return True
            
        wprint("Connection to UDP tracker failed:", self.hostname)  
        return False    

    #@timer
    def announce(self, event):
        transaction_id = random.getrandbits(32)
        message = pack('>QII20s20sQQQIIIih',self.connection_id,
                                            Action.announce.value,
                                            transaction_id,
                                            self.metadata['info_hash'], 
                                            config['client']['peer_id'].encode(),
                                            self.metadata['downloaded'],                
                                            self.metadata['left'],               
                                            self.metadata['uploaded'],             
                                            event,  
                                            0,                          # Sender IP address - 0 = Default
                                            random.getrandbits(32),    
                                            -1,                         # n clients, -1 [Spec says 74 is max but i get more than this] 
                                            self.tracker_port)          # 98 Total Bytes

        # Send announce message
        self.clientSocket.sendto(message, (self.tracker_ip, self.tracker_port)) 
        
        response = udp_tracker_response(self.clientSocket, config['udp']['announce_buffer'])

        # 20 |---->>> according to chat.gpt 
        if response and len(response[0]) >= 20 and response[1] == (self.tracker_ip, self.tracker_port):
            message = unpack('>IIIII',response[0][0:20])
            response_action, response_transaction_id = message[0], message[1]

            # Validation
            if Action.announce.value == response_action and transaction_id == response_transaction_id:
                interval, leechers, seeders = message[2], message[3], message[4]
            
                self.client_addresses = parse_tracker_peers_ip(response[0][20:])

                if self.client_addresses:  
                    iprint("UDP Tracker announce accepted, re-announce interval:", interval, "leechers:", leechers, "seeders:" ,seeders)
                    return self.client_addresses
                
                else: self.client_addresses = [] 

        wprint("UDP Tracker announce response failure")
        return self.client_addresses

    #@timer
    def scrape(self):
        transaction_id = random.getrandbits(32)
        message = pack('>QII20s', self.connection_id, Action.scrape.value, transaction_id, self.metadata['info_hash'])
        
        # Send scraping message
        self.clientSocket.sendto(message, (self.tracker_ip, self.tracker_port)) 
        
        response = udp_tracker_response(self.clientSocket, config['udp']['scraping_buffer'])

        if response and len(response[0]) == 16 and response[1] == (self.tracker_ip, self.tracker_port):
            message = unpack('>IIIII',response[0])
            response_action, response_transaction_id = message[0], message[1]
            
            # Validation
            if Action.scrape.value == response_action and transaction_id == response_transaction_id:
                completed, downloaded, incomplete = message[2], message[3], message[4]
                iprint("Scraping completed, torrent:", self.metadata['name'], "completed:", completed, "downloaded", downloaded, "incomplete" ,incomplete)

        wprint("Tracker scraping failure")

    # NOTE: Dangerous since we need to call the close function
    def close(self):
        self.clientSocket.close()