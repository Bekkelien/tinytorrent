## Tinytorrent, the goal is to make this a tiny 'automatic' torrent client 

- [x] Implementation of announce-list not just announce
- [ ] Handle the announce-list in trackers and logic 
- [ ] In read_file -> if b'files' in self.data[b'info']: # BUG if single name filename is files
- [x] In read_file -> 'path': [str(paths[index][b'path'])[3:-2]]}) # Improve implementation
- [ ] tracker_udp -> Need cleaning up, testing and error handling
- [ ] # Client IP's and Port's, use map/lambda function to speed up for loop?
- [ ] Implementation of tracking of how much data downloaded this session
- [ ] Implement tracker protocol logic as of now only supports UDP tracking
- [ ] Add check of peer id (id from connected client) in udp tracker to make sure it has expected id
- [ ] Handle pice length for a torrent file 