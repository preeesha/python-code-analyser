import logging
import logging.config
from .logging_info import  LOG_LEVEL_ICONS, setup_logging

class CustomLogger:
    
    
    def __init__(self, name: str = __name__):
      
        setup_logging()
        self.logger = logging.getLogger(name)
    
    def debug(self, message: str) -> None:
        
        icon = LOG_LEVEL_ICONS.get('DEBUG', '')
        self.logger.debug(f"{icon} {message}",stacklevel=2)
    
    def info(self, message: str) -> None:
       
        icon = LOG_LEVEL_ICONS.get('INFO', '')
        self.logger.info(f"{icon} {message}",stacklevel=2)
    
    def warning(self, message: str) -> None:
        
        icon = LOG_LEVEL_ICONS.get('WARNING', '')
        self.logger.warning(f"{icon} {message}",stacklevel=2)
    
    def error(self, message: str) -> None:
        
        icon = LOG_LEVEL_ICONS.get('ERROR', '')
        self.logger.error(f"{icon} {message}",stacklevel=2)
    
    def critical(self, message: str) -> None:
        
        icon = LOG_LEVEL_ICONS.get('CRITICAL', '')
        self.logger.critical(f"{icon} {message}",stacklevel=2)
    
    def success(self, message: str) -> None:
       
        icon = LOG_LEVEL_ICONS.get('SUCCESS', '')
        self.logger.info(f"{icon} {message}",stacklevel=2)


def get_logger(name: str = None) -> CustomLogger:
    
    return CustomLogger(name)
