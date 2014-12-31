#!/usr/bin/python
# -*- coding: utf-8 -*-
from domain_status import DomainStatus
from service.message_define import *

"""
domain data for monitor
"""

class DomainData(object):
    server_room = ""
    computer_rack = ""
    node_name = ""
    name = ""
    fullname = ""
    uuid = ""
    ip = []
    total_cpu_usage = 0.0
    memory_usage = 0.0
    disk_usage = 0.0
    status = 0
    timestamp = ""
    operation_system = ""
    
    def fromDomain(self, domain):
        ip = []
        for interface in domain.networks.values():
            if 0 != len(interface.ip):
                ip.append(interface.ip)
            
        self.server_room = domain.server_room
        self.computer_rack = domain.computer_rack
        self.node_name = domain.node_name
        self.name = domain.name
        self.uuid = domain.uuid
        self.ip = ip
        self.total_cpu_usage = domain.total_cpu_usage
        self.memory_usage = domain.memory_usage
        self.disk_usage = domain.disk_usage
        self.status = domain.status
        self.timestamp = domain.timestamp
        self.operation_system = domain.operation_system       

    @staticmethod
    def messageFromList(msg, data_list):
        server_room = []
        computer_rack = []
        node_name = []
        name = []
        uuid = []
        ip = []
        total_cpu_usage = []
        memory_usage = []
        disk_usage = []
        status = []
        timestamp = []
        operation_system = []
        for data in data_list:
            server_room.append(data.server_room)
            computer_rack.append(data.computer_rack)
            node_name.append(data.node_name)
            name.append(data.name)
            uuid.append(data.uuid)
            ip.append(data.ip)
            total_cpu_usage.append(data.total_cpu_usage)
            memory_usage.append(data.memory_usage)
            disk_usage.append(data.disk_usage)
            status.append(data.status)
            timestamp.append(data.timestamp)
            operation_system.append(data.operation_system)
            
        setStringArray(msg, ParamKeyDefine.server_room, server_room)
        setStringArray(msg, ParamKeyDefine.computer_rack, computer_rack)
        setStringArray(msg, ParamKeyDefine.node_name, node_name)
        setStringArray(msg, ParamKeyDefine.name, name)
        setStringArray(msg, ParamKeyDefine.uuid, uuid)
        setStringArrayArray(msg, ParamKeyDefine.ip, ip)
        setFloatArray(msg, ParamKeyDefine.total_cpu_usage, total_cpu_usage)
        setFloatArray(msg, ParamKeyDefine.memory_usage, memory_usage)
        setFloatArray(msg, ParamKeyDefine.disk_usage, disk_usage)
        setUIntArray(msg, ParamKeyDefine.status, status)
        setStringArray(msg, ParamKeyDefine.timestamp, timestamp)
        setStringArray(msg, ParamKeyDefine.operation_system, operation_system)

    @staticmethod
    def listFromMessage(msg):
        data_list = []
        uuid = getStringArray(msg, ParamKeyDefine.uuid)
        data_count = len(uuid)
        if 0 == data_count:
            return data_list
        server_room = getStringArray(msg, ParamKeyDefine.server_room)
        computer_rack = getStringArray(msg, ParamKeyDefine.computer_rack)
        node_name = getStringArray(msg, ParamKeyDefine.node_name)
        name = getStringArray(msg, ParamKeyDefine.name)
        ip = getStringArrayArray(msg, ParamKeyDefine.ip)
        total_cpu_usage = getFloatArray(msg, ParamKeyDefine.total_cpu_usage)
        memory_usage = getFloatArray(msg, ParamKeyDefine.memory_usage)
        disk_usage = getFloatArray(msg, ParamKeyDefine.disk_usage)
        status = getUIntArray(msg, ParamKeyDefine.status)
        timestamp = getStringArray(msg, ParamKeyDefine.timestamp)
        operation_system = getStringArray(msg, ParamKeyDefine.operation_system)
        for i in range(data_count):
            data = DomainData()
            data.server_room = server_room[i]
            data.computer_rack = computer_rack[i]
            data.node_name = node_name[i]
            data.name = name[i]
            data.uuid = uuid[i]
            data.ip = ip[i]
            data.total_cpu_usage = total_cpu_usage[i]
            data.memory_usage = memory_usage[i]
            data.disk_usage = disk_usage[i]
            data.status = status[i]
            data.timestamp = timestamp[i]
            data.operation_system = operation_system[i]
            data.fullname = "%s.%s.%s.%s"%(data.server_room, data.computer_rack,
                                           data.node_name, data.name)
            data_list.append(data)

        return data_list
