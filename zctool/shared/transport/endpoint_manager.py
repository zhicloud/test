#!/usr/bin/python
import datetime
from service.time_util import *
from endpoint_session import *

class EndpointManager(object):
    max_timeout = 10
    max_disconnect = 10
    def __init__(self, max_capacity = 1024):
        self.min_id = 1
        self.max_id = self.min_id + max_capacity
        self.next_id = self.min_id
        self.session_map = dict()
        for session_id in range(self.min_id, self.max_id):
            session = EndpointSession(session_id)
            self.session_map[session_id] = session

    def allocate(self):
        for session_id in range(self.next_id, self.max_id):
            if not self.session_map[session_id].isAllocated():
                if self.session_map[session_id].allocate():
                    self.next_id = session_id + 1
                    return session_id

        for session_id in range(self.min_id, self.next_id):
            if not self.session_map[session_id].isAllocated():
                if self.session_map[session_id].allocate():
                    self.next_id = session_id + 1
                    return session_id
        ##allocate fail
        return -1

    def deallocate(self, session_id):
        if (session_id < self.min_id) or (session_id > self.max_id):
            return False
        session = self.session_map[session_id]
        if session.isAllocated():
            session.deallocate()
            return True
        return False

    def getSession(self, session_id):
        if (session_id < self.min_id) or (session_id > self.max_id):
            return None
        session = self.session_map[session_id]
        if session.isAllocated():
            return session
        return None
    
    def isAllocated(self, session_id):
        if (session_id < self.min_id) or (session_id > self.max_id):
            return False
        session = self.session_map[session_id]
        if session.isAllocated():
            return True
        return False
    
    def checkTimeout(self):
        timeout_list = []
        alive_list = []
        disconnect_list = []
        """
        phase 1:timeout ++, if timeout > max_timeout, connected->disconneted, timeout = 0
        phase 2:timeout ++, if timeout > max_disconnect, dealloc session
        """
        current = datetime.datetime.now()
        for session in self.session_map.values():
            if session.isConnected():
                elapse = elapsedSeconds(current - session.timestamp)
                if elapse > self.max_timeout:
                    timeout_list.append(session.session_id)
                else:
                    alive_list.append(session.session_id)
            elif session.isDisconnected():
                elapse = elapsedSeconds(current - session.timestamp)
                if elapse > self.max_disconnect:
                    disconnect_list.append(session.session_id)
                    
        return timeout_list, alive_list, disconnect_list

    def getConnectedEndpoint(self):
        result = []
        for endpoint in self.session_map.values():
            if endpoint.isConnected():
                result.append(endpoint.session_id)

        return result

                
