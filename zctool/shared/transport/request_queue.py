#!/usr/bin/python
import threading
import datetime
import logging
import random
from service.service_status import StatusEnum

class RequestQueue(object):
    ##milliseconds
    def __init__(self, index, handler, cache, max_request = 1000,
                 debug = False, logger_name = "RequestQueue"):
        self.index = index
        self.handler = handler
        self.cache = cache
        self.max_request = max_request
        self.status = StatusEnum.stopped
        self.status_mutex = threading.RLock()
        
        ##block after create
        self.request_available = threading.Semaphore()
        self.request_list = []
        self.request_mutex = threading.RLock()
        self.main_thread = threading.Thread(target=self.mainProcess)

        self.debug = debug
        self.logger_name = logger_name
        if self.debug:
            self.logger = logging.getLogger(logger_name)
##            self.total = 0
##            self.handled = 0
##            self.release = 0
##            self.aquire = 0
        
    @staticmethod
    def milliseconds(time_delta):
        return (float(time_delta.microseconds + (time_delta.seconds + time_delta.days * 24 * 3600) * 10**6) / 10**3)

    def start(self):        
        """
        start channel
        """
        with self.status_mutex:
            if StatusEnum.stopped != self.status:
                return False
            self.status = StatusEnum.running            
            self.main_thread.start()
            return True
        

    def stop(self):
        """
        stop channel
        """
        with self.status_mutex:
            if StatusEnum.stopped == self.status:
                return
            if StatusEnum.running == self.status:
                self.status = StatusEnum.stopping
                with self.request_mutex:
                    ##clear request list
                    self.request_list = []
                ##notify wait thread
                self.request_available.release()
        
        self.main_thread.join()
        with self.status_mutex:
            self.status = StatusEnum.stopped
##        if self.debug:
##            self.logger.info("<%s>channel %d:request %d/%d, signal %d/%d"%(
##                self.logger_name, self.index,
##                self.handled, self.total,
##                self.aquire, self.release))

    def mainProcess(self):
        elapse_list = []
        count_list = []
        while StatusEnum.running == self.status:
            ##wait for signal
            self.request_available.acquire()
            if StatusEnum.running != self.status:
                ##double protect
                break
##            self.aquire += 1
            with self.request_mutex:
                if(0 == len(self.request_list)):
                    ##empty
                    continue
                ##FIFO/pop front
                request_list = self.request_list                
                self.request_list = []
                
            if self.handler:
                total_count = len(request_list)
                for start in range(0, total_count, self.cache):
                    end = start + self.cache
                    if end > total_count:
                        end = total_count
                        
                    if not self.debug:
                        self.handler(self.index, request_list[start:end])
                    else:                    
                        count = end - start
                        begin = datetime.datetime.now()
##                        self.handled += (end - start)
                        self.handler(self.index, request_list[start:end])
##                        self.logger.info("<%s>channel %d:%d request processed"%(
##                            self.logger_name, self.index,
##                            (end - start)))
                        elapse = self.milliseconds(datetime.datetime.now() - begin)
                        elapse_list.append(elapse)
                        count_list.append(count)

        if self.debug:
            process_count = len(elapse_list)
            if 0 == process_count:
                return
            total_count = sum(count_list)
            total_elapse = sum(elapse_list)
            average = total_elapse/process_count
            unit = total_elapse/total_count
            max_elapse = max(elapse_list)
            min_elapse = min(elapse_list)
            for i in range(process_count):
                if max_elapse == elapse_list[i]:
                    max_length = count_list[i]
                if min_elapse == elapse_list[i]:
                    min_length = count_list[i]
            average_length = int(total_count/process_count)
            ability = int(1000/unit)
            self.logger.info("<%s>channel %d statistic:called %d, total request %d, time %.3f ms, %.3f ms/unit(%d request/s)"%(
                self.logger_name, self.index, process_count, total_count, total_elapse, unit, ability))
            self.logger.info("<%s>channel %d statistic:average process in %.3f ms, length %d, max %.3f ms/%d, min %.3f ms/%d"%(
                self.logger_name, self.index, average, average_length, max_elapse, max_length, min_elapse, min_length))
        
    def put(self, request_list):
        """
        put request into queue tail
        """
        with self.request_mutex:
            if len(self.request_list) >= self.max_request:
                if self.debug:
                    self.logger.info("<%s>channel %d:put %d request fail, queue is full"%(
                        self.logger_name, self.index,
                        len(self.request_list)))
                return False
##            if self.debug:
##                self.total += len(request_list)
##                self.release += 1
            self.request_list.extend(request_list)
            self.request_available.release()
        return True
                

