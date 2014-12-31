#!/usr/bin/python
from service.message_define import *

class OperateSummary(object):
    def __init__(self):
        self.server_room = ""
        self.computer_rack = ""
        self.node_name = ""
        
        ##resource
        self.cpu_count = 0
        self.total_memory = 0
        self.available_memory = 0
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
        server_room = []
        computer_rack = []
        node_name = []
        cpu_count = []
        total_memory = []
        available_memory = []
        total_volume = []
        used_volume = []
        cpu_seconds = []
        rd_bytes = []
        wr_bytes = []
        rx_bytes = []
        tx_bytes = []
        for summary in data_list:
            server_room.append(summary.server_room)
            computer_rack.append(summary.computer_rack)
            node_name.append(summary.node_name)
            cpu_count.append(summary.cpu_count)
            total_memory.append(summary.total_memory)
            available_memory.append(summary.available_memory)
            total_volume.append(summary.total_volume)
            used_volume.append(summary.used_volume)
            cpu_seconds.append(summary.cpu_seconds)
            rd_bytes.append(summary.rd_bytes)
            wr_bytes.append(summary.wr_bytes)
            rx_bytes.append(summary.rx_bytes)
            tx_bytes.append(summary.tx_bytes)

        setStringArray(msg, ParamKeyDefine.server_room, server_room)
        setStringArray(msg, ParamKeyDefine.computer_rack, computer_rack)
        setStringArray(msg, ParamKeyDefine.node_name, node_name)

        setUIntArray(msg, ParamKeyDefine.cpu_count, cpu_count)
        setUIntArray(msg, ParamKeyDefine.total_memory, total_memory)
        setUIntArray(msg, ParamKeyDefine.available_memory, available_memory)
        setUIntArray(msg, ParamKeyDefine.total_volume, total_volume)
        setUIntArray(msg, ParamKeyDefine.used_volume, used_volume)

        setFloatArray(msg, ParamKeyDefine.cpu_seconds, cpu_seconds)
        setUIntArray(msg, ParamKeyDefine.read_bytes, rd_bytes)
        setUIntArray(msg, ParamKeyDefine.write_bytes, wr_bytes)
        setUIntArray(msg, ParamKeyDefine.received_bytes, rx_bytes)
        setUIntArray(msg, ParamKeyDefine.sent_bytes, tx_bytes)
        

    @staticmethod
    def unpackFromMessage(msg):
        server_room = getStringArray(msg, ParamKeyDefine.server_room)
        computer_rack = getStringArray(msg, ParamKeyDefine.computer_rack)
        node_name = getStringArray(msg, ParamKeyDefine.node_name)

        cpu_count = getUIntArray(msg, ParamKeyDefine.cpu_count)
        total_memory = getUIntArray(msg, ParamKeyDefine.total_memory)
        available_memory = getUIntArray(msg, ParamKeyDefine.available_memory)
        total_volume = getUIntArray(msg, ParamKeyDefine.total_volume)
        used_volume = getUIntArray(msg, ParamKeyDefine.used_volume)

        cpu_seconds = getFloatArray(msg, ParamKeyDefine.cpu_seconds)
        rd_bytes = getUIntArray(msg, ParamKeyDefine.read_bytes)
        wr_bytes = getUIntArray(msg, ParamKeyDefine.write_bytes)
        rx_bytes = getUIntArray(msg, ParamKeyDefine.received_bytes)
        tx_bytes = getUIntArray(msg, ParamKeyDefine.sent_bytes)

        result = []
        for i in range(len(node_name)):
            summary = OperateSummary()
            summary.server_room = server_room[i]
            summary.computer_rack = computer_rack[i]
            summary.node_name = node_name[i]

            summary.cpu_count = cpu_count[i]
            summary.total_memory = total_memory[i]
            summary.available_memory = available_memory[i]
            summary.total_volume = total_volume[i]
            summary.used_volume = used_volume[i]

            summary.cpu_seconds = cpu_seconds[i]
            summary.rd_bytes = rd_bytes[i]
            summary.wr_bytes = wr_bytes[i]
            summary.rx_bytes = rx_bytes[i]
            summary.tx_bytes = tx_bytes[i]
            result.append(summary)
            
        return result

            
