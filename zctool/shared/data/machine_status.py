#!/usr/bin/python
import datetime

class DiskStatistic(object):
    rd_req = 0
    rd_bytes = 0
    wr_req = 0
    wr_bytes = 0
    io_error = 0        
    rd_speed = 0
    wr_speed = 0
    def __init__(self, rd_req = 0, rd_bytes = 0, wr_req = 0, wr_bytes = 0, io_error = 0, rd_speed = 0, wr_speed = 0):
        self.rd_req = rd_req
        self.rd_bytes = rd_bytes
        self.wr_req = wr_req
        self.wr_bytes = wr_bytes
        self.io_error = io_error
        self.rd_speed = rd_speed
        self.wr_speed = wr_speed
        
    def __add__(self, other):
        self.rd_req += other.rd_req
        self.rd_bytes += other.rd_bytes
        self.wr_req += other.wr_req
        self.wr_bytes += other.wr_bytes
        self.io_error += other.io_error
        self.rd_speed += other.rd_speed
        self.wr_speed += other.wr_speed
        return self
    
##    def __repr__(self):
##        return "DiskStatistic(rd_req=%d, rd_bytes=%d, wr_req=%d, wr_bytes=%d, io_error=%d, rd_speed=%d, wr_speed=%d)"%(
##            self.rd_req, self.rd_bytes, self.wr_req, self.wr_bytes,
##            self.io_error, self.rd_speed, self.wr_speed)
    
class Disk(object):
    device = ""
    bus_type = ""
    source = ""
    used_volume = 0
    total_volume = 0
    def __init__(self, device = "", bus_type = "", source = "", \
                 used_volume = 0, total_volume = 0):
        self.device = device
        self.bus_type = bus_type
        self.source = source
        self.used_volume = used_volume
        self.total_volume = total_volume

##    def __repr__(self):
##        return "Disk(dev=%s, bus=%s, source='%s', used=%d, total=%d)"%(
##            self.device,self.bus_type,self.source,self.used_volume, self.total_volume)
    
class NetworkStatistic(object):
    rx_bytes = 0
    rx_packets = 0
    rx_errs = 0
    rx_drop = 0
    tx_bytes = 0
    tx_packets = 0
    tx_errs = 0
    tx_drop = 0      
    rx_speed = 0
    tx_speed = 0
    def __init__(self, rx_bytes = 0,rx_packets = 0,rx_errs = 0,rx_drop = 0, tx_bytes = 0,tx_packets = 0,tx_errs = 0,tx_drop = 0, rx_speed = 0, tx_speed = 0):
        self.rx_bytes = rx_bytes
        self.rx_packets = rx_packets
        self.rx_errs = rx_errs
        self.rx_drop = rx_drop
        self.tx_bytes = tx_bytes
        self.tx_packets = tx_packets
        self.tx_errs = tx_errs
        self.tx_drop = tx_drop
        self.rx_speed = rx_speed
        self.tx_speed = tx_speed

    def __add__(self, other):
        self.rx_bytes += other.rx_bytes
        self.rx_packets += other.rx_packets
        self.rx_errs += other.rx_errs
        self.rx_drop += other.rx_drop
        self.tx_bytes += other.tx_bytes
        self.tx_packets += other.tx_packets
        self.tx_errs += other.tx_errs
        self.tx_drop += other.tx_drop
        self.rx_speed += other.rx_speed
        self.tx_speed += other.tx_speed
        return self
    
##    def __repr__(self):
##        return "NetworkStatistic(rx_bytes=%d, rx_packets=%d, rx_errs=%d, rx_drop=%d, tx_bytes=%d, tx_packets=%d, tx_errs=%d, tx_drop=%d, rx_speed=%d, tx_speed=%d)"%(
##            self.rx_bytes, self.rx_packets, self.rx_errs, self.rx_drop,
##            self.tx_bytes, self.tx_packets, self.tx_errs, self.tx_drop,
##            self.rx_speed, self.tx_speed)

class NetworkInterface(object):
    device = ""
    mac = ""
    ip = ""
    network_type = 0
    def __init__(self, device = "", mac = "", ip = "", \
                 network_type = 0, statistic = NetworkStatistic()):
        self.device = device
        self.mac = mac
        self.ip = ip
        self.network_type = network_type
        self.statistic = statistic

##    def __repr__(self):
##        return "DomainInterface(dev=%s, mac=%s, ip=%s, statistic=%s)"%\
##               (self.device,self.mac,self.ip,self.statistic)

class MachineStatus(object):
    server_room = ""
    computer_rack = ""
    node_name = ""
    cpu_count = 0
    ##total usage
    total_cpu_usage = 0.0
    ##list of usage 18.3%, cpu0,cpu1...
    separate_cpu_usage = []
    ##in bytes
    total_memory = 0
    available_memory = 0
    memory_usage = 0.0
    
    ##in bytes,list of Disk
    disks = []
    ##total disk in bytes
    total_volume = 0
    used_volume = 0
    disk_usage = 0.0
    
    ##DiskStatistic(rd_req, rd_bytes, wr_req, wr_bytes, io_error, rd_speed, wr_speed)
    disk_statistic = DiskStatistic()
    ##dict of mac:NetworkInterface(dev, mac, ip, network_type, statistic)
    networks = {}
    ##NetworkStatistic(rx_bytes,rx_packets,rx_errs,rx_drop,tx_bytes,tx_packets,tx_errs,tx_drop, rx_speed, tx_speed)
    network_statistic = NetworkStatistic()
    timestamp = ""
    operation_system = ""

