#!/usr/bin/python
import threading
import socket
import select
import errno
import logging
from service.service_status import StatusEnum

class PacketHandler(object):
    """
    PacketHandler for windows
    
    def initial()
    def start()
    def stop()
    def getLocalIP()
    def getDefaultPort()
    def getLocalPorts()
    def sendPacket(packet, remote_ip, remote_port)
    def sendPacketList(request_list)
    def onPacketReceived(message_list)
    """
    
    max_queue = 10000    
    threhold = 5
    max_batch = 20
    slow_interval = 1
    ##20 ms
    normal_interval = 0.02
    ##5ms
    fast_interval = 0.005

    def __init__(self,
                 listen_ip,
                 start_port,
                 port_count,
                 callback = None,
                 bufsize = 2*1024*1024,
                 send_thread = 1,
                 receive_thread = 1):
        self.local_ip = listen_ip
        self.local_ports = []
        self.start_port = start_port
        self.port_count = port_count
        self.callback = callback
        self.bufsize = bufsize
        self.sender_count = send_thread
        self.receiver_count = receive_thread
        self.status = StatusEnum.stopped
        self.status_mutex = threading.RLock()

        self.sockets = []

        self.notify_thread = threading.Thread(target=self.notifyProcess)
        self.notify_queue = []
        self.notify_lock = threading.RLock()
        self.notify_available = threading.Event()
        
        self.send_packet_queue = []
        self.send_packet_lock = threading.RLock()
        self.send_packet_available = threading.Event()
        self.send_packet_thread = threading.Thread(target=self.sendProcess)
        
        self.receive_packet_thread = threading.Thread(target=self.receiveProcess)      
        
    def getLocalIP(self):
        return self.local_ip
    
    def getDefaultPort(self):
        if 0 == len(self.local_ports):
            return -1
        else:
            return self.local_ports[0]

    def getLocalPorts(self):
        return self.local_ports
    
    def sendPacket(self, packet, remote_ip, remote_port):        
        with self.send_packet_lock:
            current_length = len(self.send_packet_queue)
            if current_length < self.max_queue:
                self.send_packet_queue.append((packet, remote_ip, remote_port))
                current_length += 1
                if (current_length < self.threhold) or (current_length > self.max_batch):
                    self.send_packet_available.set()
                return True
            else:
                logging.warn("<PacketHandler>send queue is full, %d / %d"%(
                    current_length, self.max_queue))
                return False

    def sendPacketList(self, request_list):
        """
        @request_list:list of (packet, remote_ip, remote_port)
        """
        with self.send_packet_lock:
            current_length = len(self.send_packet_queue)
            if current_length < self.max_queue:
                self.send_packet_queue.extend(request_list)
                current_length += len(request_list)
                if (current_length < self.threhold) or (current_length > self.max_batch):
                    self.send_packet_available.set()
                return True
            else:
                logging.warn("<PacketHandler>send queue is full, %d / %d"%(
                    current_length, self.max_queue))
                return False

    def onPacketReceived(self, message_list):
        """
        @message_list:list of (packet, remote_ip, remote_port)
        """
        if self.callback is not None:
                self.callback(message_list)

    def initial(self):
        max_try = 1000
        count = 0
        ip = self.local_ip
        for port in range(self.start_port, self.start_port + max_try):
            try:
                new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.bufsize)
                new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.bufsize)
                new_socket.setblocking(0)
                new_socket.bind((ip, port))
            except socket.error as e:
                continue

            ##bind success
            self.local_ports.append(port)
            self.sockets.append(new_socket)
                
            count += 1
            if count >= self.port_count:
                logging.info("<PacketHandler>%d socket(s) established"%(
                    self.port_count))
                return True
        else:
            ##no port availabe
            logging.error("<PacketHandler>not enough available port(%d required) in %s:%d~%d"%(
                self.port_count, self.local_ip, self.start_port, self.start_port + max_try))
            return False

    def start(self):
        with self.status_mutex:
            if StatusEnum.stopped != self.status:
                return False
            self.status = StatusEnum.running   
            self.send_packet_thread.start()
            self.receive_packet_thread.start()
            self.notify_thread.start()
            return True

    def stop(self):
        with self.status_mutex:
            if StatusEnum.stopped == self.status:
                return
            if StatusEnum.running == self.status:
                self.status = StatusEnum.stopping
                
                self.send_packet_available.set()
                self.notify_available.set()
                for socket in self.sockets:
                    socket.close()

        self.notify_thread.join()
        self.send_packet_thread.join()
        self.receive_packet_thread.join()
        with self.status_mutex:
            self.status = StatusEnum.stopped


    def sendProcess(self):
        while StatusEnum.running == self.status:
            ##wait request
            self.send_packet_available.wait(self.normal_interval)
            if StatusEnum.running != self.status:
                ##double protect
                break
            if self.send_packet_available.isSet():
                self.send_packet_available.clear()                      
            
            ##check send queue
            with self.send_packet_lock:
                request_count = len(self.send_packet_queue)
                if 0 == request_count:
                    continue
                fetch_count = min(request_count, self.max_batch)
                fetch_list = self.send_packet_queue[:fetch_count]
                del self.send_packet_queue[:fetch_count]

            
            while 0 != len(fetch_list):
                readable, writable, error = select.select([], self.sockets, self.sockets, self.slow_interval)
                if StatusEnum.running != self.status:
                    ##double protect
                    break
                socket_count = len(writable)
                if 0 == socket_count:
                    continue
                fetch_count = len(fetch_list)
                available_count = min(fetch_count, socket_count)

                batch_list = fetch_list[:available_count]
                del fetch_list[:available_count]
                
                socket_list = writable[:available_count]                   

                ##send data packet
                for index in range(available_count):
                    request = batch_list[index]
                    data_socket = socket_list[index]
                    
                    data = request[0]
                    remote_ip = request[1]
                    remote_port = request[2]

                    address = (remote_ip, remote_port)
                    data_length = len(data)
                    try:                        
                        result = data_socket.sendto(data, 0, address)                    
                        if data_length != result:
                            logging.warn("<PacketHandler>imcomplete packet send to address %s, %d/%d bytes"%(
                                address, result, data_length))
