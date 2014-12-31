#!/usr/bin/python
from service.message_define import *

class StorageConfig(object):    
    def __init__(self):
        self.name = ""
        self.access_ip = ""
        self.access_port = 0
        self.upload_ip = ""
        self.upload_port = 0
        
    def toMessage(self, msg):
        setString(msg, ParamKeyDefine.node_name, self.name)
        setString(msg, ParamKeyDefine.ip, self.access_ip)
        setUInt(msg, ParamKeyDefine.port, self.access_port)
        setString(msg, ParamKeyDefine.upload_address, self.upload_ip)
        setUInt(msg, ParamKeyDefine.upload_port, self.upload_port)
        

    def fromMessage(self, msg):
        self.name = getString(msg, ParamKeyDefine.node_name)
        self.access_ip = getString(msg, ParamKeyDefine.ip)
        self.access_port = getUInt(msg, ParamKeyDefine.port)
        self.upload_ip = getString(msg, ParamKeyDefine.upload_address)
        self.upload_port = getUInt(msg, ParamKeyDefine.upload_port)
        
        
