#!/usr/bin/python
from service.logger_helper import *
from base_session import *

class TransactionManager(LoggerHelper):
    min_session_id = 1
    max_session_id = 1
    def __init__(self, logger_name, min_id = 1, session_count = 1000):
        LoggerHelper.__init__(self, logger_name)
        ##key = task type, value = task
        self.task_map = {}
        ##key = session id, value = session
        self.session_map = {}
        self.min_session_id = min_id
        self.max_session_id = min_id + session_count - 1
        self.session_count = session_count
        self.last_session = min_id - 1
        for session_id in range(self.min_session_id, self.max_session_id + 1):
            session = self.createSession(session_id)
            self.session_map[session_id] = session            
            
        self.info("transaction session created, id %d ~ %d"%(
            self.min_session_id, self.max_session_id))
        
    def addTask(self, task_type, task):
        if self.task_map.has_key(task_type):
            self.warn("add task fail, type %d already exists"%task_type)
            return False
        self.task_map[task_type] = task
        self.info("add task success, type %d"%task_type)

    def createSession(self, session_id):
        """
        create session instance, override by inherited class if necessary
        """
        session = BaseSession(session_id)
        return session

    def allocTransaction(self, task_type):
        current_offset = self.last_session + 1 - self.min_session_id
        for offset in range(self.session_count):
            session_id = self.min_session_id + (current_offset + offset)%self.session_count
            if self.session_map.has_key(session_id):
                session = self.session_map[session_id]
                if not session.is_used:
                    self.last_session = session_id
                    session.occupy(task_type)
                    return session_id
        return None
                
    def deallocTransaction(self, session_id):
        if self.session_map.has_key(session_id):
            self.session_map[session_id].reset()

    def startTransaction(self, session_id, msg):
        if self.session_map.has_key(session_id):
            session = self.session_map[session_id]
            if not session.is_used:
                self.warn("start trans fail, session %d not allocated"%(session_id))
                return
            task_type = session.task_type
            if not self.task_map.has_key(task_type):
                self.warn("start trans fail, invalid task %d for session %d"%(
                    task_type, session_id))
                return
            task = self.task_map[task_type]
            task.initialSession(msg, session)
            task.invokeSession(session)
            if session.isFinished():
                self.deallocTransaction(session_id)

    def processMessage(self, session_id, msg):
        if self.session_map.has_key(session_id):
            session = self.session_map[session_id]
            if not session.is_used:
                self.warn("process trans fail, session %d not allocated"%(session_id))
                return
            task_type = session.task_type
            if not self.task_map.has_key(task_type):
                self.warn("process trans fail, invalid task %d for session %d"%(
                    task_type, session_id))
                return
            task = self.task_map[task_type]
            task.processMessage(msg, session)
            if session.isFinished():
                self.deallocTransaction(session_id)

    def containsTransaction(self, session_id):
        """
        if processing transaction exists
        """
        if self.session_map.has_key(session_id):
            if self.session_map[session_id].is_used:
                return True

        return False

        
        
