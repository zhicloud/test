#!/usr/bin/python
import threading
from send_task import *
from service.performance_test import *

class SendTaskManager(object):
    def __init__(self, max_capacity = 1024, max_timeout = 5, max_retry = 3):
        self.min_id = 1
        self.max_id = self.min_id + max_capacity
        self.max_timeout = max_timeout
        self.max_retry = max_retry
        
        self.task_map = dict()
        self.timeout = dict()
        self.retry = dict()
        
        self.lock = threading.RLock()
        for task_id in range(self.min_id, self.max_id):
            task = SendTask(task_id)
            self.task_map[task_id] = task
            self.timeout[task_id] = 0
            self.retry[task_id] = 0

        self.available = list(self.task_map.keys())
        self.used = set()
        
    def allocate(self, count):
        with self.lock:                
            result = []
            if count > len(self.available):
                return result

            result = self.available[:count]
            for task_id in result:
                self.task_map[task_id].allocate()
                self.timeout[task_id] = 0
                self.retry[task_id] = 0                

            self.used.update(result)
            del self.available[:count]
            return result

    def deallocate(self, task_list):
        with self.lock:
            result = []
            for task_id in task_list:
                if (task_id < self.min_id) or (task_id > self.max_id):
                    continue
                if self.task_map[task_id].isAllocated():
                    self.task_map[task_id].deallocate()
                    self.timeout[task_id] = 0
                    self.retry[task_id] = 0
                    result.append(task_id)
                    
            self.used.difference_update(result)  
            self.available.extend(result)

    def getTask(self, task_id):
        if (task_id < self.min_id) or (task_id > self.max_id):
            return None
        if self.task_map[task_id].isAllocated():
            return self.task_map[task_id]
        return None
    
    def initial(self, task_id, content, remote_address):
        if (task_id < self.min_id) or (task_id > self.max_id):
            return False
        return self.task_map[task_id].initial(content, remote_address)
        
    def checkTimeout(self):
        with self.lock:
            timeout_task = []
            deallocate_task = []
                
            for task_id in self.used:
                self.timeout[task_id] += 1
                if self.timeout[task_id] >= self.max_timeout:                        
                    self.timeout[task_id] = 0
                    self.retry[task_id] += 1
                    if self.retry[task_id] > self.max_retry:
                        ##need remove
                        deallocate_task.append(task_id)
                    else:
                        ##need retry
                        timeout_task.append(task_id)
            return timeout_task, deallocate_task

if __name__ == '__main__':
    import time
##    import logging
    from service.loop_thread import *
    
##    handler = logging.StreamHandler(sys.stdout)
##    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
##    handler.setFormatter(formatter)
##    handler.setLevel(logging.DEBUG)
##    root = logging.getLogger()
##    root.addHandler(handler)
##    root.setLevel(logging.DEBUG)

    interval = 1
    count = 5000
    batch = 50
    repeat = count/batch
    max_channel = 5
    duration = 20
    
    manager = SendTaskManager(count * max_channel * interval * 2)
    

    class Proxy(LoopThread):
        def __init__(self):
            LoggerHelper.__init__(self, "proxy")
            LoopThread.__init__(self, interval)
            self.success = 0
            self.fail = 0
            
        def onLoop(self):
            id_list = []
            for i in range(repeat):
                result = manager.allocate(batch)
                if 0 != len(result):
                    id_list.extend(result)
                    self.success += len(result)
                else:
                    self.fail += batch

            manager.deallocate(id_list)
           

    print "test start"
    channels = []   
    for i in range(max_channel):
        channels.append(Proxy())
        
    with TestUnit("batch test"):
        for channel in channels:
            channel.start()
            
        for i in range(duration):
            manager.checkTimeout()            
            time.sleep(1)
            
        success = 0
        fail = 0        
        for channel in channels:
            channel.stop()
            success += channel.success
            fail += channel.fail

    print "success %d, fail %d"%(success, fail)
    result = PerfomanceManager.get().statistic()
    for entry in result:
        print entry.name, entry.count, entry.average, entry.max, entry.min, entry.total
    print "test finish"
    
        
