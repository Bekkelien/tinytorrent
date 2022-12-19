import random

from enum import Enum
from pathlib import Path
from struct import pack, unpack
from urllib.parse import urlparse
from socket import socket ,inet_ntoa, gethostbyname, AF_INET, SOCK_DGRAM

# Internal 
from src.config import Config
from src.read_file import TorrentFile
from src.networking import tracker_addresses_to_array, handle_recvfrom
from src.helpers import iprint, eprint, wprint, dprint, timer

# Configuration settings
config = Config().get_config()

# msg
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

# NOTE: TODO: BUG:
# BUG: Connection is never closed
# NOTE: TODO: BUG:
class UdpTracker:
    def __init__(self, metadata, announce): 

        self.hostname = announce
        self.metadata = metadata

        # BUG; Fails if we dont have a network connection
        self.tracker_ip = gethostbyname(urlparse(self.hostname).hostname) 
        self.tracker_port = urlparse(self.hostname).port

        # Network settings UDP
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)
        self.clientSocket.settimeout(config['udp']['timeout'])
    
    #@timer
    def connect(self):

        # Send connection message
        transaction_id = random.getrandbits(32)
        message = pack('>QII', 0x41727101980, Action.connect.value , transaction_id)
        self.clientSocket.sendto(message, (self.tracker_ip, self.tracker_port)) 

        response = handle_recvfrom(self.clientSocket, config['udp']['connection_buffer'])

        if response:
            # BUG: Can fail if response is bad
            response = unpack('>IIQ',response[0])
            response_action, response_transaction_id = response[0], response[1]
            
            # Validation
            if Action.connect.value == response_action and transaction_id == response_transaction_id:
                self.connection_id = response[2]
                iprint("Connected to UDP tracker:", self.hostname) 
                return
            
        wprint("Connection to UDP tracker failed:", self.hostname)      

    #@timer
    def announce(self, event):
        key = random.getrandbits(32)
        transaction_id = random.getrandbits(32)
        message = pack('>QII20s20sQQQIIIih',self.connection_id,
                                            Action.announce.value,
                                            transaction_id,
                                            self.metadata['info_hash'], 
                                            config['client']['peer_id'].encode(),
                                            self.metadata['downloaded'],                  # Downloaded bytes for this session
                                            self.metadata['left'],                  # Bytes left to downloaded 
                                            self.metadata['uploaded'],                  # Uploaded in bytes for this session
                                            event,  
                                            0,                  # Sender IP address - 0 = Default
                                            key,    
                                            -1,                 # n clients, -1 [Spec says 74 is max but i get more than this] 
                                            self.tracker_port)  # 98 Bytes

        # Send announce message
        self.clientSocket.sendto(message, (self.tracker_ip, self.tracker_port)) 
        
        # NOTE: Should we check client peer_id? no? since we do in handshake?
        response = handle_recvfrom(self.clientSocket, config['udp']['announce_buffer'])

        if response:
            # BUG: Can fail if response is bad
            message = unpack('>IIIII',response[0][0:20])
            response_action, response_transaction_id = message[0], message[1]

        # Validation
        if Action.announce.value == response_action and transaction_id == response_transaction_id:
            interval, leechers, seeders = message[2], message[3], message[4]
           
            client_addresses = tracker_addresses_to_array(response[0][20:]) #TODO: response better naming?
            if client_addresses:  
                iprint("Announce accepted, re-announce interval:", interval, "leechers:", leechers, "seeders:" ,seeders, network='inn')
                return client_addresses

        # Handle this
        wprint("Announce response failure")

    #@timer
    def scrape(self):
        transaction_id = random.getrandbits(32)
        message = pack('>QII20s', self.connection_id, Action.scrape.value, transaction_id, self.metadata['info_hash'])
        
        # Send scraping message
        self.clientSocket.sendto(message, (self.tracker_ip, self.tracker_port)) 
        
        response = handle_recvfrom(self.clientSocket, config['udp']['scraping_buffer'])

        if response:
            # BUG: Can fail if response is bad
            message = unpack('>IIIII',response[0])
            response_action, response_transaction_id = message[0], message[1]
            
            # Validation
            if Action.scrape.value == response_action and transaction_id == response_transaction_id:
                completed, downloaded, incomplete = message[2], message[3], message[4]
                iprint("Scraping completed, torrent:", self.metadata['name'], "completed:", completed, "downloaded", downloaded, "incomplete" ,incomplete)

        wprint("Tracker scraping failure")


if __name__ == '__main__':
    """ TESTING TESTING TESTING TESTING TESTING TESTING TESTING TESTING """

    PATH = Path('./src/files/')
    files = ['tails.torrent','ChiaSetup-1.6.1.exe.torrent','big-buck-bunny.torrent','tears-of-steel.torrent']

    for file in files:
        file = TorrentFile(PATH / file)

        torrent, info_hash = file.read_torrent_file()

        # TODO: Fix this for list as well 
        try:
            if 'udp' in torrent['announce']:
                udp_connection = UdpTracker(torrent, info_hash)
                udp_connection.connect() 
                client_addresses = udp_connection.announce(EventUdp.none.value) 
                udp_connection.scrape()
                #dprint("Client Addresses:", client_addresses[0:5])

        except Exception as e:
            eprint("TEMP HAX HANDLER:", e)

            