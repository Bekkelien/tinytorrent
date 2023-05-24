from pathlib import Path

# Internals
from src.config import Config
from src.read_torrent import TorrentFile
from src.manager import TrackerManager
from src.protocol import PeerWire, PeerManager
from src.download import Download
from src.storage import StoreDownload
from src.helpers import iprint, dprint, pprint

# Configuration settings
config = Config().get_config()

if __name__ == '__main__':
    iprint("Starting TinyTorrent client with peer id:", config['client']['peer_id'])

    PATH = Path('./src/files/')
    #files = ['gimp.torrent','tails.torrent', 'ubuntu.torrent','single.torrent','slackware.torrent', 'kalilinux.torrent','altlinux.torrent', 'wired-cd.torrent']
    files = ['gimp.torrent']

    for file in files:
        metadata = TorrentFile(PATH / file).read()
        
        ### Get peers IP addresses ### NOTE:: We only get peers when program starts ATM
        tracker = TrackerManager(metadata)
        peer_ips = tracker.get_clients()
        #dprint(peer_ips)

        ### Object for one peer_wire connection ATM
        peer_wire = PeerWire(metadata)

        # Object for one download ATM
        download = Download(metadata) 

        data = b''

        ASYNC = False # Does not connect properly to peers it seems and more bugs and stuff
        if ASYNC:
            import asyncio
            from async_peerwire_testing import Handshake
        while True:
            if ASYNC: peers = asyncio.run(Handshake(metadata).run(peer_ips))
            else:
                peers = []
                # Create a func from this
                for index, _ in enumerate(peer_ips, start=0):
                    iprint("TEST CONNECTION:", index, color='blue')
                #TODO: We are doing handshake every time ATM 
                    peer = peer_wire.handshake(peer_ips, index)
                    if peer:
                        peers.append(peer)
                        if len(peers) == 10: 
                            break
            
            # Move out of here at some points
            peers = PeerManager.rank_peers(peers)

            # END LINEAR
            pprint(peers)

            for peer in peers: #(Only one iteration for testing now)
            #current_peer = peer_wire.handshake(peer_ips, index)

                current_peer = peer[0] # Socket
                state = True
                # Jumps peer for each piece 
                while state: # Hax to avoid jumpig for each piece
                    piece_data, flag = download.linear_download_piece(current_peer) 
                    
                    if piece_data:
                        data = data + piece_data

                    else:
                        state = False
            
                    if flag:
                        StoreDownload(metadata).save(data)
                        iprint("Download success, what a time to be alive ")
                        raise NotImplementedError