##                            else:
##                                logging.info("<PacketHandler>%d bytes data send by socket %d"%(
##                                    data_length, data_socket.fileno()))
                            
                    except socket.error,e:
                        if e.errno != errno.EAGAIN:
                            logging.warn("<PacketHandler>send data exception, socket %d, msg:%s"%(
                                data_socket.fileno(), e.strerror))                                
                        continue

    def receiveProcess(self):
        while StatusEnum.running == self.status:
            ##wait for signal
            readable, writable, error = select.select(self.sockets, [], self.sockets, self.slow_interval)
            if StatusEnum.running != self.status:
                ##double protect
                break
            if 0 != len(readable):                                
                ##socket ready
                packet_list = []
                for data_socket in readable:            
                    more_data = True
                    while more_data:
                        try:
                            data, address = data_socket.recvfrom(self.bufsize)
                            recv_length = len(data)
    ##                            logging.info("<PacketHandler>%d bytes data recv from socket %d"%(
    ##                                recv_length, data_socket.fileno()))
                            
                            if 0 == recv_length:
                                ##eof
                                more_data = False
                                break
                            remote_ip = address[0]
                            remote_port = address[1]
                            
                            packet_list.append((data, remote_ip, remote_port))
                            
                        except socket.error,e:
##                            if e.errno != errno.EAGAIN:
##                                logging.warn("<PacketHandler>receive data exception, socket %d, msg:%s"%(
##                                    data_socket.fileno(), e.strerror))
                            more_data = False
                            break
                        
                if 0 != len(packet_list):  
                    ##put to notify
                    self.putToNotify(packet_list)
                
    def putToNotify(self, message_list):
        with self.notify_lock:
            current_length = len(self.notify_queue)
            if current_length < self.max_queue:
                self.notify_queue.extend(message_list)
                current_length += len(message_list)
                if (current_length < self.threhold) or (current_length > self.max_batch):
                    self.notify_available.set()
                return True
            else:
                logging.warn("<PacketHandler>notify queue is full, %d / %d"%(
                    current_length, self.max_queue))
                return False
            
    def notifyProcess(self):
        while StatusEnum.running == self.status:
            ##wait signal
            self.notify_available.wait(self.normal_interval)
            if StatusEnum.running != self.status:
                ##double protect
                break
            if self.notify_available.isSet():
                self.notify_available.clear()
            
            ##check anyway
            with self.notify_lock:
                if(0 == len(self.notify_queue)):
                    ##empty
                    continue
                ##FIFO/pop front
                notify_queue = self.notify_queue
                self.notify_queue = []
                
            self.onPacketReceived(notify_queue)

    
