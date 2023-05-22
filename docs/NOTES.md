
#### Clients (Handshake-Bitfield-unchoke) state:
```console
qBittorrent -> OK response
BBtor -> unknown bitfield, but does unchoke 
BitWombat -> unknown bitfield, but does unchoke
DelugeTorrent -> unknown bitfield, but does unchoke
µTorrent Web -> unknown bitfield, but does unchoke 
µTorrent -> Peer responded with unknown message ID after handshake, but does unchoke
Transmission -> Bitfield ok, but returns choke
b'FD63YQuRdqcfgiHPVKhr' What is this client?
b'MG-3.01.4276BOSmDjLj' What is this client? -> unknown bitfield, but does unchoke 
b'TIX0314-e9e8f3i0g3d0' What is this client? -> No bitfield?
```
```console
## TIP's'
#### Top priority:
- [ ] Handle TCP connection timeout make a generic function for connections? to avoud TimeoutError: timed out and other socket errors 

#### Needs to be implemented
- [ ] Create a logo for tinytorrent
- [ ] In read_file -> if b'files' in self.data[b'info']: # BUG if single name filename is files
- [ ] Implementation of tracking of how much data downloaded this session
- [ ] Should we verify unknown trackers response ATM and download for it, try to download from known clients in testing period
- [ ] Handle pice length for a torrent file 
- [ ] Rename sending messages name currently: message 
- [ ] Socket tracking is now a mess
- [ ] Documentation of functions and classes
- [ ] To many dependencies from a to b and c and over back into d ++
- [ ] Create many tests? - pytest
- [ ] Add type hints? 
- [ ] Map peers and what state they are in 
- [ ] Should peer id be one for en run if software or change each time?
- [ ] How to validate a tracker when using HTTP/HTTPS? or not?
- [ ] Create verification of a content of a torrent file 
- [ ] The way it is structured now makes it hard to break out of a state if the tracker does not respond with proper responses
- [ ] Add symbol if network data is going out or inn in print functions <---------- inn   out ------------>
- [ ] Add multi torrents (different torrents from same tracker) http scrape?
- [ ] Add multi port support for Http/s trackers # 6881-6889 Ports
- [ ] Manager to put logic inn and clean up logic as much as possible
- [ ] Implement IPv6 for udp and http tracker
- [ ] Allow all peer_id that is reasonable as long as verification is okay
- [ ] Will fail if all tracker protocols are'nt supported
- [ ] Qbittorrent times out every time? What are wrong here - after/during handshake Improve handshake? Try to pretend to be a known client not tiny torrent client
- [ ] Invalid message should be warning not error msg
- [ ] uTorrent Why no bitfield or “wrong” response length?
- [ ] Don’t get any connection to “leachers” or not with bitfield but that might be ok.
- [ ] When return data from function refactor to always return same datatype for instance not False, None when list is expected.
```

#### Alternative fixes
```Python  
if b'files' in data[b'info']: # Can fail if filename is files, almost impossible bug
```

```console
#### Fixed
- [x] Fixed requests error handling 
- [x] Improve HTTP tracking/protocol 
- [x] Implementation of announce-list not just announce
- [x] Are dups removed from peer list before try connect (Dups are removed but not I total count so fix that bug.)
- [x] In read_file -> 'path': [str(paths[index][b'path'])[3:-2]]}) # Improve implementation
- [x] # Client IP's and Port's, use map/lambda function to speed up for loop? -> FAST enough ATM, max 74 clients to looping os ok - 
- [x] Add check of peer id (id from connected client) in udp tracker to make sure it has expected id
- [x] UDP tracker gives more then 74 peers -> Announce accepted, re-announce interval: 1666 leechers: 2 seeders: 236 client ip addresses count: 199 -> Are this new since spec says max 74 or is it not referring to peers? NOTE; Solved -> Just accept as many as possible! 
- [x] Add check and verify IP addresses IPv4 addresses
- [x] Implement scrape for HTTP/HTTPS
- [x] fix import stuff when running tests, but main in main?
- [x] Handle the announce-list in trackers and logic [TCP] - append all url's from list and logic for getting more peer if below threshold (15 for instance in config) then try next announce url from announce list
- [x] Make a function for parsing IP addresses and ports
- [x] tracker_udp -> Need cleaning up, testing and error handling
- [x] BUG:
In PeerWire: while loop after handshake 

if len(response) >=5:
	infinite loop
 
- [x] Verify bitfield message length and compute/log pieces of tracker n
- [x] import socket instead of from socket import socket
- [x] Create unique peer_id at start up of program

```

