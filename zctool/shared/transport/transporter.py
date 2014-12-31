#!/usr/bin/python
import threading
import zlib
import random
import hashlib
import sys
import socket
import select
import logging
import traceback

from service.service_status import StatusEnum
from datagram import *
from endpoint_manager import *
from app_message import *
from transport_command import *
from send_task_manager import *
from dispatch_pool import *
from cached_pool import *

class ChannelInfo(object):
    def __init__(self, index):
        self.index = index
        self.ip = ""
        self.port = 0
        self.socket = None
        
class DispatchEvent(object):
    type_message = 0
    type_connected = 1
    type_disconnected = 2
    def __init__(self):
        self.name = ""
        self.type = self.type_message
        self.session_id = 0
        self.message = None

class Transporter(object):
    """
    usage:

    function:
    
    isRunning():is transpoter running
    bind(address, start_port, port_range):bind to local socket
    start():
    stop():
    connect(remote_ip, remote_port):
    disconnect(session_id):
    sendMessage(session_id, message_list):
    

    """
    timeout_check_interval = 1
    max_timeout = 5
    max_retry = 1
    max_task = 1000
    def __init__(self, name, logger_name,
                 handler = None, 
                 channel = 1,
                 process_channel = 1,
                 notify_channel = 1,
                 max_datagram_size = 548):
        self.handler = handler
        self.name = name
        self.bound = False
        self.ip = ""
        self.port = 0
        ##server_key
        int_value = random.random()*10000000
        sha = hashlib.sha1()
        sha.update(str(int_value))
        self.server_key = sha.hexdigest()

        
        self.channel_lock = threading.RLock()
        self.channel_index = 0
        self.channels = []
        self.channel = channel
        self.logger = logging.getLogger(logger_name)
        self.endpoint_manager = EndpointManager()
        
        self.max_datagram_size = max_datagram_size
        self.max_message_size = max_datagram_size - 20
        self.status = StatusEnum.stopped
        self.status_mutex = threading.RLock()

        self.serial_channel = process_channel
        self.serial_interval = 5
        self.serial_cache = 50

        self.package_channel = process_channel
        self.package_interval = 5
        self.package_cache = 50
        
        self.send_interval = 5
        self.send_cache = 5

        self.unpackage_channel = process_channel
        self.unpackage_interval = 5
        self.unpackage_cache = 20

        self.process_channel = process_channel
        self.process_interval = 5
        self.process_cache = 20

        self.notify_channel = notify_channel
        self.notify_interval = 20
        self.notify_cache = 50

        debug = True

        self.serialize_pool = DispatchPool(self.serial_channel,
                                            self.serialSendRequest,
                                            self.serial_interval,
                                            self.serial_cache)
##                                            debug = debug,
##                                            logger_name = "serial channel")

        self.package_pool = DispatchPool(self.package_channel,
                                         self.packageSendRequest,
                                         self.package_interval,
                                         self.package_cache)
##                                         debug = debug,
##                                         logger_name = "package channel")
        
        self.send_pool = CachedPool(self.channel,
                                    self.sendToSocket,
                                    self.send_interval,
                                    self.send_cache)
##                                    debug = debug,
##                                    logger_name = "send channel")

        self.receive_pool = []
        self.channel_managers = []
        for i in range(self.channel):
            self.receive_pool.append(threading.Thread(target=self.receiveProcess))
            self.channel_managers.append(
                SendTaskManager(self.max_task, self.max_timeout, self.max_retry))
        
        self.unpackage_pool = DispatchPool(self.unpackage_channel,
                                            self.unpackageDatagram,
                                            self.unpackage_interval,
                                            self.unpackage_cache)
##                                            debug = debug,
##                                            logger_name = "unpackage channel")

        self.process_pool = DispatchPool(self.process_channel,
                                         self.processDatagram,
                                         self.process_interval,
                                         self.process_cache)
##                                         debug = debug,
##                                         logger_name = "process channel")

        self.notify_pool = DispatchPool(self.notify_channel,
                                        self.notifyEvent,
                                        self.notify_interval,
                                        self.notify_cache)
##                                        debug = debug,
##                                        logger_name = "notify channel")
        ##timeout check
        self.timeout_check_event = threading.Event()
        self.timeout_check_thread = threading.Thread(target=self.timeoutCheckProcess)
        
    def isRunning(self):
        return (StatusEnum.running == self.status)

    def bind(self, address = "0.0.0.0", start_port = 5600, port_range = 200):
        buf_size = 2*1024*1024
        ##udp protocol
        count = 0
        for port in range(start_port, start_port + port_range):
            try:
                new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buf_size)
                new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buf_size)
                new_socket.setblocking(0)
                new_socket.bind((address, port))
            except socket.error as e:
##                self.logger.info("<Transporter>bind to '%s:%d' exception:%s"%(address, port, e.strerror))
                ##try next port
                continue

            ##bind success
