#!/usr/bin/python
import logging
import uuid
import os
import os.path
import threading
import binascii
import socket
import sys
import shutil
import select
import errno

from whisper_write_task import *
from whisper_read_task import *
from whisper_task import *
from whisper_command import *
from service.service_status import StatusEnum
from service.timed_invoker import *
from service.serialize import *
if "win32" == sys.platform:
    from packet_handler_win import *
else:
    from packet_handler import *

class WhisperEvent(object):
    start = 0
    progress = 1
    success = 2
    fail = 3
    def __init__(self):
        self.task_id = 0
        self.task_type = 0
        self.event_type = WhisperEvent.start
        self.file_id = ""
        self.current = 0
        self.total = 0
        self.percent = 0
        self.speed = 0
        

class Whisper(object):
    min_task_id = 1
    max_task_id = 500
    block_size = 32*1024
    strip_length = 64
    min_port = 10000
    max_port = 20000
    max_queue = 10000
    bufsize = 2*1024*1024
    threhold = 5
    max_batch = 20
    slow_interval = 1
    ##20 ms
    normal_interval = 0.02
    ##5ms
    fast_interval = 0.005
    ##100ms
    check_interval = 0.1
    def __init__(self, listen_ip, data_channel, tmp_path, logger_name):        
        self.logger = logging.getLogger(logger_name)
        self.tmp_path = tmp_path
        
        if os.path.exists(self.tmp_path):
            shutil.rmtree(self.tmp_path)
        os.mkdir(self.tmp_path)
        self.logger.info("<Whisper>temp file path '%s' created"%(self.tmp_path))

        self.listen_ip = listen_ip
        self.listen_port = 0
        
        ##key = file id, value = file name
        self.files = {}
        self.file_lock = threading.RLock()
        
        ##key = task id, value = whisper task
        self.tasks = {}
        self.task_lock = threading.RLock()
        
        ##list of data port
        self.channel_count = data_channel
        self.control_channel = None
        
        ##command queue
        self.status = StatusEnum.stopped
        self.status_mutex = threading.RLock()
        ##block after create
        self.message_available = threading.Event()
        self.message_queue = []
        self.message_lock = threading.RLock()
        self.main_thread = threading.Thread(target=self.mainProcess)
        self.invoker = TimedInvoker(self.onScheduleCheck, self.check_interval)
        self.observer = None
        self.system_handler = None        
        self.data_handler = None
        
        self.notify_queue = []
        self.notify_lock = threading.RLock()
        self.notify_thread = threading.Thread(target=self.notifyProcess)

        self.unserialize_queue = []
        self.unserialize_lock = threading.RLock()
        self.unserialize_available = threading.Event()
        self.unserialize_thread = threading.Thread(target=self.unserializeProcess)
        self.exit_event = threading.Event()
        
    def setListenIP(self, ip):
        self.listen_ip = ip
        
    def getListenIP(self):
        return self.listen_ip
        
    def getControlPort(self):
        return self.system_handler.getDefaultPort()

    def setObserver(self, observer):
        self.observer = observer

    def initial(self):
        buf_size = self.strip_length * self.block_size
        self.system_handler = PacketHandler(self.listen_ip, self.min_port, 1,
                                            self.onPacketReceived, buf_size)
        if not self.system_handler.initial():
            self.logger.error("<Whisper>initial system handler fail")
            return False
        
        self.data_handler = PacketHandler(self.listen_ip, self.min_port + 1, self.channel_count,
                                          self.onPacketReceived, buf_size)
        if not self.data_handler.initial():
            self.logger.error("<Whisper>initial data handler fail")
            return False        

        return True
    
    def start(self):
        with self.status_mutex:
            if StatusEnum.stopped != self.status:
                return False
            self.status = StatusEnum.running            
            self.main_thread.start()
            self.system_handler.start()
            self.data_handler.start()
            self.unserialize_thread.start()
            self.notify_thread.start()
            self.invoker.start()
            return True

    def stop(self):
        with self.status_mutex:
            if StatusEnum.stopped == self.status:
                return
            if StatusEnum.running == self.status:
                self.status = StatusEnum.stopping
                with self.message_lock:
                    ##clear request list
                    self.message_queue = []
                    
                self.message_available.set()
                self.unserialize_available.set()
                self.exit_event.set()                
                self.invoker.stop()
                self.data_handler.stop()
                self.system_handler.stop()

        self.notify_thread.join()
        self.unserialize_thread.join()
        self.main_thread.join()
        with self.status_mutex:
            self.status = StatusEnum.stopped

