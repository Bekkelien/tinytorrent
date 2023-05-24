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
            for index, file in enumerate(metadata['files']):
                print(f"{datetime.now()} [TORRENT] File {index}: {file}")

        elif 'announce_list' == key:
            for idx, _ in enumerate(list(metadata['announce_list'])):
                print(f"{datetime.now()} [TORRENT] Tracker {idx}: {list(metadata['announce_list'])[idx]}")

        elif 'bitfield' == key:
            if len(metadata['bitfield']) <= 20: print(f"{datetime.now()} [TORRENT] Bitfield: {metadata['bitfield']}")
            else: print(f"{datetime.now()} [TORRENT] Bitfield: {metadata['bitfield'][0:8]} ..... {metadata['bitfield'][-8:]}")

        elif 'pieces_downloaded' == key:
            if len(metadata['pieces_downloaded']) <= 20: print(f"{datetime.now()} [TORRENT] Pieces downloaded: {metadata['pieces_downloaded']}")
            else: print(f"{datetime.now()} [TORRENT] Pieces downloaded: {metadata['pieces_downloaded'][0:8]} ..... {metadata['pieces_downloaded'][-8:]}")

        elif 'pieces' == key:
            pieces = int(len(metadata['pieces']) / 20)
            if pieces < 1 : eprint("Info hash error unknown length:", pieces)
            else: print(f"{datetime.now()} [TORRENT] Pieces: {pieces} with hash of 20 bytes, first hash: {metadata['pieces'][0:20]}")

        else:
            print(f"{datetime.now()} [TORRENT] {key.capitalize()}: {value}")