##            r_buf = new_socket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
##            s_buf = new_socket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
##            self.logger.info("<Transporter>bind to '%s:%d' success, socket %d, recv %d, send %d"%(
##                address, port, new_socket.fileno(), r_buf, s_buf))
            if 0 == count:
                self.bound = True
                self.ip = address
                self.port = port
            info = ChannelInfo(count)
            info.socket = new_socket
            info.ip = address
            info.port = port
            self.channels.append(info)
            count += 1
            if count >= self.channel:
                return True
        else:
            ##no port availabe
            self.logger.error("<Transporter>not enough available port(%d required) in %s:%d~%d"%(
                self.channel, address, start_port, start_port + port_range - 1))
            return False
        
    def getListenPort(self):
        if self.bound:
            return self.port
        else:
            return -1
        
    def start(self):
        with self.status_mutex:
            if StatusEnum.stopped != self.status:
                self.logger.error("<Transporter>start transporter fail, not in stop status")
                return False
            self.status = StatusEnum.running
            
            self.serialize_pool.start()
            self.package_pool.start()
            self.send_pool.start()

            for i in range(self.channel):
                self.receive_pool[i].start()

            self.unpackage_pool.start()   
            self.process_pool.start()
            self.notify_pool.start()

            self.timeout_check_event.clear()
            self.timeout_check_thread.start()
            self.logger.info("<Transporter>start transporter success")
            return True

    def stop(self):
        with self.status_mutex:
            if StatusEnum.stopped == self.status:
                return
            if StatusEnum.running == self.status:
                self.status = StatusEnum.stopping
                self.logger.info("<Transporter>stopping transporter...")
                self.disconnectAll()
                
                self.timeout_check_event.set()
                
                self.serialize_pool.stop()
                self.package_pool.stop()
                self.send_pool.stop()
                
                ##notify wait thread
##                self.logger.info("<Transporter>closing socket...")
                   
                try:
                    for info in self.channels:
                        info.socket.close()
##                        self.logger.info("<Transporter>service socket %d closed"%(info.index))
                        
                except socket.error as e:
                    self.logger.warn("<Transporter>close service socket exception:%d, %s"%(e.errno, e.strerror))                                              

        self.timeout_check_thread.join()
        
        for i in range(self.channel):
            self.receive_pool[i].join()
        self.unpackage_pool.stop()
        self.process_pool.stop()
        self.notify_pool.stop()
        
        with self.status_mutex:
            self.status = StatusEnum.stopped

        self.logger.info("<Transporter>transporter stopped")
##        ##debug info
##        self.info("<DataLink>params:")
##        self.info("<DataLink>datagram size %d bytes, queue size %d"%(
##            self.max_datagram_size, self.max_queue_size))
##        self.info("<DataLink>dispatch channel %d, interval %d ms, cache %d"%(
##            self.dispatch_channel, self.dispatch_interval, self.dispatch_cache))
##        self.info("<DataLink>serialize channel %d, interval %d ms, cache %d"%(
##            self.serialize_channel, self.serialize_interval, self.serialize_cache))
##        self.info("<DataLink>package channel %d, interval %d ms, cache %d"%(
##            self.package_channel, self.package_interval, self.package_cache))
##        self.info("<DataLink>send channel %d, interval %d ms, cache %d"%(
##            self.send_channel, self.send_interval, self.send_cache))
##
##        self.info("<DataLink>unpackage channel %d, interval %d ms, cache %d"%(
##            self.unpackage_channel, self.unpackage_interval, self.unpackage_cache))
##        self.info("<DataLink>unserialize channel %d, interval %d ms, cache %d"%(
##            self.unserialize_channel, self.unserialize_interval, self.unserialize_cache))


    def connect(self, remote_ip, remote_port):
        session_id = self.endpoint_manager.allocate()
        if -1 == session_id:
            self.logger.error("<Transporter>connect fail, can't allocate endpoint")
            return False        
        ##new session
        channel_id = session_id%(self.channel)
        endpoint = self.endpoint_manager.getSession(session_id)
        if not endpoint.initial(channel_id):
            self.logger.error("<Transporter>connect fail, can't initial endpoint")
            return False
        

        info = self.channels[channel_id]
        
        request = ConnectRequest()
        request.sender = session_id
        request.ip = info.ip
        request.port = info.port
        request.name = self.name
        
        ##client_key
        int_value = random.random()*10000000
        sha = hashlib.sha1()
        sha.update(str(int_value))
        request.client_key = sha.hexdigest()

        datagram = request.toString()
        
