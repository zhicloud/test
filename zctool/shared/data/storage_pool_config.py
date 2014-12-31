#!/usr/bin/python
from service.message_define import *

class StoragePoolConfig(object):
    pool_type_fast = 2
    pool_type_normal = 1
    pool_type_slow = 0
    page_size = 4*1024##default: 4 KiB

    def __init__(self):
        self.name = ""
        self.uuid = ""
        self.type = StoragePoolConfig.pool_type_slow
        self.page_size = StoragePoolConfig.page_size
        ##list of data node name
        self.nodes = []
        
    def toMessage(self, msg):
        msg.setString(ParamKeyDefine.name, self.name)
        msg.setString(ParamKeyDefine.uuid, self.uuid)
        msg.setUInt(ParamKeyDefine.type, self.type)
        msg.setUInt(ParamKeyDefine.size, self.page_size)
        msg.setStringArray(ParamKeyDefine.node_name, self.nodes)

    def fromMessage(self, msg):
        self.name = msg.getString(ParamKeyDefine.name)
        self.uuid = msg.getString(ParamKeyDefine.uuid)
        self.type = msg.getUInt(ParamKeyDefine.type)
        self.page_size = msg.getUInt(ParamKeyDefine.size)
        nodes = msg.getStringArray(ParamKeyDefine.node_name)
        if nodes:
            self.nodes = nodes
        
