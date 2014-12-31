#!/usr/bin/python
from host_status import HostStatus
from service.message_define import *

"""
node data for monitor
"""

class NodeData(object):
    server_room = ""
    computer_rack = ""
    node_name = ""
    ip = []
    status = 0
    version = ""
    timestamp = ""
    operation_system = ""
    
    def fromHost(self, host):
        ip = []
        for interface in host.networks.values():
            if 0 != len(interface.ip):
                ip.append(interface.ip)
                
        if host.actived:
            status = 1
        else:
            status = 0
            
        self.server_room = host.server_room
        self.computer_rack = host.computer_rack
        self.node_name = host.node_name
        self.ip = ip
        self.status = status
        self.version = version
        self.timestamp = host.timestamp
        self.operation_system = host.operation_system       

    @staticmethod
    def messageFromList(msg, data_list):
        server_room = []
        computer_rack = []
        node_name = []
        ip = []
        status = []
        version = []
        timestamp = []
        operation_system = []
        for data in data_list:
            server_room.append(data.server_room)
            computer_rack.append(data.computer_rack)
            node_name.append(data.node_name)            
            ip.append(data.ip)
            status.append(data.status)
            version.append(data.version)
            timestamp.append(data.timestamp)
            operation_system.append(data.operation_system)
            
        setStringArray(msg, ParamKeyDefine.server_room, server_room)
        setStringArray(msg, ParamKeyDefine.computer_rack, computer_rack)
        setStringArray(msg, ParamKeyDefine.node_name, node_name)
        setStringArrayArray(msg, ParamKeyDefine.ip, ip)
        setUIntArray(msg, ParamKeyDefine.status, status)
        setStringArray(msg, ParamKeyDefine.version, version)
        setStringArray(msg, ParamKeyDefine.timestamp, timestamp)
        setStringArray(msg, ParamKeyDefine.operation_system, operation_system)

    @staticmethod
    def listFromMessage(msg):
        data_list = []
        node_name = getStringArray(msg, ParamKeyDefine.node_name)
        data_count = len(node_name)
        if 0 == data_count:
            return data_list
        server_room = getStringArray(msg, ParamKeyDefine.server_room)
        computer_rack = getStringArray(msg, ParamKeyDefine.computer_rack)
        ip = getStringArrayArray(msg, ParamKeyDefine.ip)
        status = getUIntArray(msg, ParamKeyDefine.status)
        version = getStringArray(msg, ParamKeyDefine.version)
        timestamp = getStringArray(msg, ParamKeyDefine.timestamp)
        operation_system = getStringArray(msg, ParamKeyDefine.operation_system)
        for i in range(data_count):
            data = HostData()
            data.server_room = server_room[i]
            data.computer_rack = computer_rack[i]
            data.node_name = node_name[i]
            data.ip = ip[i]
            data.status = status[i]
            data.version = version[i]
            data.timestamp = timestamp[i]
            data.operation_system = operation_system[i]
            data_list.append(data)

        return data_list