##        self.logger.info("[%08X]try connecting remote address '%s:%d'..."%(
##            session_id, remote_ip, remote_port))
        self.put(channel_id, (remote_ip, remote_port), [datagram])
        return True

    def disconnect(self, session_id):
        endpoint = self.endpoint_manager.getSession(session_id)
        if not endpoint:
            self.logger.error("<Transporter>disconnect fail, invalid session %d"%(
                session_id))
            return
        request = DisconnectRequest()
        request.name = self.name
        request.session = endpoint.remote_session
        
##        self.logger.info("[%08X]send disconnect request to node '%s'"%(session_id, endpoint.remote_name))
        self.send(session_id, [request.toString()])

    def disconnectAll(self):
        session_list = self.endpoint_manager.getConnectedEndpoint()
        if 0 == len(session_list):
            return
        
        for session_id in session_list:
            self.disconnect(session_id)

##        self.logger.info("<Transporter>disconnect %d connectd endpoint"%(len(session_list)))
        
        
    def sendMessage(self, session_id, message_list):
        if not self.serialize_pool.put([(session_id, message_list)]):
            self.logger.warn("<Transporter>send message to serial pool fail!")
            return False
        return True       

    def serialSendRequest(self, index, request_list):
        try:
    ##        self.logger.info("<Transporter> serialize %d send request"%(len(request_list)))
            for request in request_list:
                session_id = request[0]
                message_list = request[1]
                endpoint = self.endpoint_manager.getSession(session_id)
                if not endpoint:
                    self.logger.error("<Transporter>send message fail, invalid session %d"%session_id)
                    continue
                if not endpoint.isConnected():
                    self.logger.error("[%08X]send message fail, session disconnected"%session_id)
                    continue
                begin_serial, end_serial = endpoint.allocateSerial(len(message_list))
                if 0 == begin_serial:
                    self.logger.error("[%08X]send message fail, allocate serial fail"%
                                      session_id)
                    continue
                
                message_serial = begin_serial
                datagram_list = []
                for message in message_list:
                    content = message.toString()
                    if len(content) > self.max_message_size:
                        ##split
                        length = len(content)
                        total = (length - length%self.max_message_size)/self.max_message_size + 1
                        begin = 0
                        end = begin + self.max_message_size
                        index = 1
                        while begin != len(content):
                            message_data = MessageData()
                            message_data.serial = message_serial
                            message_data.index = index
                            message_data.total = total
                            message_data.data = content[begin:end]
                            message_data.session = endpoint.remote_session
                            
                            datagram_list.append(message_data.toString())
            ##                self.debug("[%08X]split message data, serial %d, %d/%d, begin %d - end %d, length %d"%(
            ##                    session_id, serial, index, total, begin, end, (end - begin)))                   
                            
                            ##next split
                            index += 1
                            begin = end
                            end = begin + self.max_message_size
                            if end > len(content):
                                end = len(content)
                                
        ##                self.logger.debug("[%08X]split message data, serial %d, total length %d, split into %d datagrams"%(
        ##                    session_id, message_serial, length, total))                   
                            
                    else:
                        ##single datagram
        ##                begin = datetime.datetime.now()
                        message_data = MessageData()
                        message_data.serial = message_serial
                        message_data.index = 1
                        message_data.total = 1
                        message_data.data = content
                        message_data.session = endpoint.remote_session

        ##                e2.append(elapsedMilliseconds( datetime.datetime.now() - begin))
                        datagram_list.append(message_data.toString())
                                
                    if message_serial > EndpointSession.max_serial:
                        message_serial = 1
                    else:
                        message_serial += 1


    ##            self.logger.info("<Transporter> serialize %d messages into %d datagrams"%(
    ##                len(message_list), len(datagram_list)))
        ##        self.logger.info("[%08X]e1:total %.3f ms, avg %.3f ms, %.3f ms ~ %.3f ms"%(
        ##            session_id, sum(e1), sum(e1)/len(e1), min(e1), max(e1)))
        ##        self.logger.info("[%08X]e2:total %.3f ms, avg %.3f ms, %.3f ms ~ %.3f ms"%(
        ##            session_id, sum(e2), sum(e2)/len(e2), min(e2), max(e2)))
                if not self.put(endpoint.channel, (endpoint.nat_ip, endpoint.nat_port), datagram_list):
                    self.logger.warn("[%08X]put %d datagrams into channel %d fail"%(
                        session_id, len(datagram_list)))
                    continue
                
        except Exception as e:
            self.logger.warn("<Transporter>serialize request exception:%s"%
                         (e.args))
            
    def send(self, session_id, datagram_list):
        endpoint = self.endpoint_manager.getSession(session_id)
        if not endpoint:
            self.logger.error("<Transporter>send fail, invalid endpoint id %d"%(session_id))
            return False
        return self.put(endpoint.channel, (endpoint.nat_ip, endpoint.nat_port), datagram_list)
    
    def put(self, channel_id, remote_address, datagram_list):
        request_list = []
        for datagram in datagram_list:
            request_list.append((channel_id, remote_address, datagram))
            
        if not self.package_pool.put(request_list):
            self.logger.warn("<Transporter>add %d datagrams to package pool fail!"%(
                len(request_list)))
            return False
