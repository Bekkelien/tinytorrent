import time

from termcolor import colored
from datetime import datetime

# Internal 
from src.config import Config

# Configuration settings
config = Config().get_config()

def timer(func):
    """ Decorator to time a function """
    def wrapper(*args, **kwargs):
        start = time.time()
        rv = func(*args, **kwargs)
        total = time.time() - start
        if config['debug']: 
            dprint("Runtime for function:", func.__name__, ":", f"{total:5f}")
        return rv
    return wrapper

#logger = logging.getLogger(__name__)

def iprint(*args, color = 'white'):
    info_msg = ' '.join([str(i) for i in args])
    info_msg = str(datetime.now()) + " [INFO] " + info_msg
    #logging.info(str(info_msg))
    print(colored(info_msg, color))

def dprint(*args, color = 'yellow'):
    debug_msg = ' '.join([str(i) for i in args])
    debug_msg = str(datetime.now()) + " [DEBUG] " + debug_msg
    #logging.info(str(info_msg))
    print(colored(debug_msg, color))

def eprint(*args, color = 'red'):
    error_msg = ' '.join([str(i) for i in args])
    error_msg = str(datetime.now()) + " [ERROR] " + error_msg
    #logging.error(str(error_msg))
    print(colored(error_msg, color))

def wprint(*args, color = 'magenta'):
    warning_msg = ' '.join([str(i) for i in args])
    warning_msg = str(datetime.now()) + " [WARNING] " + warning_msg
    #logging.warning(str(warning_msg))
    print(colored(warning_msg, color))

def tprint(metadata): 
    """ Takes a dict from a torrent file metadata and formate it for tinytorrent style prints"""
    for key, value in metadata.items():
        if 'files' in key:
            for file in metadata['files']:
                print(f"{datetime.now()} [TORRENT] {key.capitalize()}: {file}")

        elif 'announce-list' in key:
            for idx, _ in enumerate(list(metadata['announce-list'])):
                print(f"{datetime.now()} [TORRENT] Tracker {idx}: {list(metadata['announce-list'])[idx]}")
        else:
            print(f"{datetime.now()} [TORRENT] {key.capitalize()}: {value}")
