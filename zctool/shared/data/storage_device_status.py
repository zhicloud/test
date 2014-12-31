#!/usr/bin/python
from service.message_define import *
from storage_device_config import * 

class StorageDeviceStatus(StorageDeviceConfig):

    def __init__(self):
        StorageDeviceConfig.__init__(self)
        self.enable = True
        self.total_volume = 0
        self.available_volume = 0
        
    @staticmethod
    def packToMessage(msg, data_list):
        name = []
        uuid = []
##        serial = []
##        unit = []
        pool = []
        replication = []
        mode = []
        size = []
        allocate = []
        encryption = []
        raid = []
        page_size = []
        block_size = []
        available_volume = []
        total_volume = []
        status = []
        for data in data_list:
            name.append(data.name)
            uuid.append(data.uuid)
##            serial.append(data.serial)
##            unit.append(data.unit)
            pool.append(data.pool)
            replication.append(data.replication)
            mode.append(data.mode)
            size.append(data.size)
            if data.allocate:
                allocate.append(1)
            else:
                allocate.append(0)
                
            encryption.append(data.encryption)
            raid.append(data.raid)
            page_size.append(data.page_size)
            block_size.append(data.block_size)
            available_volume.append(data.available_volume)

            total_volume.append(data.total_volume)
            if data.enable:
                status.append(1)
            else:
                status.append(0)
            
        msg.setStringArray(ParamKeyDefine.name, name)
        msg.setStringArray(ParamKeyDefine.uuid, uuid)
##        msg.setUIntArray(ParamKeyDefine.serial, serial)
##        msg.setUIntArray(ParamKeyDefine.unit, unit)
        msg.setStringArray(ParamKeyDefine.pool, pool)
        msg.setUIntArray(ParamKeyDefine.replication, replication)
        msg.setUIntArray(ParamKeyDefine.mode, mode)
        msg.setUIntArray(ParamKeyDefine.size, size)
        msg.setUIntArray(ParamKeyDefine.allocate, allocate)
        msg.setUIntArray(ParamKeyDefine.encryption, encryption)
        msg.setUIntArray(ParamKeyDefine.raid, raid)
        msg.setUIntArray(ParamKeyDefine.page, page_size)
        msg.setUIntArray(ParamKeyDefine.block, block_size)
        msg.setUIntArray(ParamKeyDefine.available, available_volume)
        msg.setUIntArray(ParamKeyDefine.total_volume, total_volume)
        msg.setUIntArray(ParamKeyDefine.status, status)

        
       
    @staticmethod
    def unpackFromMessage(msg):
        name = msg.getStringArray(ParamKeyDefine.name)
        uuid = msg.getStringArray(ParamKeyDefine.uuid)
##        serial = msg.getUIntArray(ParamKeyDefine.serial)
##        unit = msg.getUIntArray(ParamKeyDefine.unit)
        pool = msg.getStringArray(ParamKeyDefine.pool)
        replication = msg.getUIntArray(ParamKeyDefine.replication)
        mode = msg.getUIntArray(ParamKeyDefine.mode)
        size = msg.getUIntArray(ParamKeyDefine.size)
        allocate = msg.getUIntArray(ParamKeyDefine.allocate)
        encryption = msg.getUIntArray(ParamKeyDefine.encryption)
        raid = msg.getUIntArray(ParamKeyDefine.raid)
        page_size = msg.getUIntArray(ParamKeyDefine.page)
        block_size = msg.getUIntArray(ParamKeyDefine.block)
        available_volume = msg.getUIntArray(ParamKeyDefine.available)
        total_volume = msg.getUIntArray(ParamKeyDefine.total_volume)
        status = msg.getUIntArray(ParamKeyDefine.status)

        result = []
        for i in range(len(name)):
            device = StorageDeviceStatus()
            device.name = name[i]
            device.uuid = uuid[i]
##            device.serial = serial[i]
##            device.unit = unit[i]
            device.pool = pool[i]
            device.replication = replication[i]
            device.mode = mode[i]
            device.size = size[i]
                
            if 1 == allocate[i]:
                device.allocate = True
            else:
                device.allocate = False
                
            device.encryption = encryption[i]
            device.raid = raid[i]
            device.page_size = page_size[i]
            device.block_size = block_size[i]
                
            device.available_volume = available_volume[i]
            device.total_volume = total_volume[i]
            if 1 == status[i]:
                device.enable = True
            else:
                device.enable = False
                
            result.append(device)
            
        return result
