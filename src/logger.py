import logging
import os

# The level can be changed without touching the code, e.g. LOG_LEVEL=DEBUG make run
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

def configure_logging():
    logging.basicConfig(level = LOG_LEVEL, format = LOG_FORMAT, datefmt = '%H:%M:%S')

def get_logger(name):
    return logging.getLogger(name)
