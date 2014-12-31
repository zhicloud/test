#!/usr/bin/python
from service.message_define import *

class ServerRoomConfig(object):
    
    def __init__(self, domain = "", name = "", display_name = "", uuid = "", description = ""):
        self.domain = domain
        self.uuid = uuid
        self.name = name
        self.display_name = display_name
        self.description = description
        
    def toMessage(self, msg):
        setString(msg, ParamKeyDefine.uuid, self.uuid)
        setString(msg, ParamKeyDefine.domain, self.domain)
        setString(msg, ParamKeyDefine.name, self.name)
        setString(msg, ParamKeyDefine.display, self.display_name)
        setString(msg, ParamKeyDefine.description, self.description)

    def fromMessage(self, msg):
        self.uuid = getString(msg, ParamKeyDefine.uuid)
        self.domain = getString(msg, ParamKeyDefine.domain)
        self.name = getString(msg, ParamKeyDefine.name)
        self.display_name = getString(msg, ParamKeyDefine.display)
        self.description = getString(msg, ParamKeyDefine.description)
        
    @staticmethod
    def packToMessage(msg, data_list):
        uuid = []
        domain = []
        name = []
        display = []
        description = []
        for data in data_list:
            uuid.append(data.uuid)
            domain.append(data.domain)
            name.append(data.name)
            display.append(data.display_name)
            description.append(data.description)

        setStringArray(msg, ParamKeyDefine.uuid, uuid)
        setStringArray(msg, ParamKeyDefine.domain, domain)
        setStringArray(msg, ParamKeyDefine.name, name)
        setStringArray(msg, ParamKeyDefine.display, display)
        setStringArray(msg, ParamKeyDefine.description, description)

    @staticmethod
    def unpackFromMessage(msg):
        data_list = []
        uuid = getStringArray(msg, ParamKeyDefine.uuid)
        domain = getStringArray(msg, ParamKeyDefine.domain)
        name = getStringArray(msg, ParamKeyDefine.name)
        display = getStringArray(msg, ParamKeyDefine.display)
        description = getStringArray(msg, ParamKeyDefine.description)
        for i in range(len(name)):
            data_list.append(ServerRoomConfig(
                domain[i], name[i], display[i],
                uuid[i], description[i]))
        return data_list
        
