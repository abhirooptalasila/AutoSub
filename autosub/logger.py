import sys
import logging

APP_NAME = "AutoSub"

def setup_applevel_logger(logger_name = APP_NAME, file_name=None): 
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(levelname)s] %(message)s") #%(name)s |
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(sh)
    if file_name:
        fh = logging.FileHandler(file_name)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger

def get_logger(module_name):    
   return logging.getLogger(APP_NAME).getChild(module_name)