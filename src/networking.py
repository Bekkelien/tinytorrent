import requests
import socket

from struct import unpack
from typing import Optional, Tuple, Union

# Internals 
from src.protocol import MessageType
from src.config import Config
from src.helpers import iprint, eprint, wprint

# Configuration settings
config = Config().get_config()


# Make only for http requests? may be to generic else
def http_tracker_requests(url, params, message='None') -> list:
    """ Returns content from a get request """
    try:
        response = requests.get(url, params=params, timeout=config['http']['timeout'])
        if response.status_code == 200:
            return response.content

        else:
            wprint("Request:", message, "failed with status code:", response.status_code)
            return []    

    except requests.exceptions.HTTPError as errh: eprint("Request Http Error:", errh)
    except requests.exceptions.ConnectionError as errc: eprint("Request Connection Error:", errc)
    except requests.exceptions.Timeout as errt: eprint("Request Timeout Error:", errt)
    except requests.exceptions.RequestException as err: eprint("Request critical error:", err)
    
    return []

def http_tracker_response_verify(response) -> list:
    """ Takes a inn a tracker announce response and verifies that the tracker response is correct """
    if response:
        if b'failure' in response:
            wprint("Tracker HTTP announce response failed with reason:", response) 
            return []

        elif b'warning' in response:
            wprint("Tracker HTTP announce response warning:", response)  
            return []
    
    return response
    
def udp_tracker_response(clientSocket, buffer) -> list:
    """ Response handler for UDP tracker responses """
    try:
        # Attempt to receive data from the socket
        response = clientSocket.recvfrom(buffer) # NOTE: Why are we using recvfrom here?
        return response

    except socket.timeout: wprint("UDP tracker timeout -> No response received")
    except socket.error as esock: eprint("Socket error occurred in UDP tracker response:", esock)

    return []


# TODO: rename function  to something good (Make more generic?)
# @timer Fast enough 
def parse_tracker_peers_ip(payload_addresses, split=6):
    """ hex -> 2D list of addresses """

    # TODO: Add support for IPv6 addresses
    
    if not payload_addresses: return []

    response_length = len(payload_addresses)

    if response_length < split:
        wprint("No peers available, or failed to get addresses")
        return [] 

    if response_length % split != 0:
        wprint("Tracker responded with unsupported length of:", response_length,"needs to be in 6 bytes increments")
        return [] 

    peers = int(response_length/split)

    peer_ip = []
    for index in range(0,response_length,split):
        ip = socket.inet_ntoa(payload_addresses[index:index+4])            # IP   4 Bytes # NOTE: will fail if ip is not valid?
        port = unpack("!H", payload_addresses[index+4:index+6])[0]  # Port 2 Bytes
        if port > 1024 and port <= 65535:
            peer_ip.append([ip,port])

    # NOTE: Typically tracker respond with this clients address as well to peers-1 is ok or even expected when announce or scrape after first time 
    iprint("Tracker responded with:", len(peer_ip), "peers with valid ip/port combination of total:", peers ,"peers")
    return peer_ip




"""

import ipaddress

def is_valid_ipv6(ip_str):

  try:

    ip = ipaddress.IPv6Address(ip_str)

    return True

  except ValueError:

    return False

>>> is_valid_ipv6('2001:0db8:85a3:0000:0000:8a2e:0370:7334')
True
>>> is_valid_ipv6('2001:db8:85a3:0:0:8a2e:370:7334')
True
>>> is_valid_ipv6('2001:db8:85a3::8a2e:370:7334')
True
>>> is_valid_ipv6('2001:0db8:85a3:0000:0000:8a2e:0370:7334:1234')
False
>>> is_valid_ipv6('192.168.0.1')
False

"""
#if __name__ == '__main__':
#   tracker_addresses_to_array(payload_addresses)