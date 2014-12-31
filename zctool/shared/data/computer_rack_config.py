#!/usr/bin/python
from service.message_define import *

class ComputerRackConfig(object):
    uuid = ""
    domain = ""
    server_room = ""
    name = ""
    display_name = ""
    description = ""

    def __init__(self, domain = "", server_room = "", name = "",
                 display_name = "", uuid = "", description = ""):
        self.domain = domain
        self.server_room = server_room
        self.uuid = uuid
        self.name = name
        self.display_name = display_name
        self.description = description

    def toMessage(self, msg):
        setString(msg, ParamKeyDefine.uuid, self.uuid)
        setString(msg, ParamKeyDefine.domain, self.domain)
        setString(msg, ParamKeyDefine.server_room, self.server_room)
        setString(msg, ParamKeyDefine.computer_rack, self.name)
        setString(msg, ParamKeyDefine.display, self.display_name)
        setString(msg, ParamKeyDefine.description, self.description)

    def fromMessage(self, msg):
        self.uuid = getString(msg, ParamKeyDefine.uuid)
        self.domain = getString(msg, ParamKeyDefine.domain)
        self.server_room = getString(msg, ParamKeyDefine.server_room)
        self.name = getString(msg, ParamKeyDefine.computer_rack)
        self.display_name = getString(msg, ParamKeyDefine.display)
        self.description = getString(msg, ParamKeyDefine.description)
        
    @staticmethod
    def packToMessage(msg, data_list):
        uuid = []
        domain = []
        server_room = []
        name = []
        display = []
        description = []
        for data in data_list:
            uuid.append(data.uuid)
            domain.append(data.domain)
            server_room.append(data.server_room)
            name.append(data.name)
            display.append(data.display_name)
            description.append(data.description)

        setStringArray(msg, ParamKeyDefine.uuid, uuid)
        setStringArray(msg, ParamKeyDefine.domain, domain)
        setStringArray(msg, ParamKeyDefine.server_room, server_room)
        setStringArray(msg, ParamKeyDefine.computer_rack, name)
        setStringArray(msg, ParamKeyDefine.display, display)
        setStringArray(msg, ParamKeyDefine.description, description)

    @staticmethod
    def unpackFromMessage(msg):
        data_list = []
        uuid = getStringArray(msg, ParamKeyDefine.uuid)
        domain = getStringArray(msg, ParamKeyDefine.domain)
        server_room = getStringArray(msg, ParamKeyDefine.server_room)
        name = getStringArray(msg, ParamKeyDefine.computer_rack)
        display = getStringArray(msg, ParamKeyDefine.display)
        description = getStringArray(msg, ParamKeyDefine.description)
        for i in range(len(name)):
            data_list.append(ComputerRackConfig(
                domain[i], server_room[i], name[i], display[i],
                uuid[i], description[i]))
        return data_list
        
