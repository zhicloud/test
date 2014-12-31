#!/usr/bin/python
from service.message_define import *

class ServerRackConfig(object):
    def __init__(self, uuid = "", name = "", server_room = ""):
        self.server_room = server_room
        self.uuid = uuid
        self.name = name

    def toMessage(self, msg):
        setString(msg, ParamKeyDefine.uuid, self.uuid)
        setString(msg, ParamKeyDefine.room, self.server_room)
        setString(msg, ParamKeyDefine.name, self.name)

    def fromMessage(self, msg):
        self.uuid = getString(msg, ParamKeyDefine.uuid)
        self.server_room = getString(msg, ParamKeyDefine.room)
        self.name = getString(msg, ParamKeyDefine.name)
        
    @staticmethod
    def packToMessage(msg, data_list):
        uuid = []
        server_room = []
        name = []
        for data in data_list:
            uuid.append(data.uuid)
            server_room.append(data.server_room)
            name.append(data.name)

        setStringArray(msg, ParamKeyDefine.uuid, uuid)
        setStringArray(msg, ParamKeyDefine.room, server_room)
        setStringArray(msg, ParamKeyDefine.name, name)

    @staticmethod
    def unpackFromMessage(msg):
        data_list = []
        uuid = getStringArray(msg, ParamKeyDefine.uuid)
        server_room = getStringArray(msg, ParamKeyDefine.room)
        name = getStringArray(msg, ParamKeyDefine.name)
        for i in range(len(name)):
            data_list.append(ServerRackConfig(
                uuid[i], name[i], server_room[i]))
            
        return data_list
        
