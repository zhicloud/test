#!/usr/bin/python
import random
import uuid
import datetime
import time
import threading
import logging
from service.message_define import *
from transporter import *
from data.machine_status import *
from data.host_status import *
from data.domain_status import *
from service.time_util import *
from service.timed_invoker import *

def generateMachineStatus(status, disk_count, network_count):
    status.cpu_count = int(random.random()*3)+1
    status.total_cpu_usage = random.random()*100
    status.separate_cpu_usage = []
    for i in range(status.cpu_count):
        status.separate_cpu_usage.append(random.random()*100)

    status.total_memory = int(random.random()*16*1024*1024*1024)
    status.memory_usage = random.random()*100
    status.available_memory = int(status.total_memory * status.memory_usage)
    status.disks = []
    for i in range(disk_count):
        used = int(random.random()*256*1024*1024*1024)
        status.disks.append(Disk("disk%d"%(i+1), "virtio", "hdx",
                          used, used + int(random.random()*256*1024*1024*1024)))

    status.total_volume = int(random.random()*512*1024*1024*1024)
    status.disk_usage = random.random()*100
    status.used_volume = int(status.total_volume * status.disk_usage)
    status.disk_statistic.rd_req = int(random.random()*1024*1024*1024)
    status.disk_statistic.rd_bytes = int(random.random()*1024*1024*1024)
    status.disk_statistic.wr_req = int(random.random()*1024*1024*1024)
    status.disk_statistic.wr_bytes = int(random.random()*1024*1024*1024)
    status.disk_statistic.io_error = int(random.random()*1024*1024*1024)
    status.disk_statistic.rd_speed = int(random.random()*1024*1024*1024)
    status.disk_statistic.wr_speed = int(random.random()*1024*1024*1024)

    status.networks = {}
    for i in range(network_count):
        mac = uuid.uuid4().hex
        statis = NetworkStatistic(int(random.random()*1024*1024*1024),
                                  int(random.random()*1024*1024*1024),
                                  int(random.random()*1024*1024*1024),
                                  int(random.random()*1024*1024*1024),
                                  int(random.random()*1024*1024*1024),
                                  int(random.random()*1024*1024*1024),
                                  int(random.random()*1024*1024*1024),
                                  int(random.random()*1024*1024*1024),
                                  int(random.random()*1024*1024*1024),
                                  int(random.random()*1024*1024*1024))
                                  
        status.networks[mac] = NetworkInterface("eth%d"%i, mac, "192.168.0.1",
                                                0, statis)
        status.network_statistic += statis
    status.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status.operation_system = "linux2"
    
def generateStatusData(node_count, domain_in_node):
    host_list = []
    domain_list = []
    for i in range(node_count):
        server_room = "server_room%d"%(random.random()*100)
        computer_rack = "computer_rack_%d"%(random.random()*1000)
        node_name = "node_%d"%(i+1)
        host = HostStatus()
        host.server_room = server_room
        host.computer_rack = computer_rack
        host.node_name = node_name
        host.hostname = "hostname_%d"%(random.random()*100)
        host.fullname = "%s.%s.%s"%(server_room, computer_rack, node_name)
        host.version = "1.0"
        generateMachineStatus(host, 2, 2)
        host.domains = []
        for j in range(domain_in_node):
            domain = DomainStatus()
            domain.server_room = server_room
            domain.computer_rack = computer_rack
            domain.node_name = node_name
            domain.name = "domain_%d"%(j + 1)
            domain.fullname = "%s.%s.%s.%s"%(server_room, computer_rack,
                                             node_name, domain.name)
            domain.uuid = uuid.uuid4().hex
            generateMachineStatus(domain, 2, 2)
            host.domains.append(domain.uuid)
            domain_list.append(domain)
            
        host_list.append(host)
        
    return host_list, domain_list

