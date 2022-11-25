import time
#import logging
from datetime import datetime

# Internal 
from config import Config

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

def iprint(*args):
    info_msg = ' '.join([str(i) for i in args])
    info_msg = str(datetime.now()) + " [INFO] " + info_msg
    #logging.info(str(info_msg))
    print(info_msg)

def dprint(*args):
    debug_msg = ' '.join([str(i) for i in args])
    debug_msg = str(datetime.now()) + " [DEBUG] " + debug_msg
    #logging.info(str(info_msg))
    print(debug_msg)


def eprint(*args):
    error_msg = ' '.join([str(i) for i in args])
    error_msg = str(datetime.now()) + " [ERROR] " + error_msg
    #logging.error(str(error_msg))
    print(error_msg)

def wprint(*args):
    warning_msg = ' '.join([str(i) for i in args])
    warning_msg = str(datetime.now()) + " [WARNING] " + warning_msg
    #logging.warning(str(warning_msg))
    print(warning_msg)