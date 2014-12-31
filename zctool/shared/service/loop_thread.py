#!/usr/bin/python
import service_status
import threading

from service_status import StatusEnum
from threading import *
from logger_helper import *

class LoopThread(LoggerHelper):
    """
    usage:
    isRunning():
    start():
    stop():

    override methods
    onStart():return False to cancel start process
    onStop():
    onLoop():customize loop process here

    created akumas 2013.8.8
    """
    default_timeout = 1
    def __init__(self, timeout = default_timeout):
        self.__status = StatusEnum.stopped
        self.__status_mutex = threading.RLock()
        self.__timeout = timeout
        self.__main_thread = threading.Thread(target=self.__run)
        self.__event = threading.Event()

    def isRunning(self):
        return (StatusEnum.running == self.__status)
        
    def start(self):
        """
        start service
        """
        with self.__status_mutex:
            if StatusEnum.stopped != self.__status:
                return False
            if not self.onStart():
                return False
            self.__status = StatusEnum.running
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
                self.__event.set()
        
        self.__main_thread.join()
        with self.__status_mutex:
            self.__status = StatusEnum.stopped
            
        self.onStop()
            
    def __run(self):
        self.__event.clear()
        while self.isRunning():
            self.__event.wait(self.__timeout)
            if not self.isRunning():
                ##thread stopped
                break
            self.__event.clear()
            self.onLoop()

        ##end while self.isRunning():
        
    """
    method need override by subclass
    """
    def onStart(self):
        """
        return False to cancel start process
        """
        return True
    def onStop(self):
        pass

    def onLoop(self):
        """
        customize loop process here
        """
        pass
