#!/usr/bin/python
from service.message_define import *

class DiskImage(object):
    name = ""
    catalog = 0
    operation_system = ""
    filename = ""
    path = ""
    network_address = ""
    description = ""
    def __init__(self, name = "", catalog = 0, operation_system = "",
                 filename = "", path = "", network_address = "", description = ""):
        self.name = name
        self.catalog = catalog
        self.operation_system = operation_system
        self.filename = filename
        self.path = path
        self.network_address = network_address
        self.description = description
        
    def toMessage(self, msg):
        setString(msg, ParamKeyDefine.name, self.name)
        setUInt(msg, ParamKeyDefine.catalog, self.catalog)
        setString(msg, ParamKeyDefine.operation_system, self.operation_system)
        setString(msg, ParamKeyDefine.filename, self.filename)
        setString(msg, ParamKeyDefine.path, self.path)
        setString(msg, ParamKeyDefine.network_address, self.network_address)
        setString(msg, ParamKeyDefine.description, self.description)

    def fromMessage(self, msg):
        self.name = getString(msg, ParamKeyDefine.name)
        self.catalog = getUInt(msg, ParamKeyDefine.catalog)
        self.operation_system = getString(msg, ParamKeyDefine.operation_system)
        self.filename = getString(msg, ParamKeyDefine.filename)
        self.path = getString(msg, ParamKeyDefine.path)
        self.network_address = getString(msg, ParamKeyDefine.network_address)
        self.description = getString(msg, ParamKeyDefine.description)
        
    @staticmethod
    def packToMessage(msg, data_list):
        name = []
        catalog = []
        operation_system = []
        filename = []
        path = []
        network_address = []
        description = []
        for data in data_list:
            name.append(data.name)
            catalog.append(data.catalog)
            operation_system.append(data.operation_system)
            filename.append(data.filename)
            path.append(data.path)
            network_address.append(data.network_address)
            description.append(data.description)

        setStringArray(msg, ParamKeyDefine.name, name)
        setUIntArray(msg, ParamKeyDefine.catalog, catalog)
        setStringArray(msg, ParamKeyDefine.operation_system, operation_system)
        setStringArray(msg, ParamKeyDefine.filename, filename)
        setStringArray(msg, ParamKeyDefine.path, path)
        setStringArray(msg, ParamKeyDefine.network_address, network_address)
        setStringArray(msg, ParamKeyDefine.description, description)

    @staticmethod
    def unpackFromMessage(msg):
        data_list = []
        name = getStringArray(msg, ParamKeyDefine.name)
        catalog = getUIntArray(msg, ParamKeyDefine.catalog)
        operation_system = getStringArray(msg, ParamKeyDefine.operation_system)
        filename = getStringArray(msg, ParamKeyDefine.filename)
        path = getStringArray(msg, ParamKeyDefine.path)
        network_address = getStringArray(msg, ParamKeyDefine.network_address)
        description = getStringArray(msg, ParamKeyDefine.description)
        for i in range(len(name)):
            data_list.append(DiskImage(
                name[i], catalog[i], operation_system[i], filename[i],
                path[i], network_address[i], description[i]))
        return data_list
        