##        else:
##            self.logger.info("<Transporter>add %d datagrams to package pool"%(
##                len(request_list)))            
        return True
    
    def packageSendRequest(self, index, request_list):
        ##request_list:list of (channel_id, remote_address, datagram)
        rawdata = {}
        ##serialize && resort
        for request in request_list:
            channel_id = request[0]
            address = request[1]
            datagram = request[2]
            if not rawdata.has_key(channel_id):
                rawdata[channel_id] = {address:[datagram]}
            elif not rawdata[channel_id].has_key(address):
                rawdata[channel_id][address] = [datagram]
            else:
                rawdata[channel_id][address].append(datagram)

        ##package to packet
        packets = {}
        for channel in rawdata.keys():
            channel_data = rawdata[channel]
            packets[channel] = {}
            task_manager = self.channel_managers[channel]
            fail_list = []
            for address in channel_data.keys():
                data_list = channel_data[address]
                packets[channel][address] = []
                cache = ""
                length = 0
                for data in data_list:
                    ##4 bytes length + raw data
                    data_length = len(data)
                    if (data_length + length) > self.max_datagram_size:
                        ##new packet, flush cache
                        if 0 != length:
                            packets[channel][address].append(cache)
                        cache = data
                        length = data_length
                    else:
                        cache += data
                        length += data_length
                if 0 != len(cache):
                    ##flush last packet
                    packets[channel][address].append(cache)

##        total_packets = 0
        for channel in packets.keys():
            task_manager = self.channel_managers[channel]
            packet_list = []
            fail_list = []
            for address in packets[channel].keys():
                content_list = packets[channel][address]                
                ##allocate send task
                count = len(content_list)                
                id_list = task_manager.allocate(count)
                if 0 == len(id_list):
                    self.logger.warn("<Transporter>package fail, allocate %d send task fail"%(
                        count))
                    continue
                for i in range(len(id_list)):
                    task_id = id_list[i]
                    content = content_list[i]
                    task = task_manager.getTask(task_id)
                    if not task:
                        fail_list.append(task_id)
                        continue
                    if not task.initial(content, address):
                        fail_list.append(task_id)
                        continue
                    packet_list.append((address, task.data))
            ##end for address in packets[channel].keys():
            if 0 != len(fail_list):
                task_manager.deallocate(fail_list)
                self.logger.warn("<Transporter>deallocate %d task when package"%(len(fail_list)))
                
            ##put to send channel
            if not self.send_pool.put(channel, packet_list):
                self.logger.warn("<Transporter>put %d packets to send channel %d fail!"%(
                    len(packet_list), channel))
                continue
            
##            total_packets += len(packet_list)
##        self.logger.info("<Transporter>package %d request into %d packets"%(
##            len(request_list), total_packets))

    def sendToSocket(self, index, request_list):
        ##request_list:list of (address, task.data)
        timeout = 1
        info = self.channels[index]
        send_socket = info.socket
        for item in request_list:
            address = item[0]
            data = item[1]
            emptys = []
            outcoming = [send_socket]
            try:
                readable, writable, exceptional = select.select(emptys, outcoming, outcoming, timeout)
                if not self.isRunning():
                    ##service stopped
                    return
                if writable:
                    data_length = len(data)
                    result = send_socket.sendto(data, 0, address)
                    if data_length != result:
                        self.logger.warn("<Transporter>channel %d:imcomplete data send to address %s, %d/%d bytes"%(
                            index, address, result, data_length))
##                    else:
##                        self.logger.info("<Transporter>channel %d:send %d bytes to %s(with socket %d '%s:%d')"%(
##                            index, len(data), address, send_socket.fileno(), info.ip, info.port))
                        
                        
            except socket.error,e:
                self.logger.warn("<Transporter>channel %d:send datagram from '%s:%d' to '%s' exception:%s"%(
                    index, info.ip, info.port, address, e.strerror))
                return
##        self.logger.info("<Transporter>channel %d:send %d packets"%(
##            index, len(request_list)))
        
    def receiveProcess(self):
        ##64k
##        bufsize = 64*1024
        bufsize = 2*1024*1024
        ##50 ms
        interval = 0.05
        cache = []
        cache_counter = 0
        max_cache = 200
        channel = 0
        ##statistic
        received_packet = {}
        received_length = {}
        with self.channel_lock:
            channel = self.channel_index
            info = self.channels[channel]
            receive_socket = info.socket            
            self.logger.info("<Transporter>receive channel %d ready, address '%s:%d', socket %d"%(
                channel, info.ip, info.port, receive_socket.fileno()))
            self.channel_index += 1
            
        while self.isRunning():
            emptys = []
            incoming = [receive_socket]
            timeout = False
            try:
                readable, writable, error = select.select(incoming, emptys, incoming, interval)
                if not self.isRunning():
                    ##service stopped
                    break
                if readable:
                    data, address = receive_socket.recvfrom(bufsize)
