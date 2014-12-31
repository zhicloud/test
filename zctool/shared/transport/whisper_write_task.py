#!/usr/bin/python
import io
import os
import os.path
import logging
import binascii
from whisper_task import *
from whisper_command import *
from whisper_receiver import *
from whisper_sender import *

class WhisperWriteTask(WhisperTask):
    max_timeout = 100
    ##in seconds
    report_interval = 2
    def __init__(self, task_id, file_id, filename, proxy,
                 file_size, block_size, strip_length,
                 remote_ip, remote_port):
        WhisperTask.__init__(self, task_id, TaskTypeEnum.write, file_id, filename, proxy)
        self.file_size = file_size
        self.block_size = block_size
        self.strip_length = strip_length
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.remote_data_port = []
        self.remote_data_port_count = 0
        self.remote_task = 0
        self.remote_file = ""
        self.sender = None
        self.receiver = None
        self.counter = 0
        self.check_counter = 0
        
    def setRemoteTask(self, task_id):
        self.remote_task  = task_id

    def setRemoteFile(self, file_id):
        self.remote_file = file_id
        
    def connect(self, max_channel):
        command = WriteCommand(self.task_id,
                               self.file_size, self.block_size,
                               self.strip_length, max_channel)
        return self.sendCommand(command, self.remote_ip, self.remote_port)

    def createReceiver(self):
        self.receiver = WhisperReceiver(self.filename, self.file_size, self.block_size, self.strip_length)
        return self.receiver.prepare()

    def createSender(self, port_list):
        self.sender = WhisperSender(self.filename, self.file_size, self.block_size, self.strip_length)
        self.remote_data_port = port_list
        self.remote_data_port_count = len(port_list)
        return self.sender.prepare(len(port_list) * 4)

    def startTransport(self):
        data_list = self.sender.fetchData(self.getWindowSize())
        request_list = []
        for data_block in data_list:
            data_size = len(data_block.data)
            crc = binascii.crc32(data_block.data)&0xFFFFFFFF
            remote_port = self.remote_data_port[(data_block.block%self.remote_data_port_count)]
            
            msg = Data(self.task_id, self.remote_task,
                       data_block.strip, data_block.block,
                       data_size, crc, data_block.data)
            request_list.append((msg, self.remote_ip, remote_port))
##            logging.info("<Whisper>debug:strart transport, send block %d"%(data_block.block))
            
        self.sendData(request_list)
        self.onStart()
        return True


    def handleData(self, command, sender_ip, sender_port):
        self.counter = 0
        ##send ack first
        ack = DataAck(self.remote_task, command.strip_id, command.block_id)
        self.sendData([(ack, sender_ip, sender_port)])
##        logging.info("<Whisper>debug:block received, block %d"%(command.block_id))
        return self.receiver.writeData(command.strip_id, command.block_id, command.data)
            
    def handleDataAck(self, command, sender_ip, sender_port):
        self.counter = 0
        self.onDataAck()
        
        strip_id = command.strip_id
        block_id = command.block_id
        if not self.sender.complete(strip_id, block_id):
##            logging.error("<Whisper>task[%d]:can't complete block %d/%d"%(
##                self.task_id, strip_id, block_id))
            return False
##        logging.info("<Whisper>debug:block ack, block %d"%(block_id))
        if self.sender.isFinished():
            finish = Finish(self.task_id, self.remote_task)
            self.sendCommand(finish, self.remote_ip, self.remote_port)
            logging.info("<Whisper>task[%d]:finished, notify remote receiver"%(
                self.task_id))
            return True
        data_list = self.sender.fetchData(self.getWindowSize())
        request_list = []
        for data_block in data_list:
            data_size = len(data_block.data)
            crc = binascii.crc32(data_block.data)&0xFFFFFFFF
            remote_port = self.remote_data_port[(data_block.block%self.remote_data_port_count)]
            
            msg = Data(self.task_id, self.remote_task,
                       data_block.strip, data_block.block,
                       data_size, crc, data_block.data)
            request_list.append((msg, self.remote_ip, remote_port))
##            logging.info("<Whisper>debug:send next block, send block %d"%(data_block.block))
            
        self.sendData(request_list)
        return True
                
    def handleFinish(self, command, sender_ip, sender_port):        
        if self.receiver.isFinished():
            self.finished = True
            ack = FinishAck(self.remote_task)
            self.sendCommand(ack, self.remote_ip, self.remote_port)
            logging.info("<Whisper>task[%d]:receiver finished"%(
                self.task_id))
            return True
        else:
            logging.info("<Whisper>task[%d]:recv finish event, but not all data received"%(
                self.task_id))
            return False

    def handleFinishAck(self, command, sender_ip, sender_port):
        self.sender.close()
        self.finished = True
        logging.info("<Whisper>task[%d]:sender finished"%(
            self.task_id))
        self.onSuccess(self.remote_file)
        return True

    def check(self):
        self.counter += 1
        if self.counter > self.max_timeout:
            logging.info("<Whisper>task[%d]:task timeout fail"%(
                    self.task_id))
            self.onFail()
            return False
        ##receiver
        if self.receiver is not None:
            if not self.receiver.check():
                ##check fail
                logging.info("<Whisper>task[%d]:receiver check fail"%(
                    self.task_id))
                self.onFail()
                return False
        ##sender
        if self.sender is not None:            
            if self.sender.isFinished():
                finish = Finish(self.task_id, self.remote_task)
                self.sendCommand(finish, self.remote_ip, self.remote_port)
                logging.info("<Whisper>task[%d]:notify remote receiver when check"%(
                    self.task_id))
                return True
            retry_list, fail_list = self.sender.check()
            if 0 != len(fail_list):
                ##send fail
                logging.info("<Whisper>task[%d]:sender check fail"%(
                    self.task_id))
                self.onFail()
                return False
            elif 0 != len(retry_list):
                lost = 0
                ##retry
                for cache_index in retry_list:
                    data_list = self.sender.fetchFailedData(cache_index)
                    lost += len(data_list)
                    request_list = []
                    for data_block in data_list:
                        data_size = len(data_block.data)
                        crc = binascii.crc32(data_block.data)&0xFFFFFFFF
                        remote_port = self.remote_data_port[(data_block.block%self.remote_data_port_count)]
                        
                        msg = Data(self.task_id, self.remote_task,
                                   data_block.strip, data_block.block,
                                   data_size, crc, data_block.data)
                        request_list.append((msg, self.remote_ip, remote_port))
##                        logging.warn("<Whisper>task[%d]:resend block %d"%(
##                            self.task_id, data_block.block))
                        
                    self.sendData(request_list)
##                logging.warn("<Whisper>task[%d]:resend %d lost block"%(
##                    self.task_id, lost))
                self.onDataLost(lost)
                    
            ##check progress
            self.check_counter += 1
            self.check_counter = self.check_counter%(self.report_interval * 10)
            if 0 == self.check_counter:
                sent_bytes, total_bytes, percentage, speed = self.sender.statistic()
                self.onProgress(sent_bytes, total_bytes, percentage, speed)

        return True
