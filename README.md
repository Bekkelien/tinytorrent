## Tinytorrent, the goal is to make this a tiny 'automatic' torrent client 


#### Create a torrent
```console
Place files in a folder within the ./create_torrent/files folder then run:
Windows: python ./create_torrent/make.py -f <foldername>
Linux: ?
macOS: ?
```

### BUGS

```console
# BUG, Refactor, and seems to drop one IP|Port address
    client_addresses = []
    message = response[0][20:]    
    for index in range(6,len(message),6):
        ip = inet_ntoa(message[index-6:index-2])        # IP 4 Bytes
        port = unpack("!H", message[index-2:index])[0]  # Port 2 Bytes
        tracker_address = [ip,port]                     # TODO: Add Cleaning if port or ip is missing?
        client_addresses.append(tracker_address)   
```
```console
# BUG Fully terminates tinytorrent ATM FIX in (handling of no response in UDP tracker) 
    requests.exceptions.ConnectTimeout: HTTPConnectionPool(host='tracker.kali.org', port=6969): Max retries exceeded with url: xxxxxx (Caused by ConnectTimeoutError(<urllib3.connection.HTTPConnection object at 0x00000249393811E0>, 'Connection to tracker.kali.org timed out. (connect timeout=1)'))
```

### TIP's
- [x] Implementation of announce-list not just announce
- [x] In read_file -> 'path': [str(paths[index][b'path'])[3:-2]]}) # Improve implementation
- [x] # Client IP's and Port's, use map/lambda function to speed up for loop? -> FAST enough ATM, max 74 clients to looping os ok - 
- [x] Add check of peer id (id from connected client) in udp tracker to make sure it has expected id
- [x] UDP tracker gives more then 74 peers -> Announce accepted, re-announce interval: 1666 leechers: 2 seeders: 236 client ip addresses count: 199 -> Are this new since spec says max 74 or is it not referring to peers? NOTE; Solved -> Just accept as many as possible! 
- [x] Add check and verify IP addresses IPv4 addresses
- [x] Implement scrape for HTTP/HTTPS
- [ ] Create unique peer_id at start up of program
- [ ] Handle the announce-list in trackers and logic [TCP]
- [ ] In read_file -> if b'files' in self.data[b'info']: # BUG if single name filename is files
- [ ] tracker_udp -> Need cleaning up, testing and error handling
- [ ] Implementation of tracking of how much data downloaded this session
- [ ] Implement HTTP tracking/protocol 
- [ ] Should we verify unknown trackers response ATM and download for it, try to download from known clients in testing period
- [ ] Handle pice length for a torrent file 
- [ ] Implement IPv6 for UDP http://www.bittorrent.org/beps/bep_0015.html and HTTP/HTTPS(or does this only return IPv4 stuff?)?
- [ ] Search for more client id's to make sure as many as possible are known 
- [ ] Rename sending messages name currently: message 
- [ ] Socket tracking is now a mess
- [ ] Documentation of functions and classes
- [ ] To many dependencies from a to b and c and over back into d ++
- [ ] Handle TCP connection timeout make a generic function for connections? to avoud TimeoutError: timed out and other socket errors 
- [ ] Create Tests- pytest
- [ ] Add type hints? 
- [ ] Map peers and what state they are in 
- [ ] Make a function for parsing IP addresses and ports, (Include IPv6?)
- [ ] Should peer id be one for en run if software or change each time?
- [ ] How to validate a tracker when using HTTP/HTTPS? or not?
- [ ] Create verification og a content of a torrent file 
- [ ] fix import stuff when running tests, but main in main?
- [ ] The way it is structured now makes it hard to break out of a state if the tracker does not respond with proper responses
- [ ] Add symbol if data is in and out in prints
- [ ] Decide to use network inn and out in terminal/cli or not!
- [ ] Add multi file http scrape?
- [ ] Add multi port support for Http/s trackers # 6881-6889 Ports
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