#!/usr/bin/python
import logging

class TaskTypeEnum(object):
    write = 0
    read = 1
    
class WhisperTask(object):
    def __init__(self, task_id, task_type, file_id, filename, proxy):
        self.task_id = task_id
        self.task_type = task_type
        self.file_id = file_id
        self.filename = filename
        self.proxy = proxy
        self.finished = False
        self.window_size = 1
        ##congestion control
        self.ack_counter = 0
        ##decreate trigger
        self.max_lost = 3
        self.window_threhold = 128
        self.control_step = 1

    def setWindowSize(self, window_size):
        self.window_size = window_size

    def getWindowSize(self):
        return self.window_size

    def onDataAck(self):
        ##congest control
        self.ack_counter += 1
        if self.ack_counter >= self.getWindowSize():
            self.increaseWindow()

    def onDataLost(self, count):        
        if count >= self.max_lost:
            self.decreaseWindow()

    def increaseWindow(self):
        current = self.getWindowSize()
        if current < self.window_threhold:
            new_window = current * 2
            if new_window > self.window_threhold:
                new_window = self.window_threhold
        else:
            new_window = current + self.control_step
##        logging.info("<Whisper>debug:increase window to %d / %d"%(
##            new_window, self.window_threhold))
        self.setWindowSize(new_window)
        self.ack_counter = 0

    def decreaseWindow(self):
        current = self.getWindowSize()
        self.window_threhold = current
        new_window = current - current/3
##        logging.info("<Whisper>debug:decrease window to %d / %d"%(
##            new_window, self.window_threhold))
        self.setWindowSize(new_window)
        self.ack_counter = 0        

    def sendCommand(self, command, remote_ip, remote_port):
        return self.proxy.sendCommand(command, remote_ip, remote_port)

    def sendData(self, request_list):
        """
        @request_list:list of (data msg, remote_ip, remote_port)
        """
        return self.proxy.sendData(request_list)

    def onStart(self):
        self.proxy.onTaskStart(self.task_id, self.task_type)

    def onProgress(self, current, total, percent, speed):
        self.proxy.onTaskProgress(self.task_id, self.task_type,
                                  current, total, percent, speed)

    def onSuccess(self, file_id):
        self.proxy.onTaskSuccess(self.task_id, self.task_type,
                                 file_id)

    def onFail(self):
        self.proxy.onTaskFail(self.task_id, self.task_type)

    def isWriteTask(self):
        return (TaskTypeEnum.write == self.task_type)

    def isReadTask(self):
        return (TaskTypeEnum.read == self.task_type)

    def handleData(self, command, sender_ip, sender_port):
        pass
    
    def handleDataAck(self, command, sender_ip, sender_port):
        pass
    
    def handleFinish(self, command, sender_ip, sender_port):
        pass
    
    def handleFinishAck(self, command, sender_ip, sender_port):
        pass

    def check(self):
        pass
