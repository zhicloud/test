#!/usr/bin/python
from service.message_define import *

class StorageDeviceConfig(object):
    mode_distributed = 1
    mode_local = 0
    encryption_none = 0
    encryption_rsa = 1
    raid_disable = 0

    def __init__(self):
        self.name = ""
        self.uuid = ""
##        self.serial = 0
##        self.unit = 0
        self.pool = ""
        self.replication = 0
        self.mode = 0
        self.size = 0
        self.allocate = False
        self.encryption = StorageDeviceConfig.encryption_none
        self.raid = StorageDeviceConfig.raid_disable
        self.page_size = 0
        self.block_size = 0
        
    def toMessage(self, msg):
        msg.setString(ParamKeyDefine.name, self.name)
        msg.setString(ParamKeyDefine.uuid, self.uuid)
##        msg.setUInt(ParamKeyDefine.serial, self.serial)
##        msg.setUInt(ParamKeyDefine.unit, self.unit)
        msg.setString(ParamKeyDefine.pool, self.pool)
        msg.setUInt(ParamKeyDefine.replication, self.replication)
        msg.setUInt(ParamKeyDefine.mode, self.mode)
        msg.setUInt(ParamKeyDefine.size, self.size)
        msg.setBool(ParamKeyDefine.allocate, self.allocate)
        msg.setUInt(ParamKeyDefine.encryption, self.encryption)
        msg.setUInt(ParamKeyDefine.raid, self.raid)
        msg.setUInt(ParamKeyDefine.page, self.page_size)        
        msg.setUInt(ParamKeyDefine.block, self.block_size)        

    def fromMessage(self, msg):
        self.name = msg.getString(ParamKeyDefine.name)
        self.uuid = msg.getString(ParamKeyDefine.uuid)
##        self.serial = msg.getUInt(ParamKeyDefine.serial)
##        self.unit = msg.getUInt(ParamKeyDefine.unit)
        self.pool = msg.getString(ParamKeyDefine.pool)
        self.replication = msg.getUInt(ParamKeyDefine.replication)
        self.mode = msg.getUInt(ParamKeyDefine.mode)
        self.size = msg.getUInt(ParamKeyDefine.size)
        self.allocate = msg.getBool(ParamKeyDefine.allocate)
        self.encryption = msg.getUInt(ParamKeyDefine.encryption)
        self.raid = msg.getUInt(ParamKeyDefine.raid)
        self.page_size = msg.getUInt(ParamKeyDefine.page)
        self.block_size = msg.getUInt(ParamKeyDefine.block)
        