##                    self.logger.info("<Transporter>channel %d:recv %d bytes from %s(with socket %d '%s:%d')"%(
##                        channel, len(data), address, receive_socket.fileno(), info.ip, info.port))
                    cache_counter += 1
                    cache.append((channel, address, data))
                        
                    ##statistic
                    if received_packet.has_key(address):
                        received_packet[address] += 1
                    else:
                        received_packet[address] = 1

                    if received_length.has_key(address):
                        received_length[address] += len(data)
                    else:
                        received_length[address] = len(data)
                    
                elif error:
                    self.logger.warn("<Transporter>channel %d:unknown error when receive"%(channel))
                    break
                else:
                    timeout = True
            except socket.error,e:
                self.logger.warn("<Transporter>channel %d:receive packet socket exception:%s"%
                          (channel, e.strerror))
                break
            except Exception,e:
                self.logger.warn("<Transporter>channel %d:receive packet exception:%s"%(
                    channel, e.args))
                break
            
             
            ##process cache
            if (cache_counter > max_cache) or (timeout and 0 != len(cache)):                
                ##flush all cache
                if not self.unpackage_pool.put(cache):
                    self.logger.warn("<Transporter>channel %d:add %d packets to unpackage pool fail!"%(
                        channel, len(cache)))
                    continue
##                self.logger.info("<Transporter>channel %d:receive %d packets"%(
##                    channel, len(cache)))
                cache = []
                cache_counter = 0
                            
            ##end while self.isRunning():
##        total_packets = sum(received_packet.values())
##        total_length = sum(received_length.values())
##        for address in received_packet.keys():
##            self.logger.info("<Transporter>channel %d:receive %d bytes(%d packets) from %s"%(
##                channel, received_length[address], received_packet[address], address))
##        self.logger.info("<Transporter>channel %d stopped, %d bytes(%d packets) received"%(
##            channel, total_length, total_packets))        

    def unpackageDatagram(self, index, request_list):
        ##request_list:list of (channel, address, data)
        received_datagram = []
        finished = {}
        ack_packets = {}
        for request in request_list:
            channel = request[0]
            address = request[1]
            packet = request[2]
            length = len(packet)
            begin = 0
            while (length - begin) >= 3:
                header, seq = struct.unpack(">BH", packet[begin:(begin+3)])
                if Datagram.header_mask != ((header&0xF0)>>4):
                    break
                version = (header&0x0C)>>2
                data_type = header&0x03
                if 1 == data_type:
                    ##ack
                    if finished.has_key(channel):
                        finished[channel].append(seq)
                    else:
                        finished[channel] = [seq]                        
                    begin += 3
                else:
                    ##data
                    if (length - begin) < 9:
                        ##incomplete
                        break
                    data_length, crc = struct.unpack(">HI", packet[(begin+3):(begin+9)])
                    content_offset = begin+9
                    data_content = packet[content_offset:(content_offset + data_length)]
                    ##crc check
                    computed_crc = zlib.crc32(data_content)& 0xFFFFFFFF
                    if computed_crc != crc:
                        ##data damaged
                        break
                    ##unserialize
                    command_list = unpackageFromRawdata(data_content)
                    for command in command_list:
                        received_datagram.append((address, command))

                    ack = DatagramACK(seq)                    
                    if not ack_packets.has_key(channel):
                        ack_packets[channel] = [(address, ack.toString())]
                    else:
                        ack_packets[channel].append((address, ack.toString()))
                    
                    begin = content_offset + data_length                
            ##end while (length - begin) >= 3:
                    
        ##end for request in request_list:
        ##send ack
        for channel in ack_packets.keys():
            ack_list = ack_packets[channel]
            if not self.send_pool.put(channel, ack_list):
                self.logger.warn("<Transporter>put %d ack to send channel %d fail!"%(
                    len(ack_list), channel))
                continue
        for channel in finished.keys():
            task_manager = self.channel_managers[channel]
            ##deallocate success task
            task_manager.deallocate(finished[channel])

