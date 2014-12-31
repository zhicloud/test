#!/usr/bin/python
import socket
import struct
import random
import time
import select
import socket_util

class DomainSubcriber(object):
    """
    query service address/port from multicast server
    """
    def __init__(self, mcast_address = "224.6.6.6", mcast_port = 5666):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        ##intranet ttl <=32
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        ##port reusable
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', mcast_port))
        self.mreq = struct.pack("=4sl", socket.inet_aton(mcast_address), socket.INADDR_ANY)
        self.group = (mcast_address, mcast_port)

    def query(self, retry = 3, interval = 1):
        """
        query service address/port
        @retry:retry count
        @interval:retry interval in second
        @return: ((server_ip,server_port), request_ip)
        nothing returned means query fail
        """
        timeout = 2
        random_id = int(random.random() * 10000)
        buf_size = 1024
        self.sock.settimeout(30)
        ##join group
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq)
        ##disable self loop        
##        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
        emptys = []
        incoming = [self.sock]
        ##valid request format:query:id
        request_content = "query:%d"%random_id
        ##send request:
        socket_util.sendto(self.sock, request_content, self.group, timeout)
        while retry > 0:           
            result, response = socket_util.recv(self.sock, buf_size, timeout)
            if not result:
               ##receive fail
                retry -= 1
                socket_util.sendto(self.sock, request_content, self.group, timeout)
                continue
            ##format:"result:id,ip,port,request_ip"
            param = response.split(':')
            if 2 != len(param):
                ##invalid
                continue
            if param[0] != "result":
                ##invalid
                continue
            
            result = param[1].split(',')
            if 4 != len(result):
                ##invalid
                continue
            if random_id != int(result[0]):
                ##ignore other result
                continue
            service_ip = result[1]
            service_port = int(result[2])
            request_ip = result[3]
            ##leave group
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP , self.mreq)
            self.sock.close()
            return (service_ip, service_port), request_ip

                
        ##end while retry

        ##leave group
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP , self.mreq)
        ##nothing returned means query fail        

if __name__ == '__main__':
    ##test case
    subcriber = DomainSubcriber()
    result = subcriber.query()
    if not result:
        print "query fail"
    else:
        print "query success:",result
            
