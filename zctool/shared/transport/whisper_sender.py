#!/usr/bin/python
import io
import os
import os.path
import datetime
import logging
##from service.performance_test import *

class BlockStatusEnum(object):
    idle = 0
    process = 1
    finish = 2
    fail = 3

class DataBlock(object):
    def __init__(self):
        self.strip = 0
        self.block = 0
        self.data = ""
        self.status = BlockStatusEnum.idle
        self.counter = 0
        self.max_counter = 0
        self.retry = 0
        
    def isIdle(self):
        return (self.status == BlockStatusEnum.idle)
    
    def isProcess(self):
        return (self.status == BlockStatusEnum.process)
    
    def isFinish(self):
        return (self.status == BlockStatusEnum.finish)

    def isFail(self):
        return (self.status == BlockStatusEnum.fail)

    def setStatus(self, status):
        self.status = status

class WhisperSender(object):
    max_timeout = 50
    min_timeout = 5
    max_retry = 10
    def __init__(self, filename,
                 file_size, block_size, strip_length): 
        self.filename = filename
        self.file_size = file_size
        self.block_size = block_size
        self.strip_length = strip_length
        self.remote_port = []
        self.cache_data = []
        ##key = strip id, value = channel index
        self.strip_index = {}
        self.strips = []
        self.sent = 0
        self.finished = False
        self.cache_count = 0
        self.cache_pos = 0
        ##block count in process
        self.process = 0
        ##speed
        self.last_sent = 0
        self.last_time = datetime.datetime.now()
        
    def prepare(self, cache_count):
        if not os.path.exists(self.filename):
            return False
        buffer_size = self.block_size * self.strip_length
        file_object = io.FileIO(self.filename, "r+")
        self.reader = io.BufferedRandom(file_object, buffer_size)
        
        self.cache_data = []
        self.strip_index = {}
        self.cache_count = cache_count
        for i in range(self.cache_count):
            self.cache_data.append([])
            
        ##slice strip
        strip_size = self.block_size * self.strip_length
        strip_count = 0
        remainder = self.file_size%strip_size
        if 0 == remainder:
            strip_count = self.file_size/strip_size
        else:
            strip_count = ((self.file_size - remainder) /strip_size) + 1            

        ##reverse
        for strip in range(strip_count):
            self.strips.append(strip)
        self.strips.reverse()
        ##prepare all cache
        for cache_index in range(self.cache_count):
            if 0 != len(self.strips):
                self.loadStripToCache(cache_index)
        return True

    def complete(self, strip_id, block_id):
        if not self.strip_index.has_key(strip_id):
            return False
        cache_index = self.strip_index[strip_id]
        data_list = self.cache_data[cache_index]
        count = len(data_list)
        block_offset = block_id%self.strip_length
        data_block = data_list[block_offset]
        if (data_block.strip == strip_id) and (data_block.block == block_id):
            if data_block.isIdle() or data_block.isFinish():
                return False
            self.sent += len(data_block.data)
            self.process -= 1
            data_block.setStatus(BlockStatusEnum.finish)
            ##check finish
            success = 0
            for check_block in data_list:
                if check_block.isFinish():
                    success += 1
            if success == count:
                ##head cache finish
                if self.cache_pos == cache_index:
                    ##move head
                    self.cache_pos = (self.cache_pos + 1)%self.cache_count
                ##complete,remove strip
                del self.strip_index[strip_id]
                ##load next strip
                if 0 != len(self.strips):
                    self.loadStripToCache(cache_index)                    
                
            return True
        else:
            return False
    
    def loadStripToCache(self, cache_index):
        if 0 == len(self.strips):
            return False
        self.cache_data[cache_index] = []
        strip_id = self.strips.pop()
        start_pos = strip_id * self.block_size * self.strip_length
        start_block = strip_id * self.strip_length
        self.reader.seek(start_pos)
        ##bind strip
        self.strip_index[strip_id] = cache_index
        for index in range(self.strip_length):
            ##read all strip
            data = self.reader.read(self.block_size)
            if 0 == len(data):
                ##eof
                break
            data_block = DataBlock()
            data_block.strip = strip_id
            data_block.block = (start_block + index)
            data_block.data = data
            data_block.max_counter = self.min_timeout
            self.cache_data[cache_index].append(data_block)                     
##        logging.info("<Whisper>debug:cache reloaded, cache index %d"%(
##            cache_index))
        return True

    def fetchData(self, max_process):
        """
        @return:list of data_block
        """
        result = []
        max_count = max_process - self.process
##        logging.info("<Whisper>debug:fetch %d, current %d / %d block"%(
##            max_count, self.process, max_process))
        if max_count <= 0:
            return result
        count = 0
        for i in range(self.cache_count):
            cache_index = (i + self.cache_pos)%self.cache_count
            data_list = self.cache_data[cache_index]
            for block in data_list:
                if block.isIdle():
                    block.setStatus(BlockStatusEnum.process)
                    self.process += 1
                    result.append(block)
                    if len(result) >= max_count:
                        return result
        return result

    def fetchFailedData(self, cache_index):
        result = []
        data_list = self.cache_data[cache_index]
        for block in data_list:
            if block.isFail():
                block.setStatus(BlockStatusEnum.process)
                result.append(block)
        return result
        
    def isFinished(self):
        if self.finished:
            return True
        if 0 != len(self.strips):
            return False
        ##check when no more strips        
        left = 0
        for data_list in self.cache_data:
            for data_block in data_list:
                if not data_block.isFinish():
                    left += 1

        if 0 == left:
            self.finished = True
            return True
        else:
            return False

    def close(self):
        self.reader.close()

    def check(self):
        """
        @return:list of retry cache index, list of failed cache index
        """    
        retry_list = []
        fail_list = []
        for cache_index in range(self.cache_count):
            cache_data = self.cache_data[cache_index]
            for data_block in cache_data:
                if data_block.isProcess():
                    data_block.counter += 1
                    if data_block.counter >= data_block.max_counter:
                        ##timeout
                        data_block.counter = 0
                        data_block.retry += 1
                        new_timeout = self.min_timeout + pow(data_block.retry, 2) * 10
                        if new_timeout > self.max_timeout:
                            new_timeout = self.max_timeout
                        data_block.max_counter = new_timeout
                        data_block.setStatus(BlockStatusEnum.fail)
                        if data_block.retry >= self.max_retry:
                            logging.error("<WhisperSender>block %d exceed max retry %d/%d"%(
                                data_block.block, data_block.retry, self.max_retry))
                            fail_list.append(cache_index)
                            ##next channel
                            break
                        else:
                            if cache_index not in retry_list:
                                retry_list.append(cache_index)
                            ##next block
                            continue
        return retry_list, fail_list
    
    def statistic(self):
        """
        @return:sent, total, percentage, speed
        """
        timestamp = datetime.datetime.now()
        processed = self.sent - self.last_sent
        percentage = float(self.sent)*100/self.file_size
        if processed <= 0:
            return self.sent, self.file_size, percentage, 0
        diff = timestamp - self.last_time
        elapse_seconds = diff.seconds + float(diff.microseconds)/1000000
        if elapse_seconds <= 0:
            return self.sent, self.file_size, percentage, 0
        speed = float(processed)/elapse_seconds##bps
        return self.sent, self.file_size, percentage, speed
        
        
