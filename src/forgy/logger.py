import logging
import os
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler

### create logs directory if nonexistent
##logs_parent = Path(os.getcwd()).parent.parent
##print(logs_parent)
##logs_path = logs_parent/"logs"
##print(logs_path)
##
##os.makedirs(logs_path, exist_ok=True)
##print("LOG CREATED")

# Create and configure custom logger
def configure_logger(name=None):

    # create logs directory if nonexistent
    logs_parent = Path(os.getcwd()).parent
    print(logs_parent)
    logs_path = logs_parent/"logs"
    print(logs_path)

    os.makedirs(logs_path, exist_ok=True)
    print("LOG CREATED")
    logger = logging.getLogger(name)

    # if handler exist, avoid duplicating it
    if logger.handlers:
        return logger

    # Set logging level for logger to DEBUG
    logger.setLevel(logging.DEBUG)

    # Create handlers
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)

    # Rotating file handler (a max filesize of 5MB)
    rotating_file_handler = RotatingFileHandler(f'{logs_path}/app.log', maxBytes=5e6, backupCount=3)
    rotating_file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    rotating_file_handler.setFormatter(file_format)


    # Add console and file handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(rotating_file_handler)

    return logger

    
