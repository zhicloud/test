#!/usr/bin/python
import logging
import io
import sys
from logging import *

class LoggerHelper(object):
    logger = None
    console_logger = None
    logger_name = ""
    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)
        self.logger.debug("logger '%s' added"%logger_name)
        self.logger_name = logger_name
##        if sys.platform.startswith("win32"):
##        self.console_logger = sys.stdout
##        else:
##            ##release function
##            self.console_logger = io.open("/dev/console", "wb", 0)

    def debug(self, content):
        self.logger.debug(content)
        
    def info(self, content):
        self.logger.info(content)
        
    def warn(self, content):
        self.logger.warn(content)
        
    def error(self, content):
        self.logger.error(content)
        
    def critical(self, content):
        self.logger.critical(content)

    def console(self, content):
        ##debug only
        print "[%s] %s"%(self.logger_name, content)
        ##release function
##        self.console_logger.write(bytearray("[%s] %s\n"%(self.name, content), "utf-8"))
        
        
