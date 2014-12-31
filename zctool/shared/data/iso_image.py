#!/usr/bin/python
from service.message_define import *

class ISOImage(object):
    
    def __init__(self):
        self.name = ""
        self.uuid = ""
        self.catalog = 0
        self.operation_system = ""
        self.filename = ""
        self.path = ""
        self.ip = ""
        self.port = 0
        self.disk_volume = 0
        self.description = ""
        self.timestamp = ""
        
    def toMessage(self, msg):
        setString(msg, ParamKeyDefine.name, self.name)
        setString(msg, ParamKeyDefine.uuid, self.uuid)
        setUInt(msg, ParamKeyDefine.catalog, self.catalog)
        setString(msg, ParamKeyDefine.operation_system, self.operation_system)
        setString(msg, ParamKeyDefine.filename, self.filename)
        setString(msg, ParamKeyDefine.path, self.path)
        setString(msg, ParamKeyDefine.ip, self.ip)
        setUInt(msg, ParamKeyDefine.port, self.port)
        setUInt(msg, ParamKeyDefine.disk_volume, self.disk_volume)
        setString(msg, ParamKeyDefine.description, self.description)
        setString(msg, ParamKeyDefine.timestamp, self.timestamp)

    def fromMessage(self, msg):
        self.name = getString(msg, ParamKeyDefine.name)
        self.uuid = getString(msg, ParamKeyDefine.uuid)
        self.catalog = getUInt(msg, ParamKeyDefine.catalog)
        self.operation_system = getString(msg, ParamKeyDefine.operation_system)
        self.filename = getString(msg, ParamKeyDefine.filename)
        self.path = getString(msg, ParamKeyDefine.path)
        self.ip = getString(msg, ParamKeyDefine.ip)
        self.port = getUInt(msg, ParamKeyDefine.port)
        self.disk_volume = getUInt(msg, ParamKeyDefine.disk_volume)
        self.description = getString(msg, ParamKeyDefine.description)
        self.timestamp = getString(msg, ParamKeyDefine.timestamp)
        
    @staticmethod
    def packToMessage(msg, data_list):
        name = []
        uuid = []
        catalog = []
        operation_system = []
        filename = []
        path = []
        ip = []
        port = []
        disk_volume = []
        description = []
        timestamp = []
        for data in data_list:
            name.append(data.name)
            uuid.append(data.uuid)
            catalog.append(data.catalog)
            operation_system.append(data.operation_system)
            filename.append(data.filename)
            path.append(data.path)
            ip.append(data.ip)
            port.append(data.port)
            disk_volume.append(data.disk_volume)
            description.append(data.description)
            timestamp.append(data.timestamp)

        setStringArray(msg, ParamKeyDefine.name, name)
        setStringArray(msg, ParamKeyDefine.uuid, uuid)
        setUIntArray(msg, ParamKeyDefine.catalog, catalog)
        setStringArray(msg, ParamKeyDefine.operation_system, operation_system)
        setStringArray(msg, ParamKeyDefine.filename, filename)
        setStringArray(msg, ParamKeyDefine.path, path)
        setStringArray(msg, ParamKeyDefine.ip, ip)
        setUIntArray(msg, ParamKeyDefine.port, port)
        setUIntArray(msg, ParamKeyDefine.disk_volume, disk_volume)
        setStringArray(msg, ParamKeyDefine.description, description)
        setStringArray(msg, ParamKeyDefine.timestamp, timestamp)

    @staticmethod
    def unpackFromMessage(msg):
        data_list = []
        name = getStringArray(msg, ParamKeyDefine.name)
        uuid = getStringArray(msg, ParamKeyDefine.uuid)
        catalog = getUIntArray(msg, ParamKeyDefine.catalog)
        operation_system = getStringArray(msg, ParamKeyDefine.operation_system)
        filename = getStringArray(msg, ParamKeyDefine.filename)
        path = getStringArray(msg, ParamKeyDefine.path)
        ip = getStringArray(msg, ParamKeyDefine.ip)
        port = getUIntArray(msg, ParamKeyDefine.port)
        disk_volume = getUIntArray(msg, ParamKeyDefine.disk_volume)
        description = getStringArray(msg, ParamKeyDefine.description)
        timestamp = getStringArray(msg, ParamKeyDefine.timestamp)
        for i in range(len(name)):
            data = ISOImage()
            data.name = name[i]
            data.uuid = uuid[i]
            data.catalog = catalog[i]
            data.operation_system = operation_system[i]
            data.filename = filename[i]
            data.path = path[i]
            data.ip = ip[i]
            data.port = port[i]
            data.disk_volume = disk_volume[i]
            data.description = description[i]
            data.timestamp = timestamp[i]
            data_list.append(data)
            
        return data_list
        
