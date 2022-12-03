from struct import pack, unpack
from socket import socket ,inet_ntoa, gethostbyname, AF_INET, SOCK_DGRAM

from helpers import iprint, eprint, wprint, dprint, timer

# TODO: rename function  to something good 
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