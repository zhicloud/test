#!/usr/bin/python
import threading
import io
import logging
import binascii
import socket
import select
from service.serialize import *
from service.service_status import StatusEnum
from whisper_command import *

class WhisperDataChannel(object):
    def __init__(self, index, socket, ip, port, data_handler):
        self.logger = logging.getLogger("whisper.data")
        self.index = index
        self.socket = socket
        self.ip = ip
        self.port = port
        self.data_handler = data_handler
        
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
        
    def sendMessage(self, packet_list, remote_ip, remote_port):
        with self.request_mutex:
            if len(self.request_list) >= self.max_request:
                return False
            for packet in packet_list:
                self.request_list.append((packet, remote_ip, remote_port))
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

    def sendProcess(self):
##        self.logger.info("<Whisper>data channel[%d] send thread started"%(self.index))
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
                ##serialize
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
##                        else:
##                            self.logger.info("<Whisper>channel %d:send %d bytes to %s"%(
##                                self.index, data_length, address))
                            
                            
                except socket.error,e:
                    self.logger.warn("<Whisper>channel %d:send datagram from '%s:%d' to '%s' exception:%s"%(
                        index, info.ip, info.port, address, e.strerror))
                    return                
        
    def receiveProcess(self):
##        self.logger.info("<Whisper>data channel[%d] receive thread started"%(self.index))
        bufsize = 2*1024*1024
        ##50 ms
        interval = 0.05
        cache = []
        cache_counter = 0
        max_cache = 200            
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
##                    self.logger.info("<Whisper>channel %d:recv %d byte(s) from %s"%(
##                        self.index, len(data), address))
                    
                elif error:
                    self.logger.warn("<Whisper>channel %d:unknown error when receive"%(
                        self.index))
                    break
                else:
                    timeout = True
            except socket.error,e:
                self.logger.warn("<Whisper>channel %d:receive packet socket exception:%s"%
                          (self.index, e.strerror))
                break
            except Exception,e:
                self.logger.warn("<Whisper>channel %d:receive packet exception:%s"%(
                    self.index, e.args))
                break
            
             
            ##process cache
            if (cache_counter > max_cache) or (timeout and 0 != len(cache)):                
                ##flush all cache
                for packet in cache:
                    sender_ip = packet[0][0]
                    sender_port = packet[0][1]
                    raw_data = packet[1]
                    msg = self.unserialFromPacket(raw_data)
                    if msg.type == CommandTypeEnum.data:
                        ##length&crc check
                        if msg.size != len(msg.data):
                            self.logger.error("<Whisper>data received, but data truncated %d / %d byte(s)"%(
                                len(msg.data), msg.size))
                            continue
                        data_crc = binascii.crc32(msg.data)&0xFFFFFFFF
                        if msg.crc != data_crc:
                            self.logger.error("<Whisper>data received, crc check fail, original[%08X] received[%08X]"%(
                                msg.crc, data_crc))
                            continue
                        self.data_handler(msg, sender_ip, sender_port)
                        
                        ack_msg = DataAck(msg.sender, msg.strip_id, msg.block_id)
                        ##send ack
                        self.sendMessage([ack_msg], sender_ip, sender_port)
                        
                    elif msg.type == CommandTypeEnum.data_ack:
                        ##ack
                        self.data_handler(msg, sender_ip, sender_port)
                    
                cache = []
                cache_counter = 0        

##        self.logger.info("<Whisper>data channel[%d] receive thread stopped"%(self.index))

    def isRunning(self):
        return (StatusEnum.running == self.status)    

    def serializeToPacket(self, msg):
        stream = io.BytesIO()
        writeVariant(stream, msg.type)
        if msg.type == CommandTypeEnum.data:
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
            self.logger.warn("<Whisper>unsupport message type %d in data channel %d"%(
                msg.type, self.index))
            return None
        
        data = stream.getvalue()
        stream.close()
        return data 


    def unserialFromPacket(self, packet):
        stream = io.BytesIO(packet)
        msg_type = readVariant(stream)
        if msg_type == CommandTypeEnum.data:
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
            self.logger.warn("<Whisper>unsupport message type %d in data channel %d"%(
                msg_type, self.index))
            return None
        stream.close()
        return msg
