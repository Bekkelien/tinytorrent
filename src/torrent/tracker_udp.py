import random

from enum import Enum
from pathlib import Path
from struct import pack, unpack
from urllib.parse import urlparse
from socket import socket ,inet_ntoa, gethostbyname, AF_INET, SOCK_DGRAM

# Internal 
from config import Config
from read_file import TorrentFile
from tcp import PeerWire
from helpers import iprint, eprint, wprint, dprint, timer

# Configuration settings
config = Config().get_config()

# msg
class Action(Enum):
    connect = 0
    announce = 1
    scrape = 2 
    error = 3

class Event(Enum):
    none = 0
    completed = 1
    started = 2
    stopped = 3

class UdpTracker:
    def __init__(self, torrent, info_hash): 

        self.name = torrent['info']['name']
        self.info_hash = info_hash
        self.hostname = torrent['announce'] # Dose not support announce-list
        self.tracker_ip = gethostbyname(urlparse(self.hostname).hostname) 
        self.tracker_port = urlparse(self.hostname).port
        print(self.tracker_ip, self.tracker_port)

        # Network settings UDP
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)
        self.clientSocket.settimeout(config['udp']['timeout'])
    
    #@timer
    def connect(self):

        # Send connection message
        transaction_id = random.getrandbits(32)
        message = pack('>QII', 0x41727101980, Action.connect.value , transaction_id)
        self.clientSocket.sendto(message, (self.tracker_ip, self.tracker_port)) 

        # Response NOTE: Can fail
        response = self.clientSocket.recvfrom(config['udp']['connection_buffer'])
        response = unpack('>IIQ',response[0])
        response_action, response_transaction_id = response[0], response[1]
        
        # Validation
        if Action.connect.value == response_action and transaction_id == response_transaction_id:
            self.connection_id = response[2]
            iprint("Connected to UDP tracker:", self.hostname) 
            
        else:
            wprint("Connection to UDP tracker failed:", self.hostname)      

    #@timer
    def announce(self, event):
        key = random.getrandbits(32)
        transaction_id = random.getrandbits(32)
        message = pack('>QII20s20sQQQIIIih',self.connection_id,
                                            Action.announce.value,
                                            transaction_id,
                                            self.info_hash, 
                                            config['client']['peer_id'].encode(),
                                            0,                  # Downloaded bytes for this session
                                            0,                  # Bytes left to downloaded 
                                            0,                  # Uploaded in bytes for this session
                                            event,  
                                            0,                  # Sender IP address - 0 = Default
                                            key,    
                                            -1,                 # n clients, -1 = max = 74 
                                            self.tracker_port)  # 98 Bytes

        # Send announce message
        self.clientSocket.sendto(message, (self.tracker_ip, self.tracker_port)) 
        
        # Response NOTE: Can fail
        # NOTE: Should we check client peer_id? no? since we do in handshake?
        response = self.clientSocket.recvfrom(config['udp']['announce_buffer'])
        message = unpack('>IIIII',response[0][0:20])
        response_action, response_transaction_id = message[0], message[1]

        # Validation
        if Action.announce.value == response_action and transaction_id == response_transaction_id:
            interval, leechers, seeders = message[2], message[3], message[4]

            # Client IP's and Port's 
            client_addresses = []
            message = response[0][20:]             
            for index in range(6,len(message),6):
                ip = inet_ntoa(message[index-6:index-2])        # IP 4 Bytes
                port = unpack("!H", message[index-2:index])[0]  # Port 2 Bytes
                tracker_address = [ip,port]
                client_addresses.append(tracker_address)    

            iprint("Announce accepted, re-announce interval:", interval, "leechers:", leechers, "seeders:" ,seeders)
            return client_addresses

        else:
            wprint("Announce response failure")

    #@timer
    def scraping(self):
        transaction_id = random.getrandbits(32)
        message = pack('>QII20s', self.connection_id, Action.scrape.value, transaction_id, self.info_hash)
        
        # Send scraping message
        self.clientSocket.sendto(message, (self.tracker_ip, self.tracker_port)) 
        
        # Response NOTE: Can fail
        response = self.clientSocket.recvfrom(config['udp']['scraping_buffer'])
        message = unpack('>IIIII',response[0])
        response_action, response_transaction_id = message[0], message[1]
        
        # Validation
        if Action.scrape.value == response_action and transaction_id == response_transaction_id:
            completed, downloaded, incomplete = message[2], message[3], message[4]
            iprint("Scraping completed, torrent:", self.name, "completed:", completed, "downloaded", downloaded, "incomplete" ,incomplete)

        else:
            wprint("Tracker scraping failure")


if __name__ == '__main__':

    """ TESTING TESTING TESTING TESTING TESTING TESTING TESTING TESTING """

    PATH = Path('./src/files/')
    files = ['tails.torrent','ChiaSetup-1.6.1.exe.torrent','ubuntu.torrent','big-buck-bunny.torrent']

    for file in files:
        file = TorrentFile(PATH / file)

        torrent, info_hash = file.read_torrent_file()

        # TODO: Fix this for list as well 
        if 'udp' in torrent['announce']:
            udp_connection = UdpTracker(torrent, info_hash)
            udp_connection.connect() 
            client_addresses = udp_connection.announce(Event.none.value) 
            udp_connection.scraping()
            dprint("Client Addresses:", client_addresses[0:5])
