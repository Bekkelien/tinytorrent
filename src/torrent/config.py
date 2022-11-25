import yaml
from pathlib import Path

class Config():
    def __init__(self):
        file_path = Path('config.yaml')
        
        # Read config file
        with open(file_path) as f:
            self.config = yaml.load(stream=f, Loader=yaml.Loader)

    def get_config(self) -> dict:
        return self.config

if __name__ == '__main__':
    config = Config().get_config()
    print(config)