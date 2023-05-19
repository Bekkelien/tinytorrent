from src.protocol import PeerMessage

def test_bitfield_status(debug=True):
    """ OVERKILL x99
    Currently overkill, but should be ok when implementing bitfield status for every peer 
    (assuming that we can get bitfield status of different types)
    """

    # Correct response 
    # Sate 0 == seeder
    # Sate 1 == leecher
    # Sate 2 == unknown

    for number_of_pieces in [9,21,123,4324,121]: # BUG: now is under 9 in loop
        for state in [0,1,2]:

            if state == 0: bitfield_list =  [1] * number_of_pieces
            if state == 1: bitfield_list =  [0] * (number_of_pieces-1) + [1]
            if state == 2: bitfield_list =  b'\x00'
            if debug: print(bitfield_list)

            
            bitfield_bin_padded = ''.join(map(str, bitfield_list)).ljust((len(bitfield_list) + 7) // 8 * 8, '0')
            if debug: print("f", bitfield_bin_padded)

            bitfield_bytes = int(bitfield_bin_padded, 2).to_bytes((len(bitfield_bin_padded) + 7) // 8, byteorder='big')
            if debug: print(bitfield_bytes, state)

            metadata = {}
            metadata['bitfield_length'] = ((number_of_pieces + 7) // 8) * 8
            metadata['bitfield_spare'] = metadata['bitfield_length'] - number_of_pieces

            # Test all states
            if state == 0: assert PeerMessage.bitfield_status(bitfield_bytes, metadata) == "seeder"
            if state == 1: assert PeerMessage.bitfield_status(bitfield_bytes, metadata) == "leecher"
            if state == 2: assert PeerMessage.bitfield_status(bitfield_bytes, metadata) == "unknown"


        # Bitfield should always be bytes
        assert PeerMessage.bitfield_status(b'', None) == "unknown"
