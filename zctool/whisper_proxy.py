#!/usr/bin/python
from service.message_define import *

class WhisperProxy(object):
    def __init__(self, whisper, messager):
        self.whisper = whisper
        self.messager = messager
        ##key = task id, value = session id
        self.sessions = {}
        self.whisper.setObserver(self)
        
    def onTaskStart(self, task_id, task_type):
        if self.sessions.has_key(task_id):
            session_id = self.sessions[task_id]
            event = getEvent(EventDefine.ack)
            event.success = True
            event.session = session_id
            event.setUInt(ParamKeyDefine.task, task_id)
            event.setUInt(ParamKeyDefine.type, task_type)            
            self.messager.sendMessageToSelf(event)
    
    def onTaskProgress(self, task_id, task_type, current, total, percent, speed):
        if self.sessions.has_key(task_id):
            session_id = self.sessions[task_id]
            event = getEvent(EventDefine.report)
            event.success = True
            event.session = session_id
            event.setUInt(ParamKeyDefine.task, task_id)
            event.setUInt(ParamKeyDefine.type, task_type)
            event.setUInt(ParamKeyDefine.level, int(percent))
            event.setUInt(ParamKeyDefine.speed, int(speed))
            self.messager.sendMessageToSelf(event)

    def onTaskSuccess(self, task_id, task_type, file_id):
        if self.sessions.has_key(task_id):
            session_id = self.sessions[task_id]
            event = getEvent(EventDefine.finish)
            event.success = True
            event.session = session_id
            event.setUInt(ParamKeyDefine.task, task_id)
            event.setUInt(ParamKeyDefine.type, task_type)
            event.setString(ParamKeyDefine.uuid, file_id)
            self.messager.sendMessageToSelf(event)

    def onTaskFail(self, task_id, task_type):
        if self.sessions.has_key(task_id):
            session_id = self.sessions[task_id]
            event = getEvent(EventDefine.finish)
            event.success = False
            event.session = session_id
            event.setUInt(ParamKeyDefine.task, task_id)
            event.setUInt(ParamKeyDefine.type, task_type)
            self.messager.sendMessageToSelf(event)

    def startWrite(self, session_id, filename, remote_ip, remote_port):
        file_id = self.whisper.attachFile(filename)
        task_id = self.whisper.allocateWriteTask(file_id, remote_ip, remote_port)
        if -1 == task_id:
            self.whisper.detachFile(file_id)
            return -1
        self.sessions[task_id] = session_id
        self.whisper.startWriteTask(task_id)
        return task_id
