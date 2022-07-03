# from https://stackoverflow.com/questions/11927278/how-to-configure-logging-in-python
import os
import logging

class Logger(object):
    log_file = None
    log_level = None
    
    @staticmethod
    def set_globals(file_log, level):
      Logger.log_file = file_log
      Logger.log_level = level

    def __init__(self, name):
        name = name.replace('.log','')
        logger = logging.getLogger('%s' % name)
        logger.setLevel(Logger.log_level)
        if not logger.handlers:
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s')

            file_handler = logging.FileHandler(Logger.log_file)
            config(logger, file_handler, formatter, Logger.log_level)

            console_handler = logging.StreamHandler()
            config(logger, console_handler, formatter, Logger.log_level)
        self._logger = logger

    def get(self):
        return self._logger

def config(logger, handler, formatter, log_level):
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    logger.addHandler(handler)    