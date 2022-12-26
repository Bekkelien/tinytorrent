import yaml
import random
import string

from pathlib import Path

class Config():
    
    def __init__(self):
        file_path = Path('config.yaml')
        
        # Read config file
        with open(file_path) as f:
            self.config = yaml.load(stream=f, Loader=yaml.Loader)

    def get_config(self) -> dict:
        """ Used to get config for TinyTorrent and add unique peer_id for one run of TinyTorrent"""
        self.config['client']['peer_id'] = self.config['client']['peer_id'] +  ''.join(random.choices(string.digits + string.ascii_letters, k=12))
        self.config['client']['key'] = self.config['client']['key'] +  ''.join(random.choices(string.digits + string.ascii_letters, k=6))
        return self.config

# NOTE: TESTING
if __name__ == '__main__':
    config = Config().get_config()
    from pprint import pprint
    pprint(config)
