from src.clients import Client

def test_client():
    peer_identifier_examples = [b'',                                                # Invalid
                                b'TR30ga',                                          # Invalid
                                b'-33410Z-u6nvd4bqmp3m',                            # Invalid
                                b'-qB410Z-',                                        # Kinda valid (no random peer id)
                                b'-qB4520-L8Y973gWRGNj',                            # Valid
                                b'-lt0D80-\x1c\xbf\xff\xfdw\x0e<\xdc\xa6\xadl\x1d'] # Valid
    
    excepted_response = ['', '', '', 'qBittorrent','qBittorrent', 'libTorrent']
        
    for peer_identifier, expected_response in zip(peer_identifier_examples, excepted_response):
        client_name = Client().software(peer_identifier)
        assert client_name == expected_response