class ServerProxy(object):
    total_message = 0
    total_length = 0
    connected = []
    first_packet = None
    last_packet = None
    def __init__(self, server_ip, channel = 1):
        self.finish_event = threading.Event()
        self.server = Transporter("server", "server",
                                  self,
                                  channel,
                                  channel,
                                  1,
                                  64*1024)
        self.server.bind(server_ip)
        self.server.start()
        self.logger = logging.getLogger("server")
        
    def onMessageReceived(self, message, session_id):
        if message.id == EventDefine.monitor_data:
            if not self.first_packet:
                self.first_packet = datetime.datetime.now()
            self.last_packet = datetime.datetime.now()
            content = getString(message, ParamKeyDefine.filename)
            self.total_message += 1
            self.total_length += len(content)
            
        elif message.id == RequestDefine.stop_statistic:
            ##response            
            sent_bytes = getUInt(message, ParamKeyDefine.sent_bytes)
            sent_packets = getUInt(message, ParamKeyDefine.sent_packets)
            response = getResponse(RequestDefine.stop_statistic)
            setUInt(response, ParamKeyDefine.received_bytes, self.total_length)
            setUInt(response, ParamKeyDefine.recevied_packets, self.total_message)       
            self.server.sendMessage(self.connected[0], [response])
            
            self.logger.info("receive stop response")
            self.logger.info("test result:received %d/%d bytes(%d/%d messages)"%(
                self.total_length, sent_bytes,
                self.total_message, sent_packets))
            if self.first_packet:
                elapsed = elapsedSeconds(self.last_packet - self.first_packet)
                speed = float(self.total_length*8/(1024*1024))/elapsed
                lost = float(sent_packets - self.total_message)*100/sent_packets
                self.logger.info("receive speed %.2f m/s, lost %.2f%%"%(
                    speed, lost))
            
            
            self.finish_event.set()
        
    def onSessionConnected(self, remote_name, session_id):
        self.logger.info("remote node '%s'[%08X] connected"%(
            remote_name, session_id))
        self.connected.append(session_id)
        
    def onSessionDisconnected(self, remote_name, session_id):
        self.logger.info("remote node '%s'[%08X] disconnected"%(
            remote_name, session_id))
        
    def waitResult(self, timeout = 30):
        self.finish_event.wait(timeout)

    def finish(self):
        time.sleep(3)
        for session_id in self.connected:
            self.server.disconnect(session_id)
        self.server.stop()
        
class ClientProxy(object):
    connected = []
##    node_count = 200
##    domain_in_node = 10
##    total_host = 0
##    total_domain = 0
    total_length = 0
    total_message = 0
    first_packet = None
    last_packet = None
    def __init__(self, server_ip, server_port, client_ip, channel,
            duration, message_count, message_size):
        self.channel = channel
        self.duration = duration
        self.message_count = message_count
        self.message_size = message_size
        self.finish_event = threading.Event()
        self.client = Transporter("client", "client",
                                  self,
                                  channel,
                                  channel,
                                  1,
                                  64*1024)
        self.client.bind(client_ip)
        self.client.start()
        for i in range(channel):
            self.client.connect(server_ip, server_port)
            
##        self.host_count = 0
##        self.domain_count = 0
##        for i in range(self.node_count):
##            host_list, domain_list = generateStatusData(1, self.domain_in_node)            
##
##            host_event = getEvent(EventDefine.node_status_update)
##            HostStatus.packToMessage(host_event, host_list)
##            self.message_list.append(host_event)
##
##            domain_event = getEvent(EventDefine.domain_status_update)
##            DomainStatus.packToMessage(domain_event, domain_list)
##            self.message_list.append(domain_event)
##
##            self.host_count += len(host_list)
##            self.domain_count += len(domain_list)            
        
        self.signal = threading.Event()
        self.logger = logging.getLogger("client")        
        
    def onMessageReceived(self, message, session_id):
        if message.id == RequestDefine.stop_statistic:
            ##response
            self.logger.info("receive stop response")
            received_bytes = getUInt(message, ParamKeyDefine.received_bytes)
            recevied_packets = getUInt(message, ParamKeyDefine.recevied_packets)  
            self.logger.info("test result:received %d/%d bytes(%d/%d messages)"%(
                received_bytes, self.total_length,
                recevied_packets, self.total_message))
            if self.first_packet:
                elapsed = elapsedSeconds(self.last_packet - self.first_packet)
                speed = float(self.total_length*8/(1024*1024))/elapsed
                lost = float(self.total_message - recevied_packets)*100/self.total_message
                self.logger.info("send speed %.2f m/s, lost %.2f%%"%(
                    speed, lost))
            
            self.finish_event.set()
    
    def onSessionConnected(self, remote_name, session_id):
        self.logger.info("remote node '%s'[%08X] connected"%(
            remote_name, session_id))
        self.connected.append(session_id)
        if self.channel == len(self.connected):
