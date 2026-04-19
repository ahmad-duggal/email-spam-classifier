import logging
import sys
import os
from logging.handlers import RotatingFileHandler

# Ensure log directory exists
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'system.log')

def setup_logger(name="DigitalSentinel"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Prevent duplicate handlers
    if not logger.handlers:
        # Standardized log format for production
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | [%(module)s] | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler streams to standard output (helpful for Docker)
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        # File handler writes to disk with rotation (max 5MB, keep 3 latest)
        fh = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
    return logger

# Singleton logger instance
logger = setup_logger()
