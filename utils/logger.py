import time
import logging
import os
from datetime import datetime
import json

class DailyHourlyLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.current_day = None
        self.current_hour = None
        self.handler = None
        self.logger.propagate = False
        
        # Find the project root directory
        self.parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        self.log_base_dir = os.path.join(self.parent_dir, 'logs')
        
        # Set the log format
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            style='%'
        )
        
        # Initialize the processor
        self.update_handler()

    def get_log_file_path(self):
        """Get the current log file path"""
        now = datetime.now()
        
        day_dir = now.strftime("%Y%m%d")
        day_path = os.path.join(self.log_base_dir, day_dir)
        os.makedirs(day_path, exist_ok=True)
        
        hour_file = f"log_{now.strftime('%H')}.log"
        return os.path.join(day_path, hour_file)

    def update_handler(self):
        now = datetime.now()
        current_day = now.strftime("%Y%m%d")
        current_hour = now.strftime("%H")
        
        if (self.current_day != current_day or 
            self.current_hour != current_hour or 
            self.handler is None):
            
            if self.handler is not None:
                self.logger.removeHandler(self.handler)
                self.handler.close()
            
            log_file = self.get_log_file_path()
            self.handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            self.handler.setFormatter(self.formatter)
            self.logger.addHandler(self.handler)
            
            self.current_day = current_day
            self.current_hour = current_hour

    def log(self, level, message):
        if not isinstance(message, str):
            message = json.dumps(message, indent=2, ensure_ascii=False)
        formatted_message = '\n'.join(
            line for line in message.split('\n')
        )
        
        log_file = self.update_handler()
        if level == 'DEBUG':
            self.logger.debug(formatted_message)
        elif level == 'INFO':
            self.logger.info(formatted_message)
        elif level == 'WARNING':
            self.logger.warning(formatted_message)
        elif level == 'ERROR':
            self.logger.error(formatted_message)
        elif level == 'CRITICAL':
            self.logger.critical(formatted_message)

        return log_file
        


    def debug(self, message):
        self.log('DEBUG', message)

    def info(self, message):
        self.log('INFO', message)

    def warning(self, message):
        self.log('WARNING', message)

    def error(self, message):
        self.log('ERROR', message)

    def critical(self, message):
        self.log('CRITICAL', message)

logger = DailyHourlyLogger(__name__)