##        self.logger.info("<Transporter>unpackage %d packets into %d datagrams"%(
##            len(request_list), len(received_datagram)))
        if not self.process_pool.put(received_datagram):
            self.logger.warn("<Transporter>put datagram list to process pool fail!"%(
                len(result)))            

    def processDatagram(self, index, request_list):
        ##list of (address, datagram)       
        for request in request_list:
            address = request[0]
            command = request[1]    
            try:
                if command.type == TransportCommand.type_keep_alive:
                    self.handleKeepAlive(command, command.session)
                    
                elif command.type == TransportCommand.type_connect_request:
                    self.handleConnectRequest(command, address, command.session)
                    
                elif command.type == TransportCommand.type_connect_response:
                    self.handleConnectResponse(command, address, command.session)
                    
                elif command.type == TransportCommand.type_connect_acknowledge:
                    self.handleConnectACK(command, command.session)
                    
                elif command.type == TransportCommand.type_disconnect_request:
                    self.handleDisconnectRequest(command, command.session)
                    
                elif command.type == TransportCommand.type_disconnect_response:
                    self.handleDisconnectResponse(command, command.session)
                    
                elif command.type == TransportCommand.type_message_data:
                    self.handleMessageData(command, command.session)

            except Exception,ex:
                self.logger.error("<Transporter>handle received datagram exception:%s"%(ex))
                continue              

    def handleKeepAlive(self, msg, session_id):
        endpoint = self.endpoint_manager.getSession(session_id)
        if not endpoint:
##            self.logger.error("<Transporter>accept keep alive fail, invalid session %d"%(
##                session_id))
            return
        if endpoint.remote_name != msg.name:
##            self.logger.warn("[%08X]ignore keep alive, remote name '%s' dismatched"%(session_id, msg.name))
            return        
        if endpoint.isDisconnected():
            ##reconnect
            endpoint.setConnected()
            self.logger.warn("[%08X]session reconnected, remote name'%s'"%(session_id, msg.name))
        else:
            endpoint.updateTimestamp()
##            self.logger.info("[%08X]endpoint keep alive"%(session_id))
    
    def handleConnectRequest(self, request, address, session_id):
        if 0 != len(request.digest):
            endpoint = self.endpoint_manager.getSession(session_id)
            if not endpoint:
                self.logger.error("<Transporter>accept connect request fail, invalid session %d"%(
                    session_id))
                return       
            
##            self.logger.info("[%08X]connect request auth, key '%s', digest '%s'"%(
##                session_id, request.client_key, request.digest))
            ##verify dynamic key
            challenge_key = self.computeChallengeKey(request.client_key)
            verify_key = self.computeVerifyDigest(request.client_key, challenge_key)
            
            ##send response            
            response = ConnectResponse()
            if verify_key == request.digest:
                endpoint.setRemoteName(request.name)
##                self.logger.info("[%08X]connect auth success, remote name '%s'"%(session_id, request.name))
                ##wait remote ack
                response.success = True
                response.name = self.name
                response.sender = session_id
                response.session = endpoint.remote_session
                self.send(session_id, [response.toString()])
                return
            else:
                response.success = False
                response.sender = session_id
                response.session = endpoint.remote_session

                self.logger.error("[%08X]connect reject, digest auth fail"%session_id)
                self.send(session_id, [response.toString()])
                self.endpoint_manager.deallocate(session_id)
                return
        else:            
            ##no digest
            remote_ip = request.ip
            remote_port = request.port
            session_id = self.endpoint_manager.allocate()
            if -1 == session_id:
                self.logger.error("<Transporter>accept connect request fail, can't allocate session")
                return
            endpoint = self.endpoint_manager.getSession(session_id)
            channel_id = session_id%self.channel
            if not endpoint.initial(channel_id):
                self.logger.error("<Transporter>accept connect request fail, can't initial session")
                return
            endpoint.setRemoteAddress(request.sender, remote_ip, remote_port, address[0], address[1])
            
##            self.logger.info("[%08X]received connect request from '%s:%d' (nat address '%s:%d'), remote session [%08X]"%(
##                session_id, remote_ip, remote_port, address[0], address[1], request.sender))
            
            response = ConnectResponse()
            response.success = False
            response.need_digest = True
            response.auth_method = 0##plain
            ##compute dynamic server key
            response.server_key = self.computeChallengeKey(request.client_key)
            response.client_key = request.client_key
            response.sender = session_id
            response.session = endpoint.remote_session
            ##allocated address
            channel_info = self.channels[channel_id]
            response.ip = channel_info.ip
            response.port = channel_info.port
            
##            self.logger.info("[%08X]need auth, allocate local channel %d(address '%s:%d')"%(
##                session_id, channel_id, channel_info.ip, channel_info.port))
            
            self.put(channel_id, (endpoint.nat_ip, endpoint.nat_port), [response.toString()])    
                
    def handleConnectResponse(self, response, address, session_id):
        if not self.endpoint_manager.isAllocated(session_id):
            self.logger.error("<Transporter>accept connect response fail, invalid session %d"%(
                session_id))
            return
        if response.success:
            ##success
            endpoint = self.endpoint_manager.getSession(session_id)
            endpoint.setRemoteName(response.name)
            endpoint.setConnected()
            ##send connect ACK
            ack = ConnectAcknowledge()
            ack.name = self.name
            ack.session = endpoint.remote_session

            self.send(session_id, [ack.toString()])
            
