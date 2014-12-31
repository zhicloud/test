#!/usr/bin/python
import socket
import struct
import random
import time
import sys
import os
import os.path
import socket_util
import threading
from guardian_thread import *

class DomainNode(GuardianThread):
##    service_pipe_path = "/tmp/pipe"
    def __init__(self, domain, logger_name, mcast_address = "224.6.6.6", mcast_port = 5666):
        GuardianThread.__init__(self, logger_name)
        LoggerHelper.__init__(self, logger_name)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        ##intranet ttl <=32
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        ##port reusable
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', mcast_port))
        self.mreq = struct.pack("=4sl", socket.inet_aton(mcast_address), socket.INADDR_ANY)
        self.group = (mcast_address, mcast_port)
        self.service_published = False
        self.service = []
        self.timeout = 5
        self.handler = None
        self.domain = domain
        self.request_id = 0

    def addService(self, service_name, address, port):
        self.service.append((service_name, address, port))

    def bindHandler(self, handler):
        self.handler = handler
        
    def publish(self):
        if 0 != len(self.service):
            self.service_published = True
##            ##local pipe
##            self.createPipe()
            ##notify
            for service in self.service:
                ##1-notify,param:"name, ip, port"
                socket_util.sendto(self.sock, "1:%s, %s,%d"%(service[0], service[1], service[2]), self.group, self.timeout) 

    def query(self):            
        self.request_id = int(random.random() * 10000)
        ##2-query,param:"serial"
        command = "2:%d"%(self.request_id)
        socket_util.sendto(self.sock, command, self.group, self.timeout)
        self.debug("send query request ('%s') to address '%s'"%(command, self.group))

    """
    format "cmd_id:cmd_param"
    cmd_id:
    1-notify,param:"ip,port"
    2-query,param:"serial"
    3-result,param:"serial,ip,port,request_ip"
    """
        
    def run(self):
        buf_size = 1024
        
        while self.isRunning():
            ##wait query
            result, request, address = socket_util.recvfrom(self.sock, buf_size, self.timeout)
            if result:
                content = request.split(':')
                if 2 == len(content):
                    cmd_id = content[0]
                    if "1" == cmd_id:
                        self.handleNotify(content[1])
                    elif "2" == cmd_id:
                        ##query
                        self.handleQuery(content[1], address[0])
                    elif "3" == cmd_id:
                        ##result
                        self.handleResult(content[1])
            
        ##end while self.isRunning():
            
    def handleQuery(self, param, request_ip):
        if not self.service_published:
            self.debug("ignore query request")
            return
        
        if 0 == len(self.service):
            ##no service
            self.warn("receive service query from '%s', but no service available"%(
                request_ip))
            return
        request_id = int(param)
        ##format:"3:id,name,ip,port,request_ip"
        service = self.service[0]
        response = "3:%d,%s,%s,%d,%s"%(request_id, service[0], service[1], service[2], request_ip)
        self.debug("handle query '%s' from '%s'"%(param, request_ip))
        ##send response
        result, number = socket_util.sendto(self.sock, response, self.group, self.timeout)
        self.debug("send query response '%s' to '%s'"%(response, self.group))
        if not result:
            self.warn("send query response to '%s' fail"%(request_ip))
                
    def handleNotify(self, param):
        if self.service_published:
            self.debug("ignore notify event")
            return
        ##1-notify,param:"name,ip,port"
        address = param.split(',')
        if 2 != len(address):
            self.warn("invalid notify param '%s'"%(param))
            return
        service_name = address[0]
        service_ip = address[1]
        service_port = int(address[2])
        self.debug("receive notify, service %s(%s:%d)"%(service_name, service_ip, service_port))
        self.__notifyService(service_name, service_ip, service_port, "")
        
        
    def handleResult(self, param):
        if 0 == self.request_id:
            self.debug("ignore query result")
            return
        #3-result,param:"serial,name,ip,port,request_ip"
        result = param.split(',')
        if 5 != len(result):
            self.warn("receive invalid result param '%s'"%(param))
            return
        if self.request_id != int(result[0]):
            self.info("receive result, but request id dismatched %d:%d"%(self.request_id, int(result[0])))
            return
        service_name = result[1]
        service_ip = result[2]
        service_port = int(result[3])
        request_ip = result[4]
        self.debug("query result received, service %s(%s:%d), requestor %s"%(
            service_name, service_ip, service_port, request_ip))
        self.request_id = 0
        self.__notifyService(service_name, service_ip, service_port, request_ip)
        
    def onStarted(self):
        try:            
            self.info("<DomainNode>try join group %s, domain '%s'..."%(
                self.group, self.domain))
            
            ##join group
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq)
            ##disable self loop        
##            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
        except socket.error as e:
            self.error("<DomainNode>join multicast group exception:%d, %s"%(e.errno, e.strerror))
            return
        
    def onStopping(self):
        self.info("<DomainNode>closing domain publisher...")
        try:
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP , self.mreq)
        except socket.error as e:
            self.warn("<DomainNode>leave multicast group exception:%d, %s"%(e.errno, e.strerror))
        
        try:
            self.sock.close()
            self.info("<DomainNode>domain publisher closed")
        except socket.error as e:
            self.warn("<DomainNode>close socket exception:%d, %s"%(e.errno, e.strerror)) 

    def __notifyService(self, name, ip, port, request_ip):
        if self.handler:
            self.handler(name, ip, port, request_ip)
            
if __name__ == '__main__':
    def onServiceAvailable(name, ip, port, request_ip):
        print "service available:",name, ip, port, request_ip
        
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)
    ##argv:
    ##-s:server
    if (len(sys.argv) > 1) and ("-s" == sys.argv[1]):
        server = DomainNode("test", "server")
        server.addService("dataserver_abc", "172.168.0.30", 1234)
        server.start()
        server.publish()
        time.sleep(30)
        server.stop()
    else:
        node = DomainNode("test", "node")
        node.bindHandler(onServiceAvailable)
        node.start()
        node.query()
        time.sleep(15)
        node.stop()
