#!/usr/bin/python
import threading
import io
import logging
import socket
import select
from service.serialize import *
from service.service_status import StatusEnum
from whisper_command import *

class WhisperContrlChannel(object):
    def __init__(self, socket, ip, port, command_handler):
        self.logger = logging.getLogger("whisper.data")
        self.socket = socket
        self.ip = ip
        self.port = port
        self.command_handler = command_handler
        
        self.status = StatusEnum.stopped
        self.status_mutex = threading.RLock()
        ##block after create
        self.request_available = threading.Event()
        self.request_list = []
        self.request_mutex = threading.RLock()
        self.send_thread = threading.Thread(target=self.sendProcess)
        self.receive_thread = threading.Thread(target=self.receiveProcess)
        self.max_request = 10000
        self.cache = 5
        self.interval = 1
        
    def sendCommand(self, command,
                remote_ip, remote_port):
        
        with self.request_mutex:
            if len(self.request_list) >= self.max_request:
                return False
            self.request_list.append((command, remote_ip, remote_port))
            if len(self.request_list) < self.cache:
                self.request_available.set()
        return True

    def start(self):
        with self.status_mutex:
            if StatusEnum.stopped != self.status:
                return False
            self.status = StatusEnum.running            
            self.send_thread.start()
            self.receive_thread.start()
            return True

    def stop(self):
        with self.status_mutex:
            if StatusEnum.stopped == self.status:
                return
            if StatusEnum.running == self.status:
                self.status = StatusEnum.stopping
                with self.request_mutex:
                    ##clear request list
                    self.request_list = []
                ##notify wait thread
                self.request_available.set()
        
        self.send_thread.join()
        self.receive_thread.join()
        with self.status_mutex:
            self.status = StatusEnum.stopped
            
    def isRunning(self):
        return (StatusEnum.running == self.status)

    def onCommandReceived(self, command, remote_ip, remote_port):
        self.command_handler(command, remote_ip, remote_port)

    def sendProcess(self):
        interval = 1
        while StatusEnum.running == self.status:
            ##wait for signal
            self.request_available.wait(self.interval)
            if StatusEnum.running != self.status:
                ##double protect
                break
            if self.request_available.isSet():
                ##clear when set
                self.request_available.clear() 
            with self.request_mutex:
                if(0 == len(self.request_list)):
                    ##empty
                    continue
                ##FIFO/pop front
                request_list = self.request_list
                self.request_list = []

            for request in request_list:
                msg = request[0]
                remote_ip = request[1]
                remote_port = request[2]
                data = self.serializeToPacket(msg)
                    
                address = (remote_ip, remote_port)
                emptys = []
                outcoming = [self.socket]
                try:
                    readable, writable, exceptional = select.select(emptys, outcoming, outcoming, interval)
                    if not self.isRunning():
                        ##service stopped
                        return
                    if writable:
                        data_length = len(data)
                        result = self.socket.sendto(data, 0, address)
                        if data_length != result:
                            self.logger.warn("<Whisper>channel %d:imcomplete data send to address %s, %d/%d bytes"%(
                                self.index, address, result, data_length))
    ##                    else:
    ##                        self.logger.info("<Whisper>channel %d:send %d bytes to %s(with socket %d '%s:%d')"%(
    ##                            index, len(data), address, send_socket.fileno(), info.ip, info.port))
                            
                            
                except socket.error,e:
                    self.logger.warn("<Whisper>channel %d:send datagram from '%s:%d' to '%s' exception:%s"%(
                        index, info.ip, info.port, address, e.strerror))
                    return                

    def receiveProcess(self):
        bufsize = 2*1024*1024
        ##50 ms
        interval = 0.05
        cache = []
        cache_counter = 0
        max_cache = 200
        channel = 0
            
        while self.isRunning():
            emptys = []
            incoming = [self.socket]
            timeout = False
            try:
                readable, writable, error = select.select(incoming, emptys, incoming, interval)
                if not self.isRunning():
                    ##service stopped
                    break
                if readable:
                    data, address = self.socket.recvfrom(bufsize)
                    cache_counter += 1
                    cache.append((address, data))
                    
                elif error:
                    self.logger.warn("<Whisper>channel %d:unknown error when receive"%(channel))
                    break
                else:
                    timeout = True
            except socket.error,e:
                self.logger.warn("<Whisper>channel %d:receive packet socket exception:%s"%
                          (channel, e.strerror))
                break
            except Exception,e:
                self.logger.warn("<Whisper>channel %d:receive packet exception:%s"%(
                    channel, e.args))
                break
            
             
            ##process cache
            if (cache_counter > max_cache) or (timeout and 0 != len(cache)):                
                ##flush all cache
                for packet in cache:
                    sender_ip = packet[0][0]
                    sender_port = packet[0][1]
                    raw_data = packet[1]
                    msg = self.unserialFromPacket(raw_data)
                    self.command_handler(msg, sender_ip, sender_port)
                    
                cache = []
                cache_counter = 0

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
        else:
            stream.close()
            self.logger.warn("<Whisper>unsupport message type %d in control channel"%(
                msg.type))
            return None
        
        data = stream.getvalue()
        stream.close()
        return data 


    def unserialFromPacket(self, packet):
        stream = io.BytesIO(packet)
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
        else:
            stream.close()
            self.logger.warn("<Whisper>unsupport message type %d in control channel"%(
                msg_type))
            return None
        stream.close()
        return msg