##            self.logger.info("[%08X]connect success, remote name '%s'"%(session_id, endpoint.remote_name))
            self.notifySessionConnected(endpoint.remote_name, session_id)
            return
        elif not response.need_digest:
            ##auth fail
            self.logger.error("[%08X]connect request reject"%(session_id))
            self.endpoint_manager.deallocate(session_id)
            return
        else:
            ##need digest
            ##check local session
            challenge_key = response.server_key
            remote_session = response.sender
            nat_ip = address[0]
            nat_port = address[1]
##            self.logger.info("[%08X]connect request need disgest, challenge key '%s', remote session [%08X] (nat address '%s:%d')"%\
##                      (session_id, challenge_key, remote_session, nat_ip, nat_port))
            
            endpoint = self.endpoint_manager.getSession(session_id)
            ##update remote address
            endpoint.setRemoteAddress(remote_session, response.ip, response.port, nat_ip, nat_port)
          
            ##compute dynamic key
            verify_key = self.computeVerifyDigest(response.client_key, challenge_key)

            request = ConnectRequest()
            request.client_key = response.client_key
            request.digest = verify_key
            request.name = self.name
            request.sender = session_id
            request.session = endpoint.remote_session

            self.send(session_id, [request.toString()])
            
    def handleConnectACK(self, msg, session_id):
        endpoint = self.endpoint_manager.getSession(session_id)
        if not endpoint:
            self.logger.error("<Transporter>accept connect ack fail, invalid session %d"%(
                session_id))
            return
        endpoint.setConnected()
##        self.logger.info("[%08X]connect success, remote name '%s'"%(session_id, endpoint.remote_name))
        self.notifySessionConnected(endpoint.remote_name, session_id)
    
    def handleDisconnectRequest(self, msg, session_id):
        endpoint = self.endpoint_manager.getSession(session_id)
        if not endpoint:
            self.logger.error("<Transporter>accept disconnect request fail, invalid session %d"%session_id)
            return
        ##response
        response = DisconnectResponse()
        response.success = True
        response.session = endpoint.remote_session
        
        self.send(session_id, [response.toString()])
##        self.logger.info("[%08X]disconnect success, remote node '%s' removed"%(session_id, endpoint.remote_name))
        self.notifySessionDisconnected(endpoint.remote_name, session_id)
        self.endpoint_manager.deallocate(session_id)        
        
    def handleDisconnectResponse(self, msg, session_id):
        endpoint = self.endpoint_manager.getSession(session_id)
        if not endpoint:
            self.logger.error("<Transporter>accept disconnect response fail, invalid session %d"%session_id)
            return
        self.info("[%08X]disconnect success, remote node '%s' removed"%(session_id, endpoint.remote_name))
        self.notifySessionDisconnected(endpoint.remote_name, session_id)
        self.endpoint_manager.deallocate(session_id)
        
    def handleMessageData(self, msg, session_id):
        endpoint = self.endpoint_manager.getSession(session_id)
        if not endpoint:
            self.logger.error("<Transporter>handle message data fail, invalid session %d"%session_id)
            return
        
        if 1 == msg.total:
            ##single data
            message = AppMessage.fromString(msg.data)
            
        else:
            ##multi data
            endpoint.cacheData(msg.serial, msg.index, msg.total, msg.data)
            if not endpoint.isCacheFinished(msg.serial):
                return
            ##finished
            content = endpoint.obtainCachedData(msg.serial)
            
            message = AppMessage.fromString(content)
                           
        self.notifyMessageReceived(message, session_id)


    def computeChallengeKey(self, client_key):
        number1 = zlib.crc32(client_key)&0xFF0F00FF
        number2 = zlib.crc32(self.server_key)&0xF0FFFF0F
        number3 = number1^number2
        sha = hashlib.sha1()
        sha.update(str(number3))
        return sha.hexdigest()
    
    def computeVerifyDigest(self, client_key, challenge_key):
        number1 = zlib.crc32(client_key)&0xFFFFF0FF
        number4 = zlib.crc32(challenge_key)&0xF0F0FFF0
        number5 = number1^number4
        sha = hashlib.sha1()
        sha.update(str(number5))
        return sha.hexdigest() 

    def notifyMessageReceived(self, message, session_id):
        event = DispatchEvent()
        event.type = DispatchEvent.type_message
        event.message = message
        event.session_id = session_id
        self.dispatch([event])
        
    def notifySessionConnected(self, remote_name, session_id):
##        self.debug("<SessionLayer>session connected, remote name '%s', id [%08X]"%(remote_name, session_id))
        event = DispatchEvent()
        event.type = DispatchEvent.type_connected
        event.name = remote_name
        event.session_id = session_id
        self.dispatch([event])

    def notifySessionDisconnected(self, remote_name, session_id):