##        result = PerfomanceManager.get().statistic()
##        for entry in result:
##            self.logger.info("<Statistic>%s:%d call(s), unit %.2f ms, avg %.2f ms, total %.2f ms, len %.1f/ %d"%(
##                entry.name, entry.count, entry.unit, entry.average, entry.total,
##                entry.average_length, entry.total_length))

    def onScheduleCheck(self):
        event = Check()
        self.putToMessage([(event, "", 0)])

    def putToMessage(self, message_list):
        """
        @message_list:list of (msg, remote_ip, remote_port)
        """        
        with self.message_lock:
            if len(self.message_queue) >= self.max_queue:
                return False
            self.message_queue.extend(message_list)
            if len(self.message_queue) < self.threhold:
                self.message_available.set()
        return True
        
    def mainProcess(self):
        self.logger.info("<Whisper>main process started")
        while StatusEnum.running == self.status:
            ##wait for signal
            self.message_available.wait(self.normal_interval)
            if StatusEnum.running != self.status:
                ##double protect
                break
            if self.message_available.isSet():
                ##clear when set
                self.message_available.clear() 
            with self.message_lock:
                if(0 == len(self.message_queue)):
                    ##empty
                    continue
                ##FIFO/pop front
                message_queue = self.message_queue
                self.message_queue = []

            for packet in message_queue:
                command = packet[0]
                sender_ip = packet[1]
                sender_port = packet[2]
                self.handleCommand(command, sender_ip, sender_port)
        self.logger.info("<Whisper>main process stopped")

    def notifyProcess(self):
        while StatusEnum.running == self.status:
            ##wait for signal
            self.exit_event.wait(self.check_interval)
            if StatusEnum.running != self.status:
                ##double protect
                break
            with self.notify_lock:
                if(0 == len(self.notify_queue)):
                    ##empty
                    continue
                ##FIFO/pop front
                notify_queue = self.notify_queue
                self.notify_queue = []
                
            if self.observer is None:
                continue
            
            for event in notify_queue:
                ##notify event
                if event.event_type == WhisperEvent.start:
                    self.observer.onTaskStart(event.task_id, event.task_type)
                    
                elif event.event_type == WhisperEvent.progress:
                    self.observer.onTaskProgress(event.task_id, event.task_type,
                                                 event.current, event.total,
                                                 event.percent, event.speed)
                elif event.event_type == WhisperEvent.success:
                    self.observer.onTaskSuccess(event.task_id, event.task_type,
                                                event.file_id)
                elif event.event_type == WhisperEvent.fail:
                    self.observer.onTaskFail(event.task_id, event.task_type)
                        
    def putToSystemSend(self, msg, remote_ip, remote_port):
        packet = self.serializeToPacket(msg)
        if packet is None:
            return False
        self.system_handler.sendPacket(packet, remote_ip, remote_port)
            
    def putToDataSend(self, request_list):
        """
        @request_list:list of (data msg, remote_ip, remote_port)
        """        
        packet_list = []
        for request in request_list:
            msg = request[0]
            remote_ip = request[1]
            remote_port = request[2]
            packet = self.serializeToPacket(msg)
            if packet is None:
                continue
            packet_list.append((packet, remote_ip, remote_port))
        request_length = len(packet_list)
        if 0 == request_length:
            return False
        self.data_handler.sendPacketList(packet_list)
            
    def serializeToPacket(self, msg):
        stream = io.BytesIO()
        writeVariant(stream, msg.type)
        if msg.type == CommandTypeEnum.write:            
            writeVariant(stream, msg.sender)
            writeVariant(stream, msg.size)
            writeVariant(stream, msg.block_size)
            writeVariant(stream, msg.strip_length)
            writeVariant(stream, msg.channel)
        elif msg.type == CommandTypeEnum.write_ack:
            writeVariant(stream, msg.sender)
            writeVariant(stream, msg.receiver)
            writeString(stream, msg.file_id)
            port_count = len(msg.port_list)
            writeVariant(stream, port_count)
            for port in msg.port_list:
                writeVariant(stream, port)
        elif msg.type == CommandTypeEnum.finish:
            writeVariant(stream, msg.sender)            
            writeVariant(stream, msg.receiver)            
        elif msg.type == CommandTypeEnum.finish_ack:
            writeVariant(stream, msg.sender)
            
        elif msg.type == CommandTypeEnum.read:            
            writeVariant(stream, msg.receiver)
            writeString(stream, msg.file_id)
            port_count = len(msg.port_list)
            writeVariant(stream, port_count)
            for port in msg.port_list:
                writeVariant(stream, port)                

        elif msg.type == CommandTypeEnum.read_ack:
            writeVariant(stream, msg.sender)
            writeVariant(stream, msg.receiver)
            writeVariant(stream, msg.size)
            writeVariant(stream, msg.block_size)
            writeVariant(stream, msg.strip_length)
            
        elif msg.type == CommandTypeEnum.ready:          
            writeVariant(stream, msg.sender)
        elif msg.type == CommandTypeEnum.data:
            writeVariant(stream, msg.sender)
            writeVariant(stream, msg.receiver)
            writeVariant(stream, msg.strip_id)
            writeVariant(stream, msg.block_id)
            writeVariant(stream, msg.size)
            writeVariant(stream, msg.crc)
            writeString(stream, msg.data)
        elif msg.type == CommandTypeEnum.data_ack:
            writeVariant(stream, msg.sender)
            writeVariant(stream, msg.strip_id)
            writeVariant(stream, msg.block_id)
        else:
            stream.close()
            self.logger.warn("<Whisper>unsupport message type %d in control channel"%(
                msg.type))
            return None
        
        data = stream.getvalue()
        stream.close()
        return data 
                 
    def unserializeProcess(self):
        while StatusEnum.running == self.status:
            ##wait signal
            self.unserialize_available.wait(self.normal_interval)
            if StatusEnum.running != self.status:
                ##double protect
                break
            if self.unserialize_available.isSet():
                self.unserialize_available.clear()
            
            ##check anyway
            with self.unserialize_lock:
                if(0 == len(self.unserialize_queue)):
                    ##empty
                    continue
                ##FIFO/pop front
                unserialize_queue = self.unserialize_queue
                self.unserialize_queue = []

            ##unserilize
            result = []
            for request in unserialize_queue:
                ##(data, remote_ip, remote_port)
                data = request[0]
                remote_ip = request[1]
                remote_port = request[2]
                msg = self.unserialFromPacket(data)
                if msg is None:
                    ##unserialize fail
                    continue
                result.append((msg, remote_ip, remote_port))

            if 0 != len(result):
                self.putToMessage(result)                

    def onPacketReceived(self, message_list):
        self.putToUnserialize(message_list)
                                            
    def putToUnserialize(self, packet_list):
        with self.unserialize_lock:
            current_length = len(self.unserialize_queue)
            if current_length < self.max_queue:
                self.unserialize_queue.extend(packet_list)
                current_length = len(self.unserialize_queue)
                if (current_length < self.threhold) or (current_length > self.max_batch):
                    self.unserialize_available.set()
                return True
            else:
                self.warn("<Whisper>unserialize queue is full, %d / %d"%(
                    current_length, self.max_queue))
                return False

    def unserialFromPacket(self, raw_data):
        stream = io.BytesIO(raw_data)
        msg_type = readVariant(stream)
        if msg_type == CommandTypeEnum.write:
            sender = readVariant(stream)
            size = readVariant(stream)
            block_size = readVariant(stream)
            strip_length = readVariant(stream)
            channel = readVariant(stream)           
            msg = WriteCommand(sender, size,
                               block_size, strip_length,
                               channel)
            
        elif msg_type == CommandTypeEnum.write_ack:
            sender = readVariant(stream)
            receiver = readVariant(stream)
            file_id = readString(stream)
            port_count = readVariant(stream)
            port_list = []
            for i in range(port_count):
                port_list.append(readVariant(stream))
                
            msg = WriteAck(sender, receiver, file_id, port_list)
            
        elif msg_type == CommandTypeEnum.finish:
            sender = readVariant(stream)
            receiver = readVariant(stream)
            msg = Finish(sender, receiver)            
        elif msg_type == CommandTypeEnum.finish_ack:
            sender = readVariant(stream)
            msg = FinishAck(sender)            
        elif msg_type == CommandTypeEnum.read:
            receiver = readVariant(stream)
            file_id = readString(stream)
            port_count = readVariant(stream)
            port_list = []
            for i in range(port_count):
                port_list.append(readVariant(stream))
                
            msg = Read(receiver, file_id, port_list)            
            
        elif msg_type == CommandTypeEnum.read_ack:
            sender = readVariant(stream)
            receiver = readVariant(stream)
            size = readVariant(stream)
            block_size = readVariant(stream)
            strip_length = readVariant(stream)           
            msg = ReadAck(sender, receiver,
                          size, block_size, strip_length)
            
        elif msg_type == CommandTypeEnum.ready:
            sender = readVariant(stream)
            msg = Ready(sender)
        elif msg_type == CommandTypeEnum.data:
            sender = readVariant(stream)
            receiver = readVariant(stream)
            strip_id = readVariant(stream)
            block_id = readVariant(stream)
            size = readVariant(stream)
            crc = readVariant(stream)
            data = readString(stream)            
            msg = Data(sender, receiver,
                       strip_id, block_id,
                       size, crc, data)
            
        elif msg_type == CommandTypeEnum.data_ack:
            sender = readVariant(stream)
            strip_id = readVariant(stream)
            block_id = readVariant(stream)
            msg = DataAck(sender, strip_id, block_id)
        else:
            stream.close()
            self.logger.warn("<Whisper>unsupport message type %d in control channel"%(
                msg_type))
            return None
        stream.close()
        return msg
    
    def attachFile(self, filename):
        """
        @return:file id
        """
        with self.file_lock:
            file_id = uuid.uuid4().hex
            self.files[file_id] = filename
            self.logger.info("<Whisper>attach file '%s' to file id '%s'"%(
                filename, file_id))
            return file_id

    def detachFile(self, file_id):
        """
        """
        with self.file_lock:
            if self.files.has_key(file_id):
                filename = self.files[file_id]
                self.logger.info("<Whisper>detach file '%s' from id '%s'"%(
                    filename, file_id))
                del self.files[file_id]        
            return True
        
    def containsFile(self, file_id):
        return self.files.has_key(file_id)
    
    def getFilename(self, file_id):
        with self.file_lock:
            if self.files.has_key(file_id):
                return self.files[file_id]
            else:
                return None

    def generateFile(self):
        with self.file_lock:
            file_id = uuid.uuid4().hex
            filename = os.path.join(self.tmp_path, file_id)
            self.files[file_id] = filename
            self.logger.info("<Whisper>generate file id '%s', path '%s'"%(
                file_id, filename))
            return file_id
        
    def fetchFile(self, file_id, target_file):
        """
        fetch file to target dest&detach
        """
        with self.file_lock:
            if not self.files.has_key(file_id):
                self.logger.error("<Whisper>fetch file fail, invalid id '%s'"%(
                    file_id))
                return False

            if os.path.exists(target_file):
                os.remove(target_file)
                self.logger.info("<Whisper>fetch file, existing file '%s' removed"%(
                    target_file))
                
            try:
                source_file = self.files[file_id]
                os.rename(source_file, target_file)
                self.logger.info("<Whisper>fetch file success, source file '%s'(id '%s') moved to '%s'"%(
                    source_file, file_id, target_file))
                del self.files[file_id]
                return True
                
            except Exception, e:
                self.logger.error("<Whisper>fetch file exception, file id '%s',msg:%s"%
                           (file_id, e.args))
                return False        

    def allocateWriteTask(self, file_id, remote_ip, remote_port):
        """
        @return:task id
        """
        with self.file_lock:        
            if not self.files.has_key(file_id):
                self.logger.error("<Whisper>allocate write task fail, invalid file id '%s'"%(
                    file_id))
                return -1
            filename = self.files[file_id]
            if not os.path.exists(filename):
                self.logger.error("<Whisper>allocate write task fail, file '%s' not exists"%(
                    filename))
                return -1
            file_size = os.path.getsize(filename)
            
        with self.task_lock:        
            for task_id in range(self.min_task_id, self.max_task_id):
                if not self.tasks.has_key(task_id):
                    ##new id                    
                    task = WhisperWriteTask(task_id, file_id, filename, self,
                                            file_size, self.block_size, self.strip_length,
                                            remote_ip, remote_port)
                    self.tasks[task_id] = task
                    self.logger.info("<Whisper>allocate write task sucess, task id %d, file '%s'(id '%s')"%(
                                     task_id, filename, file_id))
                    return task_id
            else:
                self.logger.error("<Whisper>allocate write task fail, no task id available")
                return -1

    def startWriteTask(self, task_id):
        with self.task_lock:
            if not self.tasks.has_key(task_id):
                self.logger.error("<Whisper>start write task fail, invalid id '%d'"%(
                    task_id))
                return False
            task = self.tasks[task_id]
            ##connect remote endpoint
            return task.connect(self.channel_count)

    def onTaskStart(self, task_id, task_type):
        event = WhisperEvent()
        event.event_type = WhisperEvent.start
        event.task_id = task_id
        event.task_type = task_type
        with self.notify_lock:
            self.notify_queue.append(event)
    
    def onTaskProgress(self, task_id, task_type,
                       current, total, percent, speed):
        event = WhisperEvent()
        event.event_type = WhisperEvent.progress
        event.task_id = task_id
        event.task_type = task_type
        event.current = current
        event.total = total
        event.percent = percent
        event.speed = speed
        with self.notify_lock:
            self.notify_queue.append(event)
            
    def onTaskSuccess(self, task_id, task_type, file_id):
        event = WhisperEvent()
        event.event_type = WhisperEvent.success
        event.task_id = task_id
        event.task_type = task_type
        event.file_id = file_id
        with self.notify_lock:
            self.notify_queue.append(event)

    def onTaskFail(self, task_id, task_type):
        event = WhisperEvent()
        event.event_type = WhisperEvent.fail
        event.task_id = task_id
        event.task_type = task_type
        with self.notify_lock:
            self.notify_queue.append(event)

    def allocateReadTask(self, remote_file_id, remote_ip, remote_port):
        """
        @return:task id
        """
        file_id = self.generateFile()
        filename = self.getFilename(file_id)
            
        with self.task_lock:        
            for task_id in range(self.min_task_id, self.max_task_id):
                if not self.tasks.has_key(task_id):
                    ##new id                    
                    task = WhisperReadTask(task_id, file_id, filename, self,
                                           remote_ip, remote_port)
                    task.setRemoteFile(remote_file_id)                 
                    self.tasks[task_id] = task
                    self.logger.info("<Whisper>allocate read task sucess, task id %d, file '%s'(id '%s')"%(
                                     task_id, filename, file_id))
                    return task_id
            else:
                self.detachFile(file_id)
                self.logger.error("<Whisper>allocate read task fail, no task id available")
                return -1

    def startReadTask(self, task_id):
        with self.task_lock:
            if not self.tasks.has_key(task_id):
                self.logger.error("<Whisper>start read task fail, invalid id '%d'"%(
                    task_id))
                return False
            task = self.tasks[task_id]
            ##connect remote endpoint
            return task.connect(self.data_handler.getLocalPorts())

    def sendData(self, request_list):        
        """
        @request_list:list of (data msg, remote_ip, remote_port)
        """
        return self.putToDataSend(request_list)
    
    def sendCommand(self, command, remote_ip, remote_port):
        return self.putToSystemSend(command, remote_ip, remote_port)   

    def handleCommand(self, command, sender_ip, sender_port):
        if command.type == CommandTypeEnum.write:
            return self.handleWriteRequest(command, sender_ip, sender_port)
        elif command.type == CommandTypeEnum.write_ack:
            return self.handleWriteAck(command, sender_ip, sender_port)
        elif command.type == CommandTypeEnum.data:
            return self.handleData(command, sender_ip, sender_port)
        elif command.type == CommandTypeEnum.data_ack:
            return self.handleDataAck(command, sender_ip, sender_port)
        elif command.type == CommandTypeEnum.finish:
            return self.handleFinish(command, sender_ip, sender_port)
        elif command.type == CommandTypeEnum.finish_ack:
            return self.handleFinishAck(command, sender_ip, sender_port)
        elif command.type == CommandTypeEnum.read:
            return self.handleReadRequest(command, sender_ip, sender_port)
        elif command.type == CommandTypeEnum.read_ack:
            return self.handleReadAck(command, sender_ip, sender_port)
        elif command.type == CommandTypeEnum.ready:
            return self.handleReady(command, sender_ip, sender_port)
        elif command.type == CommandTypeEnum.check:
            return self.handleScheduleCheck()

    def handleWriteRequest(self, command, sender_ip, sender_port):
        ##request write
        self.logger.info("<Whisper>receive write request from '%s:%d', sender %d, size %d, block %d, strip %d, channel %d"%(
            sender_ip, sender_port, command.sender, command.size,
            command.block_size, command.strip_length, command.channel))
        with self.task_lock:
            for task_id in range(self.min_task_id, self.max_task_id):
                if not self.tasks.has_key(task_id):
                    ##task id available                    
                    file_id = self.generateFile()
                    with self.file_lock:
                        filename = self.files[file_id]
                    ##allocate write task
                    task = WhisperWriteTask(task_id, file_id, filename, self,
                                            command.size, command.block_size, command.strip_length,
                                            sender_ip, sender_port)
                    task.setRemoteTask(command.sender)
                    self.logger.info("<Whisper>task[%d]:allocated, file id '%s'"%(
                        task_id, file_id))
                    
                    if not task.createReceiver():
                        self.detachFile(file_id)
                        self.logger.error("<Whisper>handle write request fail, create receiver fail")
                        return False                    
                    self.logger.info("<Whisper>task[%d]:receiver ready, file '%s', size %d, block %d, strip %d"%(
                        task_id, filename, command.size, command.block_size, command.strip_length))
                    
                    self.tasks[task_id] = task                    
                    
                    send_channel = command.channel
                    data_ports = self.data_handler.getLocalPorts()
                    if send_channel < self.channel_count:
                        port_list = data_ports[:send_channel]
                    else:
                        port_list = data_ports

                    ack = WriteAck(command.sender, task_id, file_id, port_list)
                    return self.sendCommand(ack, sender_ip, sender_port)                    
            else:
                self.logger.error("<Whisper>handle write request fail, no task id available")
                return False

    def handleWriteAck(self, command, sender_ip, sender_port):
        ##write ack
        with self.task_lock:
            task_id = command.sender
            if not self.tasks.has_key(task_id):
                self.logger.error("<Whisper>recv write ack, but invalid task id %d"%(
                    task_id))
                return False
            task = self.tasks[task_id]
            task.setRemoteTask(command.receiver)
            task.setRemoteFile(command.file_id)
            
            if not task.createSender(command.port_list):
                self.logger.error("<Whisper>task[%d]:create sender fail"%(
                    task_id))
                ##detach file id
                self.detachFile(task.file_id)
                del self.tasks[task_id]
                return False            
            self.logger.info("<Whisper>task[%d]:sender ready, remote task %d, file id '%s', %d receive ports"%(
                task_id, command.receiver, command.file_id, len(command.port_list)))
            task.startTransport()
            return True

    def handleReadRequest(self, command, sender_ip, sender_port):
        ##request read
        self.logger.info("<Whisper>receive read request from '%s:%d', receiver %d, request file '%s', %d receive port(s)"%(
            sender_ip, sender_port, command.receiver, command.file_id, len(command.port_list)))
        if not self.containsFile(command.file_id):
            self.logger.error("<Whisper>handle read request fail, invalid file id '%s'"%(command.file_id))
            return False
        filename = self.getFilename(command.file_id)
        file_size = os.path.getsize(filename)
        
        with self.task_lock:
            for task_id in range(self.min_task_id, self.max_task_id):
                if not self.tasks.has_key(task_id):
                    ##task id available  
                    ##allocate read task
                    task = WhisperReadTask(task_id, command.file_id, filename, self,
                                           sender_ip, sender_port)
                    task.setRemoteTask(command.receiver)
                    task.setSize(file_size, self.block_size, self.strip_length)
                    
                    self.logger.info("<Whisper>task[%d]:allocated, file id '%s'"%(
                        task_id, command.file_id))
                    port_count = len(command.port_list)
                    if port_count <= self.channel_count:
                        port_list = command.port_list
                    else:
                        ##truncate
                        port_list = command.port_list[:self.channel_count]
                        
                    if not task.createSender(port_list):
                        self.logger.error("<Whisper>handle read request fail, create sender fail")
                        return False                    
                    self.logger.info("<Whisper>task[%d]:sender ready, file '%s', size %d, block %d, strip %d, %d send channel"%(
                        task_id, filename, file_size, self.block_size, self.strip_length, len(port_list)))
                    
                    self.tasks[task_id] = task                        

                    ack = ReadAck(task_id, command.receiver, file_size, self.block_size, self.strip_length)
                    return self.sendCommand(ack, sender_ip, sender_port)                    
            else:
                self.logger.error("<Whisper>handle read request fail, no task id available")
                return False

    def handleReadAck(self, command, sender_ip, sender_port):
        ##read ack
        with self.task_lock:
            task_id = command.receiver
            if not self.tasks.has_key(task_id):
                self.logger.error("<Whisper>recv read ack, but invalid task id %d"%(
                    task_id))
                return False
            task = self.tasks[task_id]
            task.setRemoteTask(command.sender)
            task.setSize(command.size, command.block_size, command.strip_length)
            
            if not task.createReceiver():
                self.logger.error("<Whisper>task[%d]:create sender fail"%(
                    task_id))
                ##detach file id
                self.detachFile(task.file_id)
                del self.tasks[task_id]
                return False            
            self.logger.info("<Whisper>task[%d]:receiver ready, remote task %d, file size %d"%(
                task_id, command.sender, command.size))
            ready = Ready(command.sender)
            return self.sendCommand(ready, sender_ip, sender_port)
            
            
    def handleReady(self, command, sender_ip, sender_port):
        ##read ready
        with self.task_lock:
            task_id = command.sender
            if not self.tasks.has_key(task_id):
                self.logger.error("<Whisper>recv read ready, but invalid task id %d"%(
                    task_id))
                return False
            task = self.tasks[task_id]
            task.startTransport()
            return True
        
    def handleData(self, command, sender_ip, sender_port):
