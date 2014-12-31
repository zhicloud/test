#!/usr/bin/python
from service.message_define import *
from service_data import *

class ServiceDetail(object):
    def __init__(self):
        self.uuid = ""
        self.name = ""

        ##resource
        self.cpu_count = 0
        self.total_volume = 0
        self.used_volume = 0

        self.summary_data = None
        self.average_data = None
        self.top_data = None
        self.bottom_data = None

        self.data_list = []

    def toMessage(self, msg):
        data_list = list(self.data_list)
        if self.summary_data:
            data_list.append(self.summary_data)
        else:
            data_list.append(OperateData())

        if self.average_data:
            data_list.append(self.average_data)
        else:
            data_list.append(OperateData())

        if self.top_data:
            data_list.append(self.top_data)
        else:
            data_list.append(OperateData())

        if self.bottom_data:
            data_list.append(self.bottom_data)
        else:
            data_list.append(OperateData())

        timestamp = []
        status = []
        total_cpu_usage = []
        disk_usage = []
        
        cpu_seconds = []
        rd_req = []
        rd_bytes = []
        wr_req = []
        wr_bytes = []
        io_error = []
        rd_speed = []
        wr_speed = []

        rx_bytes = []
        rx_packets = []
        rx_errs = []
        rx_drop = []
        tx_bytes = []
        tx_packets = []
        tx_errs = []
        tx_drop = []
        rx_speed = []
        tx_speed = []
        for data in data_list:
            timestamp.append(data.timestamp)
            status.append(data.status)
            
            total_cpu_usage.append(data.total_cpu_usage)
            disk_usage.append(data.disk_usage)
            
            cpu_seconds.append(data.cpu_seconds)

            rd_req.append(data.rd_req)
            rd_bytes.append(data.rd_bytes)
            wr_req.append(data.wr_req)
            wr_bytes.append(data.wr_bytes)
            io_error.append(data.io_error)
            rd_speed.append(data.rd_speed)
            wr_speed.append(data.wr_speed)

            rx_bytes.append(data.rx_bytes)
            rx_packets.append(data.rx_packets)
            rx_errs.append(data.rx_errs)
            rx_drop.append(data.rx_drop)
            tx_bytes.append(data.tx_bytes)
            tx_packets.append(data.tx_packets)
            tx_errs.append(data.tx_errs)
            tx_drop.append(data.tx_drop)
            rx_speed.append(data.rx_speed)
            tx_speed.append(data.tx_speed)

        setString(msg, ParamKeyDefine.uuid, self.uuid)
        setString(msg, ParamKeyDefine.name, self.name)

        setUInt(msg, ParamKeyDefine.cpu_count, self.cpu_count)
        setUInt(msg, ParamKeyDefine.total_volume, self.total_volume)
        setUInt(msg, ParamKeyDefine.used_volume, self.used_volume)

        setStringArray(msg, ParamKeyDefine.timestamp, timestamp)
        setUIntArray(msg, ParamKeyDefine.status, status)
        setFloatArray(msg, ParamKeyDefine.total_cpu_usage, total_cpu_usage)
        setFloatArray(msg, ParamKeyDefine.disk_usage, disk_usage)
        setFloatArray(msg, ParamKeyDefine.cpu_seconds, cpu_seconds)

        setUIntArray(msg, ParamKeyDefine.read_request, rd_req)
        setUIntArray(msg, ParamKeyDefine.read_bytes, rd_bytes)
        setUIntArray(msg, ParamKeyDefine.write_request, wr_req)
        setUIntArray(msg, ParamKeyDefine.write_bytes, wr_bytes)
        setUIntArray(msg, ParamKeyDefine.io_error, io_error)
        setUIntArray(msg, ParamKeyDefine.read_speed, rd_speed)
        setUIntArray(msg, ParamKeyDefine.write_speed, wr_speed)

        setUIntArray(msg, ParamKeyDefine.received_bytes, rx_bytes)
        setUIntArray(msg, ParamKeyDefine.recevied_packets, rx_packets)
        setUIntArray(msg, ParamKeyDefine.recevied_errors, rx_errs)
        setUIntArray(msg, ParamKeyDefine.received_drop, rx_drop)
        setUIntArray(msg, ParamKeyDefine.sent_bytes, tx_bytes)
        setUIntArray(msg, ParamKeyDefine.sent_packets, tx_packets)
        setUIntArray(msg, ParamKeyDefine.sent_errors, tx_errs)
        setUIntArray(msg, ParamKeyDefine.sent_drop, tx_drop)
        setUIntArray(msg, ParamKeyDefine.received_speed, rx_speed)
        setUIntArray(msg, ParamKeyDefine.sent_speed, tx_speed)                

    def fromMessage(self, msg):
        self.uuid = getString(msg, ParamKeyDefine.uuid)
        self.name = getString(msg, ParamKeyDefine.name)

        self.cpu_count = getUInt(msg, ParamKeyDefine.cpu_count)
        self.total_volume = getUInt(msg, ParamKeyDefine.total_volume)
        self.used_volume = getUInt(msg, ParamKeyDefine.used_volume)

        timestamp = getStringArray(msg, ParamKeyDefine.timestamp)
        if len(timestamp) < 4:
            ##insufficient data
            return
        
        status = getUIntArray(msg, ParamKeyDefine.status)
        total_cpu_usage = getFloatArray(msg, ParamKeyDefine.total_cpu_usage)
        disk_usage = getFloatArray(msg, ParamKeyDefine.disk_usage)
        cpu_seconds = getFloatArray(msg, ParamKeyDefine.cpu_seconds)

        rd_req = getUIntArray(msg, ParamKeyDefine.read_request)
        rd_bytes = getUIntArray(msg, ParamKeyDefine.read_bytes)
        wr_req = getUIntArray(msg, ParamKeyDefine.write_request)
        wr_bytes = getUIntArray(msg, ParamKeyDefine.write_bytes)
        io_error = getUIntArray(msg, ParamKeyDefine.io_error)
        rd_speed = getUIntArray(msg, ParamKeyDefine.read_speed)
        wr_speed = getUIntArray(msg, ParamKeyDefine.write_speed)

        rx_bytes = getUIntArray(msg, ParamKeyDefine.received_bytes)
        rx_packets = getUIntArray(msg, ParamKeyDefine.recevied_packets)
        rx_errs = getUIntArray(msg, ParamKeyDefine.recevied_errors)
        rx_drop = getUIntArray(msg, ParamKeyDefine.received_drop)
        tx_bytes = getUIntArray(msg, ParamKeyDefine.sent_bytes)
        tx_packets = getUIntArray(msg, ParamKeyDefine.sent_packets)
        tx_errs = getUIntArray(msg, ParamKeyDefine.sent_errors)
        tx_drop = getUIntArray(msg, ParamKeyDefine.sent_drop)
        rx_speed = getUIntArray(msg, ParamKeyDefine.received_speed)
        tx_speed = getUIntArray(msg, ParamKeyDefine.sent_speed)

        for i in range(len(timestamp)):
            data = ServiceData()
            data.timestamp = timestamp[i]
            data.status = status[i]
            
            data.total_cpu_usage = total_cpu_usage[i]
            data.disk_usage = disk_usage[i]
            data.cpu_seconds = cpu_seconds[i]

            data.rd_req = rd_req[i]
            data.rd_bytes = rd_bytes[i]
            data.wr_req = wr_req[i]
            data.wr_bytes = wr_bytes[i]
            data.io_error = io_error[i]
            data.rd_speed = rd_speed[i]
            data.wr_speed = wr_speed[i]

            data.rx_bytes = rx_bytes[i]
            data.rx_packets = rx_packets[i]
            data.rx_errs = rx_errs[i]
            data.rx_drop = rx_drop[i]
            data.tx_bytes = tx_bytes[i]
            data.tx_packets = tx_packets[i]
            data.tx_errs = tx_errs[i]
            data.tx_drop = tx_drop[i]
            data.rx_speed = rx_speed[i]
            data.tx_speed = tx_speed[i]
            self.data_list.append(data)

        self.bottom_data = self.data_list.pop()
        self.top_data = self.data_list.pop()
        self.average_data = self.data_list.pop()
        self.summary_data = self.data_list.pop()
        