##        self.debug("<SessionLayer>session disconnected, remote name '%s', id [%08X]"%(remote_name, session_id))
        event = DispatchEvent()
        event.type = DispatchEvent.type_disconnected
        event.name = remote_name
        event.session_id = session_id
        self.dispatch([event])
            
    def dispatch(self, event_list):
        if not self.notify_pool.put(event_list):
            self.logger.warn("<Transporter>add %d event to notify pool fail!"%(
                len(event_list)))
            return False
        return True

    def notifyEvent(self, index, event_list):
        if not self.handler:
            return
        
        for event in event_list:
            if DispatchEvent.type_message == event.type:
                self.handler.onMessageReceived(event.message, event.session_id)
            elif DispatchEvent.type_connected == event.type:
                self.handler.onSessionConnected(event.name, event.session_id)
            elif DispatchEvent.type_disconnected == event.type:
                self.handler.onSessionDisconnected(event.name, event.session_id)                    

    def timeoutCheckProcess(self):
        channel_check = []
        session_check = []
        retry_count = 0
        fail_count = 0
        keep_alive_interval = 5
        keep_alive_counter = 0
        while self.isRunning():
            self.timeout_check_event.wait(self.timeout_check_interval)
            if not self.isRunning():
                ##service stopped
                break
            ##check channel task
            begin = datetime.datetime.now()
            for channel in range(self.channel):
                task_manager = self.channel_managers[channel]
                retry_list, remove_list = task_manager.checkTimeout()
                if 0 != len(retry_list):
                    packets = []
                    retry_count += len(retry_list)
                    for task_id in retry_list:
##                        self.logger.debug("<Transporter>channel %d:resend task %d"%(
##                            channel, task_id))
                        task = task_manager.getTask(task_id)
                        if not task:
                            continue
                        packets.append((task.address, task.data))
                        
                    if not self.send_pool.put(channel, packets):
                        self.logger.warn("<Transporter>channel %d:resend task to send pool fail, %d tasks"%(
                            channel, len(retry_list)))
                        break
                    self.logger.warn("<Transporter>channel %d:resend %d tasks"%(
                        channel, len(retry_list)))
                        
                if 0 != len(remove_list):
                    ##debug
##                    for task_id in remove_list:
##                        self.logger.debug("<Transporterchannel %d:deallocate task %d"%(
##                            channel, task_id))                        
                    fail_count += len(remove_list)
                    task_manager.deallocate(remove_list)
                    self.logger.warn("<Transporter>channel %d:deallocate %d failed task"%(
                        channel, len(remove_list)))
                    
             ##end for channel in range(self.channel):
            channel_check.append(elapsedMilliseconds(datetime.datetime.now() - begin))

            begin = datetime.datetime.now()
            ##check endpoint session
            timeout_list, alive_list, disconnect_list = self.endpoint_manager.checkTimeout()
            for session_id in timeout_list:
                ##timeout session
                endpoint = self.endpoint_manager.getSession(session_id)
                endpoint.setDisconnected()
##                self.logger.warn("[%08X]session disconnected, remote name '%s'"%(
##                    session_id, endpoint.remote_name))
                
            for session_id in disconnect_list:
                ##disconnected session
                endpoint = self.endpoint_manager.getSession(session_id)
##                self.logger.warn("[%08X]resume session timeout, remote name '%s'"%(
##                    session_id, endpoint.remote_name))
                self.notifySessionDisconnected(endpoint.remote_name, session_id)
                self.endpoint_manager.deallocate(session_id)

            keep_alive_counter += 1
            if keep_alive_counter > keep_alive_interval:
                keep_alive_counter = 0
##                self.logger.info("<Transporter>send %d keep alive"%(
##                    len(alive_list)))
                for session_id in alive_list:
                    ##alive session
                    endpoint = self.endpoint_manager.getSession(session_id)
                    
                    request = KeepAlive()
                    request.name = self.name
                    request.session = endpoint.remote_session                    
                    
                    self.send(session_id, [request.toString()])
                
                
            session_check.append(elapsedMilliseconds(datetime.datetime.now() - begin))
            
##        self.logger.info("<Transporter>check process finished, %d retry, %d fail"%(
##            retry_count, fail_count))
        ##channel check
##        self.logger.info("<Transporter>channel check %d, total %.2f ms, avg %.3f ms, %.2f ~ %.2f ms"%(
##            len(channel_check), sum(channel_check), sum(channel_check)/len(channel_check),
##            min(channel_check), max(channel_check)))
##
##        self.logger.info("<Transporter>session check %d, total %.2f ms, avg %.3f ms, %.2f ~ %.2f ms"%(
##            len(session_check), sum(session_check), sum(session_check)/len(session_check),
##            min(session_check), max(session_check)))
