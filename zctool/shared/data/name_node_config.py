#!/usr/bin/python
from service.message_define import *
from data_node_config import *

class NameNodeConfig(object):    
    def __init__(self):
        self.name = ""
        self.ip = ""
        self.port = 0
        self.replication = 0
        self.data_nodes = []
        
    def toMessage(self, msg):
        setString(msg, ParamKeyDefine.name, self.name)
        setString(msg, ParamKeyDefine.ip, self.ip)
        setUInt(msg, ParamKeyDefine.port, self.port)
        setUInt(msg, ParamKeyDefine.replication, self.replication)
        node_name = []
        upload_port = []
        upload_address = []
        auto_start = []
        for node in self.data_nodes:
            node_name.append(node.name)
            upload_address.append(node.ip)
            upload_port.append(node.port)
            if node.auto_start:
                auto_start.append(1)
            else:
                auto_start.append(0)
        setStringArray(msg, ParamKeyDefine.node_name, node_name)
        setStringArray(msg, ParamKeyDefine.upload_port, upload_port)
        setUIntArray(msg, ParamKeyDefine.upload_address, upload_address)
        setUIntArray(msg, ParamKeyDefine.auto_start, auto_start)        

    def fromMessage(self, msg):
        self.name = getString(msg, ParamKeyDefine.name)
        self.ip = getString(msg, ParamKeyDefine.ip)
        self.port = getUInt(msg, ParamKeyDefine.port)
        self.replication = getUInt(msg, ParamKeyDefine.replication)
        node_name = getStringArray(msg, ParamKeyDefine.node_name)
        upload_port = getStringArray(msg, ParamKeyDefine.upload_port)
        upload_address = getUIntArray(msg, ParamKeyDefine.upload_address)
        auto_start = getUIntArray(msg, ParamKeyDefine.auto_start)
        self.data_nodes = []
        for i in range(len(node_name)):
            node = DataNodeConfig()
            node.name = node_name[i]
            node.ip = upload_port[i]
            node.port = upload_address[i]
            if 1 == auto_start[i]:
                node.auto_start = True
            else:
                node.auto_start = False

            self.data_nodes.append(node)
