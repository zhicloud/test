#!/usr/bin/python
import threading
import datetime
import logging
import random
from service.service_status import StatusEnum
from request_queue import *

class DispatchPool(object):
    def __init__(self, max_queue, handler,
                 interval = 5, cache = 50, max_request = 1000,
                 debug = False, logger_name = "CachedPool"):
        self.max_queue = max_queue
        self.max_capacity = max_queue * max_request
        self.interval = float(interval)/1000
        self.cache = cache*max_queue
        
        self.queues = []
        for i in range(max_queue):
            ##create channel
            self.queues.append(RequestQueue(
                i, handler, cache, max_request = max_request,
                debug = debug, logger_name = logger_name))
            
        self.request_available = threading.Event()
        self.request_list = []
        self.request_lock = threading.RLock()
        self.dispatch_thread = threading.Thread(target=self.dispatchProcess)
        self.status = StatusEnum.stopped
        self.status_mutex = threading.RLock()
        ##for debug
        self.debug = debug        
        if self.debug:
            self.logger_name = logger_name
            self.logger = logging.getLogger(logger_name)
##            self.notify = 0
##            self.timeout = 0
##            self.available = 0
##            self.request = 0
##            self.handled = 0

    def start(self):
        with self.status_mutex:
            if StatusEnum.stopped != self.status:
                return False
            self.status = StatusEnum.running            
            for queue in self.queues:
                if not queue.start():
                    return False
            self.dispatch_thread.start()
            return True

    def stop(self):
        with self.status_mutex:
            if StatusEnum.stopped == self.status:
                return
            if StatusEnum.running == self.status:
                self.status = StatusEnum.stopping
##                with self.request_lock:
##                    self.request_list = []
                ##notify wait thread
                self.request_available.set()
                for queue in self.queues:
                    queue.stop()
        
        self.dispatch_thread.join()
        with self.status_mutex:
            self.status = StatusEnum.stopped

##        if self.debug:
##            self.logger.info("<%s>handled %d/%d, notify %d/%d, timeout %d"%(
##                self.logger_name,
##                self.handled, self.request,
##                self.available, self.notify,
##                self.timeout))

    def put(self, request_list):
        if StatusEnum.running != self.status:
            return False
        with self.request_lock:
            if len(self.request_list) >= self.max_capacity:
                if self.debug:
                    self.logger.info("<%s>put %d request fail, queue is full(%d)"%(
                        self.logger_name, len(self.request_list),
                        self.max_capacity))
                return False
            self.request_list.extend(request_list)
            if self.debug:
                self.logger.info("<%s>put %d request, total %d"%(
                    self.logger_name, len(request_list), len(self.request_list)))
            if len(self.request_list) < self.cache:                
                self.request_available.set()
        return True

    def dispatchProcess(self):
        last_index = 0
        while StatusEnum.running == self.status:
            ##wait for signal
            self.request_available.wait(self.interval)
            if StatusEnum.running != self.status:
                ##double protect
                break
            if self.request_available.isSet():
                ##clear when set
                self.request_available.clear() 
                    
            with self.request_lock:
                if(0 == len(self.request_list)):
                    ##empty
                    continue
                
                ##FIFO/pop front
                request_list = self.request_list
                self.request_list = []
            
            ##dispatch
            total_length = len(request_list)
            if 1 == self.max_queue:
                ##only on channel
                self.queues[0].put(request_list)
                if self.debug:
                    self.logger.info("<%s>dispatch %d request to single channel"%(
                        self.logger_name, len(request_list)))
                continue
            elif total_length <= (self.max_queue * 2):
                index = (last_index)%self.max_queue
                self.queues[index].put(request_list)
                if self.debug:
                    self.logger.info("<%s>direct dispatch %d request to channel %d"%(
                        self.logger_name, len(request_list), index))
                last_index = index + 1
                continue
            else:                
                ##split by channel
                tmp = total_length%self.max_queue
                if 0 != tmp:
                    length = (total_length - tmp + self.max_queue)/self.max_queue
                else:
                    length = total_length/self.max_queue
                
                index = (last_index + 1)%self.max_queue
                for begin in range(0, total_length, length):                    
                    end = begin + length
                    if end > total_length:
                        end = total_length
##                    print "put [%d ~ %d]/%d to %d"%(begin, end, total_length, index)
                    self.queues[index].put(request_list[begin:end])
                    if self.debug:
                        self.logger.info("<%s>seg dispatch %d request to channel %d, [%d ~ %d]/%d"%(
                            self.logger_name, (end - begin), index,
                            begin, end, total_length))
                        
                    index = (index + 1)%self.max_queue
                    
                last_index = index + 1

                

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

    lock = threading.RLock()
    handled = 0
    def request_handler(index, request_list):
        global handled
        with lock:
            handled += len(request_list)
            time.sleep(0.002)
    
    duration = 5
    count = 20000
    batch = 200
    repeat = count/batch
##    request = object()
    
    request_list = []
    for i in range(count):
        request_list.append(1)
    print "dispatch pool"

    max_channel = 4
    name = "put@%d"%batch
    pool = DispatchPool(max_channel, request_handler, max_request = 10000,
                        debug = True, logger_name = name)
    pool.start()

    handled = 0
    put = 0
    batch = 10
    with TestUnit("test1"):
        for i in range(duration):
            for j in range(batch):
##                length = 9
                length = int(random.random()*200)
                with TestUnit(name):
                    if not pool.put(request_list[:length]):
##                        print "put fail"
                        pass
                    else:
                        put += length

            time.sleep(0.01)

        time.sleep(1)
        pool.stop()
    print "handled %d/%d"%(handled, put)
        
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
    
                 
