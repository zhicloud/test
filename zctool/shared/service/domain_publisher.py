#!/usr/bin/python
import socket
import struct
import time
import sys
import socket_util
from guardian_thread import *

class DomainPublisher(GuardianThread):
    def __init__(self, mcast_address = "224.6.6.6", mcast_port = 5666):
        GuardianThread.__init__(self, "publisher")
        LoggerHelper.__init__(self, "publisher")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        ##intranet ttl <=32
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        ##port reusable
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', mcast_port))
        self.mreq = struct.pack("=4sl", socket.inet_aton(mcast_address), socket.INADDR_ANY)
        self.group = (mcast_address, mcast_port)
        self.service = []

    def addService(self, address, port):
        self.service.append((address, port))
        
    def run(self):
        buf_size = 1024
        timeout = 5
        try:
            ##join group
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq)
            ##disable self loop        
##            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
        except socket.error as e:
            self.error("join multicast group exception:%d, %s"%(e.errno, e.strerror))
            return
        
        while self.isRunning():
            ##wait query
            result, request, address = socket_util.recvfrom(self.sock, buf_size, timeout)
            if not result:
                ##timeout or error
                continue
            ##valid request format:query:id
            param = request.split(':')
            if 2 != len(param):
                ##invalid
                continue
            if param[0] != "query":
                ##invalid
                continue
            
            request_id = int(param[1])
            ##format:"result:id,ip,port,request_ip"
            service = self.service[0]
            response = "result:%d,%s,%d,%s"%(request_id, service[0], service[1], address[0])
            ##send response
            result, number = socket_util.sendto(self.sock, response, self.group, timeout)
            if not result:
                self.warn("publisher send query response fail")
            
        ##end while self.isRunning():
        
    def onStopping(self):
        self.info("closing domain publisher...")
        try:
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP , self.mreq)
        except socket.error as e:
            self.warn("leave multicast group exception:%d, %s"%(e.errno, e.strerror))
        
        try:
            self.sock.close()
            self.info("domain publisher closed")
        except socket.error as e:
            self.warn("close socket exception:%d, %s"%(e.errno, e.strerror))       
        

if __name__ == '__main__':
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)
    ##test case
    publisher = DomainPublisher()
    publisher.addService("127.0.0.1", 1234)
    publisher.start()
    time.sleep(10)
    publisher.stop()
