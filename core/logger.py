import logging
import sys
from datetime import datetime

def setup_logger(name: str = "excel_agent") -> logging.Logger:
    """Setup and return a configured logger instance."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        file_handler = logging.FileHandler('logs/excel_agent_%s.log' % datetime.now().strftime("%Y%m%d_%H%M%S"))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger 