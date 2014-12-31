#!/usr/bin/python
import service_status
import threading
import traceback

from service_status import StatusEnum
from logger_helper import * 
from threading import *

class BaseService(LoggerHelper):
    
    def __init__(self, logger_name, max_request = 10000):
        LoggerHelper.__init__(self, logger_name)
        self.__max_request = 10000
        self.__status = StatusEnum.stopped
        self.__status_mutex = threading.RLock()
        ##block after create
        self.__request_semaphore = threading.Semaphore(0)
        self.__request_list = []
        self.__request_mutex = threading.RLock()
        self.__main_thread = threading.Thread(target=self.__mainProcess)

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
            if StatusEnum.running == self.__status:
                self.__status = StatusEnum.stopping
                ##notify wait thread
                self.__request_semaphore.release()
        
        self.__main_thread.join()
        with self.__status_mutex:
            self.__status = StatusEnum.stopped
        self.onStop()

    def __mainProcess(self):
        while StatusEnum.running == self.__status:
            ##wait for signal
            self.__request_semaphore.acquire()
            if StatusEnum.running != self.__status:
                ##double protect
                break
            with self.__request_mutex:
                if(0 == len(self.__request_list)):
                    ##empty
                    continue
                ##FIFO/pop front
                request = self.__request_list[0]
                self.__request_list.remove(request)
            try:
                self.OnRequestReceived(request)
                
            except Exception as e:
                self.console("<BaseService>OnRequestReceived exception:%s"%e.args[0])
                self.error("<BaseService>OnRequestReceived exception:%s"%e.args[0])
                traceback.print_exc()
        
    def putRequest(self, request):
        """
        put request into queue tail
        """
        with self.__request_mutex:
            if len(self.__request_list) >= self.__max_request:
                self.console("<BaseService>request queue is full")
                self.error("<BaseService>request queue is full")
                return False
            self.__request_list.append(request)
            self.__request_semaphore.release()
            return True
        
    def insertRequest(self, request):
        """
        put request into queue head
        """
        with self.__request_mutex:
            if len(self.__request_list) >= self.__max_request:
                self.console("<BaseService>request queue is full")
                self.error("<BaseService>request queue is full")
                return False
            self.__request_list.insert(0, request)
            self.__request_semaphore.release()
            return True
        
    """
    method need override by subclass
    """

    """
    onStart
    @return:
    False = initial fail, stop service
    True = initial success, start main service
    """
    def onStart(self):
        pass

    def onStop(self):
        pass

    def OnRequestReceived(self, request):
        pass

