import pytest

from src.networking import tracker_addresses_to_array

def test_tracker_addresses_to_array(payload_addresses = b'\ff\xff\xff\xff\x4f\ff\xff\x01\xff\x4e\ff\xfe\xff\x00\x00'):
    client_addresses = tracker_addresses_to_array(payload_addresses)
    print(client_addresses)