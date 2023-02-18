from src.networking import parse_tracker_peers_ip

def test_tracker_addresses_to_array():
    payload_addresses = b'\xfe\xff\x00\x00\x4f\x4f' \
                      + b'\x4e\xff\xfe\xff\x00\x00' 
                      # ['254.255.0.0', 20303] -> Valid 
                      # ['78.255.254.255', 0]] -> Invalid

    client_addresses = parse_tracker_peers_ip(payload_addresses)
    assert client_addresses == [['254.255.0.0', 20303]]


