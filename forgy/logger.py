import logging
import os
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
# create logs directory if nonexistent

os.makedirs('logs', exist_ok=True)

# Create and configure custom logger
def configure_logger(name=None):
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
    rotating_file_handler = RotatingFileHandler(f'logs/app.log', maxBytes=5e6, backupCount=3)
    rotating_file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    rotating_file_handler.setFormatter(file_format)


    # Add console and file handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(rotating_file_handler)

    return logger

    
