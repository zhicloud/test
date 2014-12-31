#!/usr/bin/python
from service.message_define import *
from storage_pool_config import *

class DataNodeStatus(object):
    def __init__(self):
        self.name = ""
        self.uuid = ""
        self.type = StoragePoolConfig.pool_type_slow
        self.serial = 0
        self.available_volume = 0
        self.total_volume = 0
        self.enable = False
        self.timestamp = ""
