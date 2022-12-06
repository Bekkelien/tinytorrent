import requests

from struct import unpack
from socket import inet_ntoa

# Internals 
from src.config import Config
from src.helpers import iprint, eprint, wprint

# Configuration settings
config = Config().get_config()


# Make only for http requests? may be to generic else
def get_request(url, params, message='None'):
    """ Returns content from a get request"""
    try:
        response = requests.get(url, params=params, timeout=config['http']['timeout'])
        if response.status_code != 200:
            wprint("Request:", message, "failed with status code:", response.status_code)
            return False

        if 'failure' in str(response.content): # TODO: warning message handling of these as well
            wprint("Response:", message, "failure, reason:", response.content)
            return False    

        return response.content

    except requests.exceptions.HTTPError as errh:
        eprint ("Request Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        eprint ("Request Connection Error:", errc)
    except requests.exceptions.Timeout as errt:
        eprint ("Request Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        eprint ("Request critical error:", err)
    
    return False


# TODO: rename function  to something good (Make more generic?)
# @timer Fast enough 
def tracker_addresses_to_array(payload_addresses, split=6):
    """ hex -> 2D list of addresses """
    # TODO: Add support for IPv6 addresses
    
    response_length = len(payload_addresses)

    if response_length < split:
        wprint("No peers available, or failed to get addresses")
        return False

    if response_length % split != 0:
        wprint("Tracker responded with unsupported length of:", response_length,"needs to be in 6 bytes increments")
        return False

    peers = int(response_length/split)

    client_addresses = []
    for index in range(0,response_length,split):
        ip = inet_ntoa(payload_addresses[index:index+4])            # IP   4 Bytes # NOTE: will fail if ip is not valid?
        port = unpack("!H", payload_addresses[index+4:index+6])[0]  # Port 2 Bytes
        if port > 1024 and port <= 65535:
            client_addresses.append([ip,port])
    
    # NOTE: Typically tracker respond with this clients address as well to peers-1 is ok or even expected when announce or scrape after first time 
    iprint("Tracker responded with:", len(client_addresses), "peers with valid ip/port combination of total:", peers ,"peers")
    return client_addresses

#if __name__ == '__main__':
#   tracker_addresses_to_array(payload_addresses)