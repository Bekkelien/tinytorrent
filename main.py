import psutil

from pathlib import Path

# Internal s
from src.config import Config
from src.read_torrent import TorrentFile
from src.manager import TrackerManager
from src.protocol import PeerWire
from src.download import Download
from src.storage import StoreDownload
from src.helpers import iprint, dprint, pprint

# Configuration settings
config = Config().get_config()

if __name__ == '__main__':
    iprint("Starting TinyTorrent client with peer id:", config['client']['peer_id'])

    PATH = Path('./src/files/')
    #files = ['pi-lite.torrent', 'gimp.torrent','tails.torrent', 'ubuntu.torrent','single.torrent','slackware.torrent', 'kalilinux.torrent','altlinux.torrent', 'wired-cd.torrent']
    #files = ['gimp.torrent']
    files = ['pi-lite.torrent']
    #files = ['ChiaSetup-1.8.1.exe.torrent']
    
    for file in files:
        metadata = TorrentFile(PATH / file).read()

        data = b''

        ASYNC = False # Does not connect properly to peers it seems and more bugs and stuff
        if ASYNC:
            import asyncio
            from async_peerwire_testing import Handshake
        while True:
            tracker = TrackerManager(metadata)
            peer_addresses = tracker.get_clients()

            if ASYNC: peers = asyncio.run(Handshake(metadata).run(peer_addresses))
            else:
                #TODO: We are doing handshake every time ATM 
                peer_addresses_connected = PeerWire(metadata, peer_addresses).connect()

                # TEST
                #print(psutil.net_connections())
                DOWNLOAD = True
                if DOWNLOAD:
                    if peer_addresses_connected:
                        for peer in peer_addresses_connected:
                        #peers.append(peer)

                        # Trying to download as soon as connected 
                        #for peer in peers: #(Only one iteration for testing now)
                        #current_peer = peer_wire.handshake(peer_ips, index)

                            client_socket = peer[0] # Socket
                            state = True
                            # Jumps peer for each piece 
                            while state: # Hax to avoid for each piece
                                piece_data, flag = Download(metadata, client_socket).linear_download_piece() 
                                if piece_data:  
                                    data = data + piece_data

                                else:
                                    state = False

                                if flag:
                                    StoreDownload(metadata).save(data)
                                    iprint("Download success, what a time to be alive ")
                                    raise NotImplementedError

                        #if len(peers) == 10: 
                        #   break
            
            # Move out of here at some points
            #peers = PeerManager.rank_peers(peers)

            # END LINEAR
            #pprint(peers)