##            self.logger.info("all connected")
            time.sleep(1)
            self.startTest()
        
    def onSessionDisconnected(self, remote_name, session_id):
        pass
    
    def sendProcess(self):
        if not self.first_packet:
            self.first_packet = datetime.datetime.now()
        for j in range(self.channel):
            session_id = self.connected[j]
            request_list = self.segs[j]
##            self.logger.info("dispatch %d datagrams to channel %d"%(
##                len(request_list), session_id))
            self.client.send(session_id, request_list)
        self.last_packet = datetime.datetime.now()
            
        self.total_message += self.message_count
        self.total_length += self.message_count * self.message_size
            
    def startTest(self):
        content = ""
        for i in range(self.message_size):
            content += chr(int(random.random()*94 + 32))            

        event = getEvent(EventDefine.monitor_data)
        setString(event, ParamKeyDefine.filename, content)

        message_data = MessageData()
        message_data.serial = 1
        message_data.index = 1
        message_data.total = 1
        message_data.data = event.toString()
        
            
        total_length = self.message_count
        tmp = total_length%self.channel
        if 0 != tmp:
            length = (total_length - tmp)/(self.channel - 1)
        else:
            length = total_length/self.channel
            
        self.segs = []
        for i in range(len(self.connected)):
            begin = i * length
            end = begin + length
            if end > total_length:
                end = total_length
            session_id = self.connected[i]
            message_data.session = session_id
            
            datagram_list = []
            for j in range(begin, end):
                datagram_list.append(message_data.toString())
            
            self.segs.append(datagram_list)
            
        ##start
        start = getRequest(RequestDefine.start_statistic)
        self.client.sendMessage(self.connected[0], [start])
        
        invoker = TimedInvoker(self.sendProcess)
        invoker.start()
        
        self.logger.info("start send message")
        time.sleep(self.duration + 1)
        
        invoker.stop() 
        ##stop
        stop = getRequest(RequestDefine.stop_statistic)
        setUInt(stop, ParamKeyDefine.sent_bytes, self.total_length)
        setUInt(stop, ParamKeyDefine.sent_packets, self.total_message)    
        self.client.sendMessage(self.connected[0], [stop])
       
        time.sleep(3)
    def waitResult(self, timeout = 30):
        self.finish_event.wait(timeout)

    def finish(self):
        time.sleep(1)
        for session_id in self.connected:
            self.client.disconnect(session_id)
            
        self.client.stop()
        

if __name__ == '__main__':
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)

    server_channel = 2
    client_channel = 10
    duration = 20
##    message_count = 1280
    message_count = 512
    message_size = 10*1024
    timeout = duration + 10
##    message_size = 50*1024
    
    server_ip = "192.168.66.204"
##    server_ip = "192.168.66.103"
    server_port = 5600
##    client_ip = "192.168.66.102"
    client_ip = "192.168.66.203"
    
    if len(sys.argv) > 1:
        ##server
        proxy = ServerProxy(server_ip, server_channel)
##        time.sleep(2)
        proxy.waitResult(timeout)
        proxy.finish()     
    else:
        ##client
        proxy = ClientProxy(
            server_ip, server_port, client_ip, client_channel,
            duration, message_count, message_size)
##        time.sleep(2)
        proxy.waitResult(timeout)
        proxy.finish()

        
