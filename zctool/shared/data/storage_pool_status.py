#!/usr/bin/python
from service.message_define import *
from storage_pool_config import *

class StoragePoolStatus(object):
    def __init__(self):
        self.name = ""
        self.uuid = ""
        self.type = StoragePoolConfig.pool_type_slow
        self.page_size = StoragePoolConfig.page_size
        ##list of data node name
        self.nodes = []
        self.available_volume = 0
        self.total_volume = 0
        self.enable = True

    @staticmethod
    def packToMessage(msg, data_list):
        name = []
        uuid = []
        pool_type = []
        page_size = []
        nodes = []
        available = []
        total_volume = []
        status = []
        for data in data_list:
            name.append(data.name)
            uuid.append(data.uuid)
            pool_type.append(data.type)
            page_size.append(data.page_size)
            nodes.append(data.nodes)
            available.append(data.available_volume)
            total_volume.append(data.total_volume)
            if data.enable:
                status.append(1)
            else:
                status.append(0)

        msg.setStringArray(ParamKeyDefine.name, name)
        msg.setStringArray(ParamKeyDefine.uuid, uuid)
        msg.setUIntArray(ParamKeyDefine.type, pool_type)
        msg.setUIntArray(ParamKeyDefine.size, page_size)

        msg.setStringArrayArray(ParamKeyDefine.node_name, nodes)
        msg.setUIntArray(ParamKeyDefine.available, available)
        msg.setUIntArray(ParamKeyDefine.total_volume, total_volume)
        msg.setUIntArray(ParamKeyDefine.status, status)

    @staticmethod
    def unpackFromMessage(msg):
        name = msg.getStringArray(ParamKeyDefine.name)
        uuid = msg.getStringArray(ParamKeyDefine.uuid)
        pool_type = msg.getUIntArray(ParamKeyDefine.type)
        page_size = msg.getUIntArray(ParamKeyDefine.size)

        nodes = msg.getStringArrayArray(ParamKeyDefine.node_name)
        available_volume = msg.getUIntArray(ParamKeyDefine.available)
        total_volume = msg.getUIntArray(ParamKeyDefine.total_volume)
        status = msg.getUIntArray(ParamKeyDefine.status)

        result = []
        for i in range(len(name)):
            pool = StoragePoolStatus()
            pool.name = name[i]
            pool.uuid = uuid[i]
            pool.type = pool_type[i]
            pool.page_size = page_size[i]
            pool.nodes = nodes[i]
            pool.available_volume = available_volume[i]
            pool.total_volume = total_volume[i]
            if 1 == status[i]:
                pool.enable = True
            else:
                pool.enable = False
                
            result.append(pool)
            
        return result
