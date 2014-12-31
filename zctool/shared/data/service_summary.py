#!/usr/bin/python
from service.message_define import *

class ServiceSummary(object):
    def __init__(self):
        self.uuid = ""
        self.name = ""
        
        ##resource
        self.cpu_count = 0
        self.total_volume = 0
        self.used_volume = 0

        ##usage
        self.cpu_seconds = 0.0
        self.rd_bytes = 0
        self.wr_bytes = 0
        self.rx_bytes = 0
        self.tx_bytes = 0

    @staticmethod
    def packToMessage(msg, data_list):
        uuid = []
        name = []
        
        cpu_count = []
        total_volume = []
        used_volume = []
        cpu_seconds = []
        rd_bytes = []
        wr_bytes = []
        rx_bytes = []
        tx_bytes = []
        for summary in data_list:
            uuid.append(summary.uuid)
            name.append(summary.name)
            cpu_count.append(summary.cpu_count)
            total_volume.append(summary.total_volume)
            used_volume.append(summary.used_volume)
            cpu_seconds.append(summary.cpu_seconds)
            rd_bytes.append(summary.rd_bytes)
            wr_bytes.append(summary.wr_bytes)
            rx_bytes.append(summary.rx_bytes)
            tx_bytes.append(summary.tx_bytes)

        setStringArray(msg, ParamKeyDefine.uuid, uuid)
        setStringArray(msg, ParamKeyDefine.name, name)

        setUIntArray(msg, ParamKeyDefine.cpu_count, cpu_count)
        setUIntArray(msg, ParamKeyDefine.total_volume, total_volume)
        setUIntArray(msg, ParamKeyDefine.used_volume, used_volume)

        setFloatArray(msg, ParamKeyDefine.cpu_seconds, cpu_seconds)
        setUIntArray(msg, ParamKeyDefine.read_bytes, rd_bytes)
        setUIntArray(msg, ParamKeyDefine.write_bytes, wr_bytes)
        setUIntArray(msg, ParamKeyDefine.received_bytes, rx_bytes)
        setUIntArray(msg, ParamKeyDefine.sent_bytes, tx_bytes)
        

    @staticmethod
    def unpackFromMessage(msg):
        uuid = getStringArray(msg, ParamKeyDefine.uuid)
        name = getStringArray(msg, ParamKeyDefine.name)

        cpu_count = getUIntArray(msg, ParamKeyDefine.cpu_count)
        total_volume = getUIntArray(msg, ParamKeyDefine.total_volume)
        used_volume = getUIntArray(msg, ParamKeyDefine.used_volume)

        cpu_seconds = getFloatArray(msg, ParamKeyDefine.cpu_seconds)
        rd_bytes = getUIntArray(msg, ParamKeyDefine.read_bytes)
        wr_bytes = getUIntArray(msg, ParamKeyDefine.write_bytes)
        rx_bytes = getUIntArray(msg, ParamKeyDefine.received_bytes)
        tx_bytes = getUIntArray(msg, ParamKeyDefine.sent_bytes)

        result = []
        for i in range(len(name)):
            summary = ServiceSummary()
            summary.uuid = uuid[i]
            summary.name = name[i]

            summary.cpu_count = cpu_count[i]
            summary.total_volume = total_volume[i]
            summary.used_volume = used_volume[i]

            summary.cpu_seconds = cpu_seconds[i]
            summary.rd_bytes = rd_bytes[i]
            summary.wr_bytes = wr_bytes[i]
            summary.rx_bytes = rx_bytes[i]
            summary.tx_bytes = tx_bytes[i]
            result.append(summary)
            
        return result

            
