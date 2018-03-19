import logging
import logging.handlers
import sys
import os
from enum import IntEnum

# These are flags for standard handler + formatter combos. 
class BasicLoggingConfiguration(IntEnum):
    COMMAND_LINE = 1                # Log everything to a command line with reasonable human-readability
    TWO_SHORT_ROTATING_FILES = 2    # Log a short history suitable for `tail`-ing on a server
    TEN_MEDIUM_ROTATING_FILES = 4   # Log a more thorough history that saves a longer history.
    COMMAND_LINE_DEBUG = 8          # A more thorough logging service

class LoggingService(object):

    @classmethod
    def get_log_filename(klass):
        # First, try the directory of the executable
        log_base_path = os.path.abspath(sys.path[0])
        if log_base_path == '':
            # If not, try the current working directory
            log_base_path = os.path.abspath(os.getcwd())
            # That directory plus "logs/ohmega.log" (which may rotate with a [.N])
        return os.path.join(log_base_path, "logs", "ohmega.log")

    @classmethod
    def create_log_directory(klass):
        return os.makedirs(os.path.dirname(LoggingService.getLogFilename(), 0o644))
        

    def __init__(self, logging_configuration = None):

        logging.getLogger().setLevel(logging.DEBUG)
        # Note that COMMAND_LINE and None are basically the same thing, meaning that this
        # configuration will be used by default.
        if logging_configuration == None or logging_configuration & BasicLoggingConfiguration.COMMAND_LINE:
            self.add_command_line_logging()
        if logging_configuration & BasicLoggingConfiguration.COMMAND_LINE_DEBUG:
            self.add_command_line_debug_logging()
        # TODO: do an int flag with this, which isn't supported in 2.7
        #if logging_configuration & BasicLoggingConfiguration.TWO_SHORT_ROTATING_FILES:
        #    self.addShortRotatingLogging()
        #if logging_configuration & BasicLoggingConfiguration.TEN_MEDIUM_ROTATING_FILES:
        #    self.addMediumRotatingLogging()

    @property
    def logger(self):
        return logging

    def add_command_line_logging(self):
        formatter = logging.Formatter("%(levelname)-8.8s:%(filename)12.12s@%(lineno)-4.4s %(message)s")
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(stream_handler)

    def add_command_line_debug_logging(self):
        formatter = logging.Formatter("%(levelname)-8.8s:%(filename)12.12s@%(lineno)-4.4s %(message)s")
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(stream_handler)

    def add_short_rotating_file_logging(self):
        formatter = logging.Formatter("%(levelname)-8.8s:%(filename)12.12s@%(lineno)-4.4s [%(asctime)-23.23s] $(message)s")
        LoggingService.make_log_dir()
        # 2 1-MB log files
        file_handler = logging.handlers.RotatingFileHandler(LoggingService.getLogFilename(),
            'a', 1024 * 1024 * 1, 1, 'utf8')
    
    def add_medium_rotating_file_logging(self):
        formatter = logging.Formatter("%(levelname)-8.8s:%(filename)12.12s@%(lineno)-4.4s [%(asctime)-23.23s] $(message)s")
        LoggingService.make_log_dir()
        # 10 10-MB log files
        file_handler = logging.handlers.RotatingFileHandler(LoggingService.getLogFilename(),
            'a', 1024 * 1024 * 10, 9, 'utf8')

