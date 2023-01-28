import yaml
import random
import string

from pathlib import Path

class Config():
    def __init__(self):
        self.config_path = Path('config.yaml')

    def get_config(self) -> dict:
        """ Get the configuration file and return a dictionary """

        # Read config file
        with open(self.config_path) as f:
            config = yaml.load(stream=f, Loader=yaml.Loader)

        # Add session ID 
        config['client']['peer_id'] = config['client']['peer_id'] +  ''.join(random.choices(string.digits + string.ascii_letters, k=12))
        config['client']['key'] = config['client']['key'] +  ''.join(random.choices(string.digits + string.ascii_letters, k=6))
        return config

# Testing configuration information:
if __name__ == '__main__':
    config = Config().get_config()
    from pprint import pprint
    pprint(config)
