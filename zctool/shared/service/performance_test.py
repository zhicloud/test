#!/usr/bin/python
import threading
import datetime

class PerfomanceManager(object):
    instance = None
    initialed = False
    lock = threading.RLock()
    @staticmethod
    def get():
        if not PerfomanceManager.initialed:
            with PerfomanceManager.lock:
                if not PerfomanceManager.initialed:
                    if not PerfomanceManager.instance:
                        ##default contructor
                        PerfomanceManager.instance = PerfomanceManager()
                        PerfomanceManager.initialed = True
                        return PerfomanceManager.instance
        return PerfomanceManager.instance
    
    @staticmethod
    def milliseconds(elapsed):
        return float(elapsed.microseconds + (elapsed.seconds + elapsed.days * 24 * 3600) * 10**6) / 10**3

    class PerformanceUnit(object):
        def __init__(self, name, count, average_elapse, total_elapse,
                    total_length, average_length, unit_average):            
            self.name = name
            self.count = count
            self.average = average_elapse
            self.total = total_elapse
            self.total_length = total_length
            self.average_length = average_length
            self.unit = unit_average            
            
    def __init__(self):
        self.container = []
        self.container_lock = threading.RLock()

    def add(self, name, time, begin, end, count):
        with self.container_lock:
            self.container.append((name, time, begin, end, count))

    def statistic(self):
        with self.container_lock:
            data = {}
            begin_data = {}
            end_data = {}
            length_data = {}
            for item in self.container:
                name, elapse, begin, end, count = item
                if data.has_key(name):
                    data[name].append(elapse)
                    begin_data[name].append(begin)
                    end_data[name].append(end)
                    length_data[name].append(count)
                else:
                    data[name] = [elapse]
                    begin_data[name] = [begin]
                    end_data[name] = [end]
                    length_data[name] = [count]

            result = []
            for name in data.keys():
                data_list = data[name]
                count = len(data_list)
                total_elapse = sum(data_list)
                average_elapse = total_elapse/count
                total_length = sum(length_data[name])
                average_length = float(total_length)/count
                unit_average = total_elapse/total_length
                
                result.append(PerfomanceManager.PerformanceUnit(
                    name, count, average_elapse, total_elapse, 
                    total_length, average_length, unit_average))

            return result

class TestUnit(object):
    def __init__(self, name, count = 1):
        self.name = name
        self.begin = datetime.datetime.now()
        self.count = count
        self.reported = False

    def __del__(self):
        if not self.reported:
            end = datetime.datetime.now()
            ##milliseconds
            ms = PerfomanceManager.milliseconds(end - self.begin)            
            PerfomanceManager.get().add(self.name, ms, self.begin, end, self.count)
    
    def __enter__(self):
        self.begin = datetime.datetime.now()

    def __exit__(self, exc_type, exc_value, traceback):
        end = datetime.datetime.now()
        ##milliseconds
        ms = PerfomanceManager.milliseconds(end - self.begin)            
        PerfomanceManager.get().add(self.name, ms, self.begin, end, self.count)
        self.reported = True

if __name__ == '__main__':
    import time
    import datetime
    import random
    import zlib
    from transport.datagram import *
##    t = TestUnit("t1")
####    with TestUnit("t1") as t:
##    
##    time.sleep(1)
##
##    del t
##
##    with TestUnit("t2", 10) as t:
##        time.sleep(1)
##
##    with TestUnit("t1"):
##        time.sleep(1)
##    count = 100
##    with TestUnit("t3", count) as t:
##        for i in range(count):
##            time = datetime.datetime.now()

    length = 512
    content = ""
    for i in range(length):
        content += chr(int(random.random()*94 + 32))

    count = 100000
    datagram = Datagram()
    datagram.setData(content)
    for i in range(count):
        with TestUnit("datagram crc", count):
            crc = zlib.crc32(datagram.data)&0xFFFFFFFF
        with TestUnit("datagram tostring", count):
            datagram.toString()

    result = PerfomanceManager.get().statistic()
    for entry in result:
        print entry.name, entry.count, entry.average, entry.total_length, entry.average_length, entry.unit
    

