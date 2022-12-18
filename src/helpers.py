import time
#import logging
#from pprint import pprint
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

def iprint(*args, color = 'white', network = ''):
    info_msg = ' '.join([str(i) for i in args])
    if 'inn' in network: info_msg = "<-----| " + info_msg
    if 'out' in network: info_msg = "|-----> " + info_msg
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

def tprint(torrent_dict): 
    """ Takes a dict from a torrent file and formate it for tinytorrent style prints"""

    print(f"{datetime.now()} [TORRENT] Name: {torrent_dict['info']['name']}")
    print(f"{datetime.now()} [TORRENT] Trackers: {torrent_dict['announce-list']}")

    if 'files' in torrent_dict['info']: 
        for i in range(len(torrent_dict['info']['files'])):
            print(f"{datetime.now()} [TORRENT] File {i}: {torrent_dict['info']['files'][i]}")

    print(f"{datetime.now()} [TORRENT] Piece length: {torrent_dict['info']['piece_length']}")
    print(f"{datetime.now()} [TORRENT] Piece size: {torrent_dict['info']['piece_length'] / 1024} KB") # ALWAYS use ceil?
    print(f"{datetime.now()} [TORRENT] Pieces: {torrent_dict['pieces']}")
    print(f"{datetime.now()} [TORRENT] Total size of files: {torrent_dict['size']/1024/1024} MB")
