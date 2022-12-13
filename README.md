## Tinytorrent, the goal is to make this a tiny 'automatic' torrent client 


#### Create a torrent
```console
Place files in a folder within the ./create_torrent/files folder then run:
Windows: python ./create_torrent/make.py -f <foldername>
Linux: ?
macOS: ?
```

### Testing (To be implemented)
```console
run:
pytest
pytest -s # To display the prints
```

### TIP's'
#### Top priority:
- [ ] tracker_udp -> Need cleaning up, testing and error handling
- [ ] Handle TCP connection timeout make a generic function for connections? to avoud TimeoutError: timed out and other socket errors 
#### Needs to be implemented
- [ ] Create a logo for tinytorrent
- [ ] Create unique peer_id at start up of program
- [ ] In read_file -> if b'files' in self.data[b'info']: # BUG if single name filename is files
- [ ] Implementation of tracking of how much data downloaded this session
- [ ] Improve HTTP tracking/protocol 
- [ ] Should we verify unknown trackers response ATM and download for it, try to download from known clients in testing period
- [ ] Handle pice length for a torrent file 
- [ ] Implement IPv6 for UDP http://www.bittorrent.org/beps/bep_0015.html and HTTP/HTTPS(or does this only return IPv4 stuff?)?
- [ ] Rename sending messages name currently: message 
- [ ] Socket tracking is now a mess
- [ ] Documentation of functions and classes
- [ ] To many dependencies from a to b and c and over back into d ++
- [ ] Create Tests- pytest
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
- [ ] Implement IPv6
#### Fixed
- [x] Fixed requests error handling 
- [x] Implementation of announce-list not just announce
- [x] In read_file -> 'path': [str(paths[index][b'path'])[3:-2]]}) # Improve implementation
- [x] # Client IP's and Port's, use map/lambda function to speed up for loop? -> FAST enough ATM, max 74 clients to looping os ok - 
- [x] Add check of peer id (id from connected client) in udp tracker to make sure it has expected id
- [x] UDP tracker gives more then 74 peers -> Announce accepted, re-announce interval: 1666 leechers: 2 seeders: 236 client ip addresses count: 199 -> Are this new since spec says max 74 or is it not referring to peers? NOTE; Solved -> Just accept as many as possible! 
- [x] Add check and verify IP addresses IPv4 addresses
- [x] Implement scrape for HTTP/HTTPS
- [x] fix import stuff when running tests, but main in main?
- [x] Handle the announce-list in trackers and logic [TCP] - append all url's from list and logic for getting more peer if below threshold (15 for instance in config) then try next announce url from announce list
- [x] Make a function for parsing IP addresses and ports


### Reserve response from current hand sake testing (Client's extension protocol's ?)
```python
    ↑♣ b'\x00\x00\x00\x00\x00\x18\x00\x05'
    ►♣ b'\x00\x00\x00\x00\x00\x10\x00\x05'
    ►☺ b'\x00\x00\x00\x00\x00\x10\x00\x01'
    ►♦ b'\x00\x00\x00\x00\x00\x10\x00\x04'
    ►  b'\x00\x00\x00\x00\x00\x10\x00\x00'
        '[ 0   1   2   3   4   5   6  7]'

    '\x10 -> 5 = BEP-10 Extension Protocol' 
    '\x18 -> 5 = ?'
    '\x05 -> 7 = '  
    '\x04 -> 7 = BEP-6 Fast Extension '
```