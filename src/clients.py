import json

from dataclasses import dataclass

# Internals
from src.helpers import wprint, iprint, dprint, eprint

@dataclass
class Extensions:
    fast_extensions = b'\x04' # Not implemented
    exception_protocol = 16 # == b'\x10'== BEP 10

class Client:
    def __init__(self) -> None:
        self.clients = json.load(open('./src/clients.json')) # Cache this?
        #print(self.clients.keys())

    def software(self, peer_identifier: bytes) -> str:
        peer_identifier = peer_identifier.decode("utf-8", "ignore")
        if len(peer_identifier) > 8:
            if peer_identifier[1:3] in self.clients.keys():
                name = self.clients[peer_identifier[1:3]]
                version = peer_identifier[3:7]
                id = peer_identifier[8:]
                iprint("Client:", name, "version:", version, "id:", id)
                return name
        
        # TODO: implement flag to disconnect this peer if invalid message
        wprint("Unknown client software:", peer_identifier)

    def extensions(self, reserved): # TODO
        if reserved[5]  == Extensions.exception_protocol:
            iprint("Peer support extension protocol: BEP 10 - Extension Protocol for Peers to Send Arbitrary Data")