##        with TestUnit("handle data"):
        with self.task_lock:
            task_id = command.receiver
            if not self.tasks.has_key(task_id):
                self.logger.error("<Whisper>handle data fail, invalid task %d"%(
                    task_id))
                return False
            task = self.tasks[task_id]
            return task.handleData(command, sender_ip, sender_port)       
            
    def handleDataAck(self, command, sender_ip, sender_port):
        with self.task_lock:
            task_id = command.sender
            if not self.tasks.has_key(task_id):
                self.logger.error("<Whisper>handle data ack fail, invalid task %d"%(
                    task_id))
                return False
            task = self.tasks[task_id]
            return task.handleDataAck(command, sender_ip, sender_port)
                
    def handleFinish(self, command, sender_ip, sender_port):
        with self.task_lock:
            task_id = command.receiver
            if not self.tasks.has_key(task_id):
                self.logger.error("<Whisper>handle finish fail, invalid task %d"%(
                    task_id))
                return False
            task = self.tasks[task_id]
            task.handleFinish(command, sender_ip, sender_port)
            if task.finished:
                self.logger.info("<Whisper>task[%d]:deallocated"%(
                    task_id))
                del self.tasks[task_id]
            return True

    def handleFinishAck(self, command, sender_ip, sender_port):
        with self.task_lock:
            task_id = command.sender
            if not self.tasks.has_key(task_id):
                self.logger.error("<Whisper>handle data ack fail, invalid task %d"%(
                    task_id))
                return False
            task = self.tasks[task_id]
            task.handleFinishAck(command, sender_ip, sender_port)
            self.logger.info("<Whisper>task[%d]:deallocated"%(
                    task_id))
            del self.tasks[task_id]
            return True
            
    def handleScheduleCheck(self):
##        with TestUnit("check"):
        with self.task_lock:            
            fail_list = []
            for task_id in self.tasks.keys():
                task = self.tasks[task_id]
                if not task.check():
                    ##check fail
                    fail_list.append(task_id)
            if 0 != len(fail_list):
                for task_id in fail_list:
                    self.logger.error("<Whisper>task[%d]:deallocate due to check fail"%(
                        task_id))
                    del self.tasks[task_id]
                                            
    
