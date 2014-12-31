#!/usr/bin/python
from service.message_define import *

class SystemStatus(object):
    physical_node = 0
    total_physical_node = 0
    virtual_node = 0
    total_virtual_node = 0
    network = 0
    total_network = 0
    total_cpu_usage = 0.0
    memory_usage = 0.0
    disk_usage = 0.0
    read_request = 0
    read_bytes = 0
    write_request = 0
    write_bytes = 0
    io_error = 0
    received_bytes = 0
    recevied_packets = 0
    recevied_errors = 0
    received_drop = 0
    sent_bytes = 0
    sent_packets = 0
    sent_errors = 0
    sent_drop = 0
    timestamp = ""

    def toMessage(self, msg):
        setUIntArray(msg, ParamKeyDefine.physical_node,
                     [self.physical_node, self.total_physical_node])
        setUIntArray(msg, ParamKeyDefine.virtual_node,
                     [self.virtual_node, self.total_virtual_node])
        setUIntArray(msg, ParamKeyDefine.network,
                     [self.network, self.total_network])
        setFloat(msg, ParamKeyDefine.total_cpu_usage, self.total_cpu_usage)
        setFloat(msg, ParamKeyDefine.memory_usage, self.memory_usage)
        setFloat(msg, ParamKeyDefine.disk_usage, self.disk_usage)

        setUInt(msg, ParamKeyDefine.read_request, self.read_request)
        setUInt(msg, ParamKeyDefine.read_bytes, self.read_bytes)
        setUInt(msg, ParamKeyDefine.write_request, self.write_request)
        setUInt(msg, ParamKeyDefine.write_bytes, self.write_bytes)
        setUInt(msg, ParamKeyDefine.io_error, self.io_error)
        
        setUInt(msg, ParamKeyDefine.received_bytes, self.received_bytes)
        setUInt(msg, ParamKeyDefine.recevied_packets, self.recevied_packets)
        setUInt(msg, ParamKeyDefine.recevied_errors, self.recevied_errors)
        setUInt(msg, ParamKeyDefine.received_drop, self.received_drop)
        setUInt(msg, ParamKeyDefine.sent_bytes, self.sent_bytes)
        setUInt(msg, ParamKeyDefine.sent_packets, self.sent_packets)
        setUInt(msg, ParamKeyDefine.sent_errors, self.sent_errors)
        setUInt(msg, ParamKeyDefine.sent_drop, self.sent_drop)
        
        setString(msg, ParamKeyDefine.timestamp, self.timestamp)        

    def fromMessage(self, msg):
        p_array = getUIntArray(msg, ParamKeyDefine.physical_node)
        self.physical_node = p_array[0]
        self.total_physical_node = p_array[1]

        v_array = getUIntArray(msg, ParamKeyDefine.virtual_node)
        self.virtual_node = v_array[0]
        self.total_virtual_node = v_array[1]

        n_array = getUIntArray(msg, ParamKeyDefine.network)
        self.network = n_array[0]
        self.total_network = n_array[1]       
        
        self.total_cpu_usage = getFloat(msg, ParamKeyDefine.total_cpu_usage)
        self.memory_usage = getFloat(msg, ParamKeyDefine.memory_usage)
        self.disk_usage = getFloat(msg, ParamKeyDefine.disk_usage)

        self.read_request = getUInt(msg, ParamKeyDefine.read_request)
        self.read_bytes = getUInt(msg, ParamKeyDefine.read_bytes)
        self.write_request = getUInt(msg, ParamKeyDefine.write_request)
        self.write_bytes = getUInt(msg, ParamKeyDefine.write_bytes)
        self.io_error = getUInt(msg, ParamKeyDefine.io_error)
        
        self.received_bytes = getUInt(msg, ParamKeyDefine.received_bytes)
        self.recevied_packets = getUInt(msg, ParamKeyDefine.recevied_packets)
        self.recevied_errors = getUInt(msg, ParamKeyDefine.recevied_errors)
        self.received_drop = getUInt(msg, ParamKeyDefine.received_drop)
        self.sent_bytes = getUInt(msg, ParamKeyDefine.sent_bytes)
        self.sent_packets = getUInt(msg, ParamKeyDefine.sent_packets)
        self.sent_errors = getUInt(msg, ParamKeyDefine.sent_errors)
        self.sent_drop = getUInt(msg, ParamKeyDefine.sent_drop)
        
        self.timestamp = getString(msg, ParamKeyDefine.timestamp)  