if __name__ == '__main__':
    import logging
    import sys
    import time
    import random
    from service.loop_thread import *
    from service.performance_test import *
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)
##    global success
##    success = 0
##    fail = 0
    
    def request_handler(index, request_list):
        success = 0
        with TestUnit("request called"):
            result_list = []        
            for i in request_list:
                success += i
##            print success
    
    duration = 10
    count = 20000
    batch = 200
    repeat = count/batch
##    request = object()
    
    request_list = []
    for i in range(batch):
        request_list.append(1)
    print "request queue"

    max_channel = 5
    name = "put@%d"%batch

    queue_list = []
    for i in range(max_channel):
        queue = RequestQueue(i, request_handler,
                             50,
                             debug = True,
                             logger_name = name)
        queue.start()
        queue_list.append(queue)

    with TestUnit("test1"):
        for i in range(duration):
            for j in range(batch):
                length = int(random.random()*count)
                for k in range(max_channel):
                    with TestUnit(name):
                        queue_list[k].put(request_list[:length])

    for queue in queue_list:
        queue.stop()
        
        
##    pool = SmartPool(max_channel, request_handler, cache = 1000,
##                     debug = True,
##                     logger_name = name)
##    pool.start()
##
##    with TestUnit("test2"):
##        for i in range(duration):
##            for j in range(batch):
##                length = int(random.random()*count)
##                with TestUnit(name):
##                    pool.put(request_list[:length])
##
##        pool.stop()

##    name = "put@%d"%batch
##
##    pool = SmartPool(max_channel, request_handler, debug = True,
##                     logger_name = name)
##    pool.start()
##
##    with TestUnit("test3"):
##        for i in range(duration):
##            for j in range(repeat):
##                with TestUnit(name):
##                    pool.put(request_list)
##
##        pool.stop()

##    child_pool = SmartPool(max_channel, request_handler)
##
##    def resend_handler(index, request_list):
##        with TestUnit("parent called"):
##            result_list = []
##            child_pool.addRequestList(index, request_list)
##        
##    parent_pool = SmartPool(max_channel, resend_handler, fast_cache = 1000)
##    child_pool.start()
##    parent_pool.start()
##    
##    with TestUnit("Recursion"):
##        for i in range(duration):
##            for j in range(count):
##                with TestUnit("put to parent"):
##                    parent_pool.addRequest((j%max_channel), request)
##        time.sleep(0.1)
##        child_pool.stop()
##        parent_pool.stop()

##    ##speed swith
##    high_speed = 3000
##    low_speed = 40
##    interval = 0.1
##    freq = int(1/interval)
##    high_request = high_speed*max_channel/freq
##    low_request = low_speed*max_channel/freq
##
##    fast_request = []
##    for i in range(high_request):
##        fast_request.append(object())
##
##    slow_request = []
##    for i in range(low_request):
##        slow_request.append(object())
##
##    pool = SmartPool(max_channel, request_handler)
##    class Proxy(LoopThread):
##            def __init__(self):
##                LoggerHelper.__init__(self, "proxy")
##                LoopThread.__init__(self, interval)
##                self.high = True
##                self.index = 0
##                
##            def onLoop(self):
##                self.index += 1
##                if self.high:
##                    with TestUnit("put to fast mode"):
##                        pool.addRequestList((self.index%max_channel), fast_request)
##                else:
##                    with TestUnit("put to slow mode"):
##                        pool.addRequestList((self.index%max_channel), slow_request)   
##
##    proxy = Proxy()
##    pool.start()
##    proxy.start()
##    with TestUnit("Recursion"):
##        ##fast
##        proxy.high = True
##        time.sleep(3)
##        
##        ##slow
##        proxy.high = False
##        time.sleep(30)
##
##        ##fast
##        proxy.high = True
##        time.sleep(5)
##
##        ##slow
##        proxy.high = False
##        time.sleep(30)  
##
##    time.sleep(5) 
##    proxy.stop()
##    pool.stop()

##
##    pool = SmartPool(max_channel, request_handler)
##    pool.start()
##
##    with TestUnit("batch2"):
##        for i in range(duration):
##            for j in range(repeat):
##                with TestUnit("batch put/20"):
##                    pool.addRequestList((j%max_channel), request_list)
##            
##    pool.stop()
##
##    pool = SmartPool(max_channel, request_handler)
##    pool.start()
##    batch = 100
##    repeat = count/batch
##
##    with TestUnit("batch3"):
##        for i in range(duration):
##            for j in range(repeat):
##                with TestUnit("batch put/100"):
##                    pool.addRequestList((j%max_channel), request_list)
##
##    pool.stop()
    
    result = PerfomanceManager.get().statistic()
    for entry in result:
        print entry.name, entry.count, entry.average, entry.total
  
    print "finished"    
    
                 
