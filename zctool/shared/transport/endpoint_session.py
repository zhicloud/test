#!/usr/bin/python
import threading
import sys
import datetime
from message_cache_task import *

class EndpointSession(object):
    status_idle = 0
    status_allocated = 1
    status_connected = 2
    status_disconnected = 3
    
    max_serial = sys.maxint
    def __init__(self, session_id):
        self.mutex = threading.RLock()
        self.session_id = session_id
        self.status = EndpointSession.status_idle
        self.timestamp = None
        self.remote_name = ""
        self.remote_ip = ""
        self.remote_port = 0
        self.remote_session = 0
        self.nat_ip = ""
        self.nat_port = 0
        self.cache_map = {}
        self.channel = 0
        self.serial = 1
            
    def allocate(self):
        with self.mutex:
            if EndpointSession.status_idle != self.status:
                return False
            else:
                self.status = EndpointSession.status_allocated
                return True

    def deallocate(self):
        with self.mutex:
            self.status = EndpointSession.status_idle
            self.remote_name = ""
            self.remote_ip = ""
            self.remote_port = 0
            self.remote_session = 0
            self.nat_ip = ""
            self.nat_port = 0
            self.cache_map = {}

    def setStatus(self, status):
        with self.mutex:
            self.status = status        
            
    def isAllocated(self):
        return (EndpointSession.status_idle != self.status)
    
    def isConnected(self):
        return (EndpointSession.status_connected == self.status)        

    def isDisconnected(self):
        return (EndpointSession.status_disconnected == self.status)
    
    def setConnected(self):
        with self.mutex:
            if not self.isAllocated():
                return False
            self.status = EndpointSession.status_connected
            self.timestamp = datetime.datetime.now()

    def setDisconnected(self):
        with self.mutex:
            if not self.isAllocated():
                return False
            self.status = EndpointSession.status_disconnected
            self.timestamp = datetime.datetime.now()
        
    def initial(self, channel):
        with self.mutex:
            if not self.isAllocated():
                return False
            self.channel = channel
            self.timestamp = datetime.datetime.now()
            return True
        
    def allocateSerial(self, count):
        with self.mutex:
            if not self.isAllocated():
                return 0, 0
            begin = self.serial
            end = (begin + count)%self.max_serial
            self.serial = end
            return begin, end        
        
    def setRemoteAddress(
        self, remote_session,
        remote_ip, remote_port,
        nat_ip, nat_port):
        with self.mutex:
            if not self.isAllocated():
                return False
            self.remote_session = remote_session
            self.remote_ip = remote_ip
            self.remote_port = remote_port
            self.nat_ip = nat_ip
            self.nat_port = nat_port
            return True

    def setRemoteName(self, name):
        with self.mutex:
            if not self.isAllocated():
                return False
            self.remote_name = name
            return True
        
    def updateTimestamp(self):
        with self.mutex:
            if not self.isAllocated():
                return False
            self.timestamp = datetime.datetime.now()
            return True
        
    def cacheData(self, serial, index, total, data):
        with self.mutex:
            if not self.isAllocated():
                return False
            if self.cache_map.has_key(serial):
                ##already exist
                task = self.cache_map[serial]
                task.add(index, data)
                return True
            else:
                ##new task
                task = MessageCacheTask()
                task.initial(index, total, data)
                self.cache_map[serial] = task
                return True
            
    def isCacheFinished(self, serial):
        with self.mutex:
            if not self.isAllocated():
                return False
            if not self.cache_map.has_key(serial):
                ##no entry
                return False
            return self.cache_map[serial].finished

    def obtainCachedData(self, serial):
        with self.mutex:
            if not self.isAllocated():
                return None
            if not self.cache_map.has_key(serial):
                ##no entry
                return None
            task = self.cache_map[serial]
            if not task.finished:
                return None
            content =  task.obtain()
            del self.cache_map[serial]
            return content
        
