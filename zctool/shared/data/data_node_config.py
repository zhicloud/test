#!/usr/bin/python
from service.message_define import *

class DataNodeConfig(object):    
    def __init__(self):
        self.name = ""
        self.ip = ""
        self.port = 0
        self.auto_start = False
        
    def toMessage(self, msg):
        setString(msg, ParamKeyDefine.name, self.name)
        setString(msg, ParamKeyDefine.ip, self.ip)
        setUInt(msg, ParamKeyDefine.port, self.port)
        setBool(msg, ParamKeyDefine.auto_start, self.auto_start)        

    def fromMessage(self, msg):
        self.name = getString(msg, ParamKeyDefine.name)
        self.ip = getString(msg, ParamKeyDefine.ip)
        self.port = getUInt(msg, ParamKeyDefine.port)
        self.auto_start = getBool(msg, ParamKeyDefine.auto_start)
        
        
