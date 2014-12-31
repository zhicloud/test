#!/usr/bin/python
import threading
import datetime
import logging
import random
from service.service_status import StatusEnum
from cached_queue import *

class CachedPool(object):
    def __init__(self, max_queue, handler,
                 interval = 5, cache = 50, max_request = 1000,
                 debug = False, logger_name = "CachedPool"):
        self.max_queue = max_queue        
        self.queues = []
        for i in range(max_queue):
            ##create channel
            self.queues.append(CachedQueue(
                i, handler,
                interval = interval,
                cache = cache,
                max_request = max_request,
                debug = debug, logger_name = logger_name))

    def start(self):          
        for queue in self.queues:
            if not queue.start():
                return False
        return True

    def stop(self):
        for queue in self.queues:
            queue.stop()

    def put(self, index, request_list):
        if index >= self.max_queue:
            return False
        return self.queues[index].put(request_list)                

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
    print "cached pool"

    max_channel = 5
    name = "put@%d"%batch
    pool = CachedPool(max_channel, request_handler, debug = True,
                     logger_name = name)
    pool.start()

    with TestUnit("test1"):
        for i in range(duration):
            for j in range(batch):
                length = int(random.random()*count)
                for i in range(max_channel):
                    with TestUnit(name):
                        pool.put(i, request_list[:length])

        pool.stop()
        
        
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
    
                 
