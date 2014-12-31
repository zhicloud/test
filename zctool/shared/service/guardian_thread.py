#!/usr/bin/python
import service_status
import threading

from service_status import StatusEnum
from threading import *
from logger_helper import *

class GuardianThread(LoggerHelper):
    ##guardian name
    _name = ""
    
    def __init__(self, name):
        self.__status = StatusEnum.stopped
        self.__status_mutex = threading.RLock()
        self._name = name
        self.__main_thread = threading.Thread(target=self.run)

    def isRunning(self):
        return (StatusEnum.running == self.__status)
        
    def start(self):
        """
        start service
        """
        with self.__status_mutex:
            if StatusEnum.stopped != self.__status:
                self.console("guardian '%s' already running"%self._name)
                return False
            self.__status = StatusEnum.running
            self.onStarted()
            self.__main_thread.start()
            return True

    def stop(self):
        """
        stop service
        """
        with self.__status_mutex:
            if StatusEnum.stopped == self.__status:
                return
            if self.isRunning():
                self.__status = StatusEnum.stopping
                ##notify wait thread
                self.onStopping()
        
        self.__main_thread.join()
        with self.__status_mutex:
            self.__status = StatusEnum.stopped
            self.onStopped()

        
    """
    method need override by subclass
    """
    def run(self):
        pass
    def onStarted(self):
        pass
    def onStopping(self):
        pass
    def onStopped(self):
        pass
