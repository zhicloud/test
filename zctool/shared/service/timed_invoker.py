#!/usr/bin/python
import service_status
import threading

from service_status import StatusEnum

class TimedInvoker(object):
    """
    usage:
    constuctor(callback_function, interval, limit)
    
    isRunning():
    start():
    stop():
    
    created akumas 2013.12.27
    """
    interval = 1
    def __init__(self, callback, interval = interval, limit = 0):
        self.__status = StatusEnum.stopped
        self.__status_mutex = threading.RLock()
        self.__interval = interval
        self.__limit = limit
        self.__callback = callback
        self.__main_thread = threading.Thread(target=self.__run)
        self.__invoke_thread = threading.Thread(target=self.__invoke)
        self.__exit_event = threading.Event()
        self.__invoke_event = threading.Event()

    def isRunning(self):
        return (StatusEnum.running == self.__status)
        
    def start(self):
        """
        start service
        """
        with self.__status_mutex:
            if StatusEnum.stopped != self.__status:
                return False
            self.__status = StatusEnum.running
            self.__main_thread.start()
            self.__invoke_thread.start()
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
                self.__exit_event.set()
                self.__invoke_event.set()
        
        self.__main_thread.join()
        self.__invoke_thread.join()
        with self.__status_mutex:
            self.__status = StatusEnum.stopped
            
    def __run(self):
        count = 0
        while self.isRunning():
            self.__exit_event.wait(self.__interval)
            if not self.isRunning():
                ##thread stopped
                break
            self.__invoke_event.set()
            count += 1
            if 0 != self.__limit:
                if count >= self.__limit:
                    break
    def __invoke(self):
        count = 0
        while self.isRunning():
            self.__invoke_event.wait()
            if not self.isRunning():
                ##thread stopped
                break
            if self.__invoke_event.isSet():
                ##clear when set
                self.__invoke_event.clear() 
            ##callback
            self.__callback()
            count += 1
            if 0 != self.__limit:
                if count >= self.__limit:
                    break

        ##end while self.isRunning():
                
if __name__ == '__main__':
    import logging
    import time
    import sys
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)

    logger = logging.getLogger("test")

    ##invoke
    def callback():
        logger.info("invoked")

    invoker = TimedInvoker(callback)
    invoker.start()
    time.sleep(5)
    invoker.stop()

##    ##limit
##    invoker = TimedInvoker(callback, 2, 2)
##    invoker.start()
##    time.sleep(6)
##    invoker.stop()
    
        

