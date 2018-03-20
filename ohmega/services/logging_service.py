import logging
import logging.handlers
import sys
import os
from enum import IntEnum


# These are flags for standard handler + formatter combos.
class LoggingConfiguration(IntEnum):
    # Log everything to a command line with reasonable human-readability
    COMMAND_LINE = 1
    # Log a short history suitable for `tail`-ing on a server
    TWO_SHORT_ROTATING_FILES = 2
    # Log a longer, more throrough history
    TEN_MEDIUM_ROTATING_FILES = 4
    # Debug variant for development on the command line
    COMMAND_LINE_DEBUG = 8


class LoggingService(object):

    @classmethod
    def get_log_filename(klass):
        # First, try the directory of the executable
        log_base_path = os.path.abspath(sys.path[0])
        if log_base_path == '':
            # If not, try the current working directory
            log_base_path = os.path.abspath(os.getcwd())
            # That directory plus "logs/ohmega.log"
            # (which may rotate with a [.N])
        return os.path.join(log_base_path, "logs", "ohmega.log")

    @classmethod
    def create_log_directory(klass):
        return os.makedirs(os.path.dirname(
            LoggingService.getLogFilename(), 0o644))

    def __init__(self, logging_configuration=None):

        logging.getLogger().setLevel(logging.DEBUG)
        # Note that COMMAND_LINE and None are basically the same thing, meaning
        # that this configuration will be used by default.
        if logging_configuration is None or\
                logging_configuration & LoggingConfiguration.COMMAND_LINE:
            self.add_command_line_logging()
        if logging_configuration & LoggingConfiguration.COMMAND_LINE_DEBUG:
            self.add_command_line_debug_logging()

    @property
    def logger(self):
        return logging

    def add_command_line_logging(self):
        formatter = logging.Formatter(
                "%(levelname)-8.8s:%(filename)12.12s@%(lineno)-4.4s %(message)s")
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(stream_handler)

    def add_command_line_debug_logging(self):
        formatter = logging.Formatter(
                "%(levelname)-8.8s:%(filename)12.12s@%(lineno)-4.4s %(message)s")
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(stream_handler)

#    def add_short_rotating_file_logging(self):
#        formatter = logging.Formatter(
#                "%(levelname)-8.8s:%(filename)12.12s@%(lineno)-4.4s [%(asctime)-23.23s] $(message)s")
#        LoggingService.make_log_dir()
#        # 2 1-MB log files
#        file_handler = logging.handlers.RotatingFileHandler(LoggingService.getLogFilename(),
#            'a', 1024 * 1024 * 1, 1, 'utf8')
#    
#    def add_medium_rotating_file_logging(self):
#        formatter = logging.Formatter(
#                "%(levelname)-8.8s:%(filename)12.12s@%(lineno)-4.4s [%(asctime)-23.23s] $(message)s")
#        LoggingService.make_log_dir()
#        # 10 10-MB log files
#        file_handler = logging.handlers.RotatingFileHandler(LoggingService.getLogFilename(),
#            'a', 1024 * 1024 * 10, 9, 'utf8')
#
