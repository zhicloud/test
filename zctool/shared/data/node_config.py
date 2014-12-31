#!/usr/bin/python
from service.message_define import *

class NodeConfig(object):
    domain = ""
    server_room = ""
    computer_rack = ""
    name = ""
    actived = False

    def __init__(self, domain = "", server_room = "", computer_rack = "",
                 name = "", actived = False):
        self.domain = domain
        self.server_room = server_room
        self.computer_rack = computer_rack
        self.name = name
        self.actived = actived
        
    def toMessage(self, msg):
        setString(msg, ParamKeyDefine.domain, self.domain)
        setString(msg, ParamKeyDefine.server_room, self.server_room)
        setString(msg, ParamKeyDefine.computer_rack, self.computer_rack)
        setString(msg, ParamKeyDefine.node_name, self.name)
        setBool(msg, ParamKeyDefine.actived, self.actived)

    def fromMessage(self, msg):
        self.domain = getString(msg, ParamKeyDefine.domain)
        self.server_room = getString(msg, ParamKeyDefine.server_room)
        self.computer_rack = getString(msg, ParamKeyDefine.computer_rack)
        self.name = getString(msg, ParamKeyDefine.node_name)
        self.actived = getBool(msg, ParamKeyDefine.actived)
        
    @staticmethod
    def packToMessage(msg, data_list):
        domain = []
        server_room = []
        computer_rack = []
        name = []
        actived = []
        for data in data_list:
            domain.append(data.domain)
            server_room.append(data.server_room)
            computer_rack.append(data.computer_rack)
            name.append(data.name)
            if data.actived:
                actived.append(1)
            else:
                actived.append(0)

        setStringArray(msg, ParamKeyDefine.domain, domain)
        setStringArray(msg, ParamKeyDefine.server_room, server_room)
        setStringArray(msg, ParamKeyDefine.computer_rack, computer_rack)
        setStringArray(msg, ParamKeyDefine.node_name, name)
        setUIntArray(msg, ParamKeyDefine.actived, actived)        

    @staticmethod
    def unpackFromMessage(msg):
        data_list = []
        domain = getStringArray(msg, ParamKeyDefine.domain)
        server_room = getStringArray(msg, ParamKeyDefine.server_room)
        computer_rack = getStringArray(msg, ParamKeyDefine.computer_rack)
        name = getStringArray(msg, ParamKeyDefine.node_name)
        actived = getUIntArray(msg, ParamKeyDefine.actived)
        for i in range(len(name)):
            data_list.append(NodeConfig(
                domain[i], server_room[i], computer_rack[i], name[i],
                (1 == actived[i])))
        return data_list
