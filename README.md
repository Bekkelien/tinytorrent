## Tinytorrent, the goal is to make this a tiny 'automatic' torrent client 


#### Create a torrent
```console
Windows: python ./create_torrent/make.py -f <foldername>
```

### TIP's
- [x] Implementation of announce-list not just announce
- [x] In read_file -> 'path': [str(paths[index][b'path'])[3:-2]]}) # Improve implementation
- [x] # Client IP's and Port's, use map/lambda function to speed up for loop? -> FAST enough ATM, max 74 clients to looping os ok - 
- [x] Add check of peer id (id from connected client) in udp tracker to make sure it has expected id
- [ ] Handle the announce-list in trackers and logic [TCP]
- [ ] In read_file -> if b'files' in self.data[b'info']: # BUG if single name filename is files
- [ ] tracker_udp -> Need cleaning up, testing and error handling
- [ ] Implementation of tracking of how much data downloaded this session
- [ ] Implement HTTP tracking/protocol 
- [ ] Should we verify unknown trackers response ATM and download for it, try to download from known clients in testing period
- [ ] Handle pice length for a torrent file 
- [ ] Implement IPv6 for UDP http://www.bittorrent.org/beps/bep_0015.html
- [ ] Search for more client id's to make sure as many as possible are known 
- [ ] Rename sending messages name currently: message 
- [ ] Socket tracking is now a mess
- [ ] Documentation of functions and classes
- [ ] To many dependencies from a to b and c and over back into d ++
- [ ] Handle TCP connection timeout make a generic function for connections? to avoud TimeoutError: timed out and other socket errors 
- [ ] Create Tests- pytest
- [ ] Add type hints? 
- [ ] Map peers and what state they are in 
- [ ] UDP tracker gives more then 74 peers -> Announce accepted, re-announce interval: 1666 leechers: 2 seeders: 236 client ip addresses count: 199 -> Are this new since spec says max 74 or is it not referring to peers? 

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