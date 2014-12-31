#!/usr/bin/python

class ServiceData(object):
    def __init__(self):
        self.timestamp = ""
        self.status = 0
        self.total_cpu_usage = 0.0
        self.disk_usage = 0.0
        
        self.cpu_seconds = 0.0

        self.rd_req = 0
        self.rd_bytes = 0
        self.wr_req = 0
        self.wr_bytes = 0
        self.io_error = 0
        self.rd_speed = 0
        self.wr_speed = 0
        
        self.rx_bytes = 0
        self.rx_packets = 0
        self.rx_errs = 0
        self.rx_drop = 0
        self.tx_bytes = 0
        self.tx_packets = 0
        self.tx_errs = 0
        self.tx_drop = 0
        self.rx_speed = 0
        self.tx_speed = 0

    @staticmethod
    def accumulate(data_list):
        result = ServiceData()
        for data in data_list:
            result.cpu_seconds += data.cpu_seconds
            result.rd_req += data.rd_req
            result.rd_bytes += data.rd_bytes
            result.wr_req += data.wr_req
            result.wr_bytes += data.wr_bytes
            result.io_error += data.io_error

            result.rx_bytes += data.rx_bytes
            result.rx_packets += data.rx_packets
            result.rx_errs += data.rx_errs
            result.rx_drop += data.rx_drop
            result.tx_bytes += data.tx_bytes
            result.tx_packets += data.tx_packets
            result.tx_errs += data.tx_errs
            result.tx_drop += data.tx_drop
            
        return result

    @staticmethod
    def average(data_list):
        result = ServiceData()
        total_cpu_usage = 0.0
        disk_usage = 0.0
        
        cpu_seconds = 0.0
        rd_req = 0
        rd_bytes = 0
        wr_req = 0
        wr_bytes = 0
        io_error = 0
        rd_speed = 0
        wr_speed = 0
        
        rx_bytes = 0
        rx_packets = 0
        rx_errs = 0
        rx_drop = 0
        tx_bytes = 0
        tx_packets = 0
        tx_errs = 0
        tx_drop = 0
        rx_speed = 0
        tx_speed = 0

        for data in data_list:
            total_cpu_usage += data.total_cpu_usage
            disk_usage += data.disk_usage
            cpu_seconds += data.cpu_seconds
            rd_req += data.rd_req
            rd_bytes += data.rd_bytes
            wr_req += data.wr_req
            wr_bytes += data.wr_bytes
            io_error += data.io_error
            rd_speed += data.rd_speed
            wr_speed += data.wr_speed

            rx_bytes += data.rx_bytes
            rx_packets += data.rx_packets
            rx_errs += data.rx_errs
            rx_drop += data.rx_drop
            tx_bytes += data.tx_bytes
            tx_packets += data.tx_packets
            tx_errs += data.tx_errs
            tx_drop += data.tx_drop
            rx_speed += data.rx_speed
            tx_speed += data.tx_speed

        count = len(data_list)
        result.total_cpu_usage = total_cpu_usage/count
        result.disk_usage = disk_usage/count
        result.cpu_seconds = cpu_seconds/count
        
        result.rd_req = rd_req/count
        result.rd_bytes = rd_bytes/count
        result.wr_req = wr_req/count
        result.wr_bytes = wr_bytes/count
        result.io_error = io_error/count
        result.rd_speed = rd_speed/count
        result.wr_speed = wr_speed/count
        
        result.rx_bytes = rx_bytes/count
        result.rx_packets = rx_packets/count
        result.rx_errs = rx_errs/count
        result.rx_drop = rx_drop/count
        result.tx_bytes = tx_bytes/count
        result.tx_packets = tx_packets/count
        result.tx_errs = tx_errs/count
        result.tx_drop = tx_drop/count
        result.rx_speed = rx_speed/count
        result.tx_speed = tx_speed/count

        return result

    @staticmethod
    def top(data_list):
        result = ServiceData()
        
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

        result.total_cpu_usage = max(total_cpu_usage)
        result.disk_usage = max(disk_usage)
        
        result.cpu_seconds = max(cpu_seconds)
        
        result.rd_req = max(rd_req)
        result.rd_bytes = max(rd_bytes)
        result.wr_req = max(wr_req)
        result.wr_bytes = max(wr_bytes)
        result.io_error = max(io_error)
        result.rd_speed = max(rd_speed)
        result.wr_speed = max(wr_speed)
        
        result.rx_bytes = max(rx_bytes)
        result.rx_packets = max(rx_packets)
        result.rx_errs = max(rx_errs)
        result.rx_drop = max(rx_drop)
        result.tx_bytes = max(tx_bytes)
        result.tx_packets = max(tx_packets)
        result.tx_errs = max(tx_errs)
        result.tx_drop = max(tx_drop)
        result.rx_speed = max(rx_speed)
        result.tx_speed = max(tx_speed)

        return result
    
    @staticmethod
    def bottom(data_list):
        result = ServiceData()
        
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

        result.total_cpu_usage = min(total_cpu_usage)
        result.disk_usage = min(disk_usage)
        
        result.cpu_seconds = min(cpu_seconds)
        
        result.rd_req = min(rd_req)
        result.rd_bytes = min(rd_bytes)
        result.wr_req = min(wr_req)
        result.wr_bytes = min(wr_bytes)
        result.io_error = min(io_error)
        result.rd_speed = min(rd_speed)
        result.wr_speed = min(wr_speed)
        
        result.rx_bytes = min(rx_bytes)
        result.rx_packets = min(rx_packets)
        result.rx_errs = min(rx_errs)
        result.rx_drop = min(rx_drop)
        result.tx_bytes = min(tx_bytes)
        result.tx_packets = min(tx_packets)
        result.tx_errs = min(tx_errs)
        result.tx_drop = min(tx_drop)
        result.rx_speed = min(rx_speed)
        result.tx_speed = min(tx_speed)

        return result
    
