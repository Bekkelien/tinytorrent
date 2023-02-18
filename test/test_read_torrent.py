from src.read_torrent import TorrentFile

def test_torrentfile_read():

    singeltorrent = './test/torrents/single.torrent'
    multitorrent = './test/torrents/multi.torrent'

    metadata = TorrentFile(multitorrent).read()

    assert metadata['info_hash'] == b'\xb0\xf1Fm\xa6ag\\\xfe)k\xac\x14\x93\x0f4#\xc17\x81'
    assert metadata['announce_list'] == ['udp://tracker.opentrackr.org:1337/announce']
    assert metadata['size'] == 328
    assert metadata['files'] == [{'length': 237, 'path': ['data1.txt']}, {'length': 91, 'path': ['data2.txt']}]
    assert metadata['name'] == 'multi'
    assert metadata['piece_length'] == 16384
    assert metadata['pieces_count'] == 1
    assert metadata['bitfield_spare'] == 7
    assert metadata['bitfield_length'] == 8
    assert metadata['left'] == 328
    assert metadata['downloaded'] == 0
    assert metadata['uploaded'] == 0
    assert metadata['pieces'] == b'+\xb1\xedvB\xa5\x15)\xa6)C\x0eP\x11\xe2\xff\xcf\ng\xe5'

    metadata = TorrentFile(singeltorrent).read()

    assert metadata['info_hash'] == b'=\xbaw\x84K\xef\t\ro\x1b\xb4\xf4\xece\x04\x14\x9d\xdf\xed\xfe'
    assert metadata['announce_list'] == ['udp://tracker.opentrackr.org:1337/announce']
    assert metadata['size'] == 237
    assert metadata['files'] == [{'length': 237, 'path': ['data3.txt']}]
    assert metadata['name'] == 'single'
    assert metadata['piece_length'] == 16384
    assert metadata['pieces_count'] == 1
    assert metadata['bitfield_spare'] == 7
    assert metadata['bitfield_length'] == 8
    assert metadata['left'] == 237
    assert metadata['downloaded'] == 0
    assert metadata['uploaded'] == 0
    assert metadata['pieces'] == b'o\xaa\xd3\xe2\x1a0}n\xe4\xcb\xd1\x00lr\xd6\x08\xe1\xb4\xa6\x85'    