### Reserve response from current hand sake testing (Client's extension protocol's ?)

uTP extension ?
x00\x03\x00\x00\x00\x00\x00\x00'

```python
    ↑♣ b'\x00\x00\x00\x00\x00\x18\x00\x05'
    ►♣ b'\x00\x00\x00\x00\x00\x10\x00\x05'
    ►☺ b'\x00\x00\x00\x00\x00\x10\x00\x01'
    ►♦ b'\x00\x00\x00\x00\x00\x10\x00\x04'
    ►  b'\x00\x00\x00\x00\x00\x10\x00\x00'
        '[ 0   1   2   3   4   5   6  7]'

    '\x10 -> 5 = BEP-10 Extension Protocol for Peers to Send Arbitrary Data' 
    '\x18 -> 5 = eXEMPT - Extension for Peers to Send Metadata File'
    '\x01 -> 7 = BEP-5 Distributed Hash Table'
    '\x05 -> 7 = Holepunch Extension'  
    '\x04 -> 7 = BEP-6 Fast Extension '
```


### Peer counter has a bug:
```console
2023-02-19 19:14:15.422396 [INFO] Connected to UDP tracker: udp://tracker.opentrackr.org:1337/announce
2023-02-19 19:14:15.485103 [INFO] Tracker responded with: 199 peers with valid ip/port combination of total: 200 peers
2023-02-19 19:14:15.485103 [INFO] UDP Tracker announce accepted, re-announce interval: 1949 leechers: 14 seeders: 2579
2023-02-19 19:14:17.530531 [WARNING] UDP tracker timeout -> No response received
2023-02-19 19:14:17.530531 [WARNING] Connection to UDP tracker failed: udp://tracker.coppersurfer.tk:6969/announce
2023-02-19 19:14:19.533368 [WARNING] UDP tracker timeout -> No response received
2023-02-19 19:14:19.533368 [WARNING] Connection to UDP tracker failed: udp://tracker.leechers-paradise.org:6969/announce
2023-02-19 19:14:19.586100 [INFO] Connected to UDP tracker: udp://tracker.openbittorrent.com:80/announce
2023-02-19 19:14:19.617458 [INFO] Tracker responded with: 199 peers with valid ip/port combination of total: 200 peers
2023-02-19 19:14:19.617458 [INFO] UDP Tracker announce accepted, re-announce interval: 1655 leechers: 12 seeders: 1918
2023-02-19 19:14:20.130430 [WARNING] Tracker did not send complete response
2023-02-19 19:14:20.130930 [WARNING] Tracker did not send incomplete response
2023-02-19 19:14:20.130930 [WARNING] Tracker did not send interval response
2023-02-19 19:14:20.130930 [WARNING] Tracker did not send peers response
2023-02-19 19:14:20.130930 [INFO] HTTP Announce OK, complete: None incomplete: None interval: None peers: 0
2023-02-19 19:14:20.130930 [INFO] Get clients resulted in: 584 Peers/Client addresses
```

### Bug
```console
2023-05-22 23:18:53.274256 [INFO] Trying to downloaded pieces: 0 pieces left: 1012
2023-05-22 23:18:53.274256 [INFO] Blocks in current piece: 16
Traceback (most recent call last):
  File "d:\code\tinytorrent\main.py", line 53, in <module>
    block_data, flag = download.linear_test(current_peer)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "d:\code\tinytorrent\src\download.py", line 66, in linear_test
    current_peer.send(hax)
ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host
```