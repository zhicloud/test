#!/usr/bin/python
# -*- coding: utf-8 -*-
from machine_status import *
from service.message_define import *

class DomainStatus(MachineStatus):
    class StatusEnum(object):
        no_state = 0
        running = 1
        blocked = 2
        paused = 3
        shutdown = 4
        shutoff = 5
        crashed = 6
        pm_suspend = 7
        
    name = ""
    fullname = ""
    uuid = ""
    status = StatusEnum.no_state
    ##vnc listen port, only valid when running
    port = 0

    def isRunning(self):
        return (DomainStatus.StatusEnum.running == self.status)

    @staticmethod
    def unpackFromMessage(msg):
        server_room = getStringArray(msg, ParamKeyDefine.server_room)
        computer_rack = getStringArray(msg, ParamKeyDefine.computer_rack)        
        node_name = getStringArray(msg, ParamKeyDefine.node_name)
        uuid = getStringArray(msg, ParamKeyDefine.uuid)
        status = getUIntArray(msg, ParamKeyDefine.status)
        name = getStringArray(msg, ParamKeyDefine.domain)
        cpu_count = getUIntArray(msg, ParamKeyDefine.cpu_count)
        total_cpu_usage = getFloatArray(msg, ParamKeyDefine.total_cpu_usage)
        separate_cpu_usage = getFloatArrayArray(msg, ParamKeyDefine.separate_cpu_usage)
        total_memory = getUIntArray(msg, ParamKeyDefine.total_memory)
        available_memory = getUIntArray(msg, ParamKeyDefine.available_memory)
        timestamp = getStringArray(msg, ParamKeyDefine.timestamp)
        operation_system = getStringArray(msg, ParamKeyDefine.operation_system)
        
        disk_device = getStringArrayArray(msg, ParamKeyDefine.disk_device)
        disk_bus_type = getStringArrayArray(msg, ParamKeyDefine.disk_bus_type)
        disk_source = getStringArrayArray(msg, ParamKeyDefine.disk_source)
        disk_used = getUIntArrayArray(msg, ParamKeyDefine.disk_used)
        disk_volume = getUIntArrayArray(msg, ParamKeyDefine.disk_volume)
        total_volume = getUIntArray(msg, ParamKeyDefine.total_volume)
        used_volume = getUIntArray(msg, ParamKeyDefine.used_volume)
        read_request = getUIntArray(msg, ParamKeyDefine.read_request)
        read_bytes = getUIntArray(msg, ParamKeyDefine.read_bytes)
        write_request = getUIntArray(msg, ParamKeyDefine.write_request)
        write_bytes = getUIntArray(msg, ParamKeyDefine.write_bytes)
        io_error = getUIntArray(msg, ParamKeyDefine.io_error)
        read_speed = getUIntArray(msg, ParamKeyDefine.read_speed)
        write_speed = getUIntArray(msg, ParamKeyDefine.write_speed)

        network_device = getStringArrayArray(msg, ParamKeyDefine.network_device)
        ethernet_address = getStringArrayArray(msg, ParamKeyDefine.ethernet_address)
        ip = getStringArrayArray(msg, ParamKeyDefine.ip)    
        network_type = getUIntArrayArray(msg, ParamKeyDefine.network_type)
        
        received_bytes = getUIntArrayArray(msg, ParamKeyDefine.received_bytes)
        recevied_packets = getUIntArrayArray(msg, ParamKeyDefine.recevied_packets)
        recevied_errors = getUIntArrayArray(msg, ParamKeyDefine.recevied_errors)
        received_drop = getUIntArrayArray(msg, ParamKeyDefine.received_drop)
        sent_bytes = getUIntArrayArray(msg, ParamKeyDefine.sent_bytes)
        sent_packets = getUIntArrayArray(msg, ParamKeyDefine.sent_packets)
        sent_errors = getUIntArrayArray(msg, ParamKeyDefine.sent_errors)
        sent_drop = getUIntArrayArray(msg, ParamKeyDefine.sent_drop)
        received_speed = getUIntArrayArray(msg, ParamKeyDefine.received_speed)
        sent_speed = getUIntArrayArray(msg, ParamKeyDefine.sent_speed)

        port = getUIntArray(msg, ParamKeyDefine.port)
        
        result = []
        for i in range(len(uuid)):
            domain = DomainStatus()
            domain.server_room = server_room[i]
            domain.computer_rack = computer_rack[i]
            domain.node_name = node_name[i]
            domain.name = name[i]
            domain.fullname = "%s.%s.%s.%s"%(domain.server_room, domain.computer_rack,
                                           domain.node_name, domain.name)
            
            domain.uuid = uuid[i]
            domain.status = status[i]
            domain.operation_system = operation_system[i]
            domain.timestamp = timestamp[i]
            domain.cpu_count = cpu_count[i]
            domain.total_cpu_usage = total_cpu_usage[i]
            domain.separate_cpu_usage = separate_cpu_usage[i]
            domain.total_memory = total_memory[i]
            domain.available_memory = available_memory[i]
            if 0 != domain.total_memory:
                domain.memory_usage = float(domain.total_memory - domain.available_memory)/domain.total_memory
            else:
                domain.memory_usage = 0.0
            domain.disk = []
            for j in range(len(disk_device[i])):
                domain.disk.append(Disk(disk_device[i][j],
                                        disk_bus_type[i][j],
                                        disk_source[i][j],
                                        disk_used[i][j],
                                        disk_volume[i][j]))
                
                                        
            domain.total_volume = total_volume[i]
            domain.used_volume = used_volume[i]
            if 0 != domain.total_volume:
                domain.disk_usage = float(domain.used_volume)/domain.total_volume
            else:
                domain.disk_usage = 0.0
            domain.disk_statistic = DiskStatistic(read_request[i],
                                                  read_bytes[i],
                                                  write_request[i],
                                                  write_bytes[i],
                                                  io_error[i],
                                                  read_speed[i],
                                                  write_speed[i])
            
            domain.network_statistic = NetworkStatistic()
            domain.networks = {}
            for j in range(len(network_device[i])):
                statistic = NetworkStatistic(received_bytes[i][j],
                                             recevied_packets[i][j],
                                             recevied_errors[i][j],
                                             received_drop[i][j],
                                             sent_bytes[i][j],
                                             sent_packets[i][j],
                                             sent_errors[i][j],
                                             sent_drop[i][j],
                                             received_speed[i][j],
                                             sent_speed[i][j])
                domain.network_statistic += statistic
                mac = ethernet_address[i][j]
                domain.networks[mac] = NetworkInterface(network_device[i][j],
                                                        mac,
                                                        ip[i][j],
                                                        network_type[i][j],
                                                        statistic)
            domain.port = port[i]
            result.append(domain)
        return result

    @staticmethod
    def packToMessage(msg, data_list):
        name = []
        node_name = []
        server_room = []
        computer_rack = []
        cpu_count = []
        total_cpu_usage = []
        separate_cpu_usage = []
        total_memory = []
        available_memory = []
        disk_device = []
        disk_bus_type = []
        disk_source = []
        disk_used = []
        disk_volume = []
        total_volume = []
        used_volume = []
        read_request = []
        read_bytes = []
        write_request = []
        write_bytes = []
        io_error = []
        read_speed = []
        write_speed = []
        network_device = []
        ethernet_address = []
        ip = []
        network_type = []
        received_bytes = []
        recevied_packets = []
        recevied_errors = []
        received_drop = []
        sent_bytes = []
        sent_packets = []
        sent_errors = []
        sent_drop = []
        received_speed = []
        sent_speed = []
        total_received_speed = []
        total_sent_speed = []
        uuid = []
        status = []
        operation_system = []
        timestamp = []
        port = []
        for domain in data_list:
            name.append(domain.name)
            node_name.append(domain.node_name)
            server_room.append(domain.server_room)
            computer_rack.append(domain.computer_rack)            
            uuid.append(domain.uuid)
            status.append(domain.status)
            cpu_count.append(domain.cpu_count)
            total_cpu_usage.append(domain.total_cpu_usage)
            separate_cpu_usage.append(domain.separate_cpu_usage)
            total_memory.append(domain.total_memory)
            available_memory.append(domain.available_memory)
            domain_disk_device = []
            domain_disk_bus_type = []
            domain_disk_source = []
            domain_disk_used = []
            domain_disk_volume = []
            for disk in domain.disks:
                domain_disk_device.append(disk.device)
                domain_disk_bus_type.append(disk.bus_type)
                domain_disk_source.append(disk.source)
                domain_disk_used.append(disk.used_volume)
                domain_disk_volume.append(disk.total_volume)
                
            disk_device.append(domain_disk_device)
            disk_bus_type.append(domain_disk_bus_type)
            disk_source.append(domain_disk_source)
            disk_used.append(domain_disk_used)
            disk_volume.append(domain_disk_volume)

            total_volume.append(domain.total_volume)
            used_volume.append(domain.used_volume)
            
            read_request.append(domain.disk_statistic.rd_req)
            read_bytes.append(domain.disk_statistic.rd_bytes)
            write_request.append(domain.disk_statistic.wr_req)
            write_bytes.append(domain.disk_statistic.wr_bytes)
            io_error.append(domain.disk_statistic.io_error)
            read_speed.append(domain.disk_statistic.rd_speed)
            write_speed.append(domain.disk_statistic.wr_speed)
            
            domain_network_device = []
            domain_ethernet_address = []
            domain_ip = []
            domain_network_type = []
            domain_received_bytes = []
            domain_recevied_packets = []
            domain_recevied_errors = []
            domain_received_drop = []
            domain_sent_bytes = []
            domain_sent_packets = []
            domain_sent_errors = []
            domain_sent_drop = []
            domain_received_speed = []
            domain_sent_speed = []
            for interface in domain.networks.values():
                domain_network_device.append(interface.device)
                domain_ethernet_address.append(interface.mac)
                domain_ip.append(interface.ip)
                domain_network_type.append(interface.network_type)
                domain_received_bytes.append(interface.statistic.rx_bytes)
                domain_recevied_packets.append(interface.statistic.rx_packets)
                domain_recevied_errors.append(interface.statistic.rx_errs)
                domain_received_drop.append(interface.statistic.rx_drop)
                domain_sent_bytes.append(interface.statistic.tx_bytes)
                domain_sent_packets.append(interface.statistic.tx_packets)
                domain_sent_errors.append(interface.statistic.tx_errs)
                domain_sent_drop.append(interface.statistic.tx_drop)
                domain_received_speed.append(interface.statistic.rx_speed)
                domain_sent_speed.append(interface.statistic.tx_speed)            

            network_device.append(domain_network_device)
            ethernet_address.append(domain_ethernet_address)
            ip.append(domain_ip)
            network_type.append(domain_network_type)
            received_bytes.append(domain_received_bytes)
            recevied_packets.append(domain_recevied_packets)
            recevied_errors.append(domain_recevied_errors)
            received_drop.append(domain_received_drop)
            sent_bytes.append(domain_sent_bytes)
            sent_packets.append(domain_sent_packets)
            sent_errors.append(domain_sent_errors)
            sent_drop.append(domain_sent_drop)
            received_speed.append(domain_received_speed)
            sent_speed.append(domain_sent_speed)

            total_received_speed.append(domain.network_statistic.rx_speed)
            total_sent_speed.append(domain.network_statistic.tx_speed)
            operation_system.append(domain.operation_system)
            timestamp.append(domain.timestamp)
            port.append(domain.port)

        ##end for domain in self.node_status.domains:
        setStringArray(msg, ParamKeyDefine.uuid, uuid)
        setUIntArray(msg, ParamKeyDefine.status, status)
        setStringArray(msg, ParamKeyDefine.domain, name)
        setUIntArray(msg, ParamKeyDefine.cpu_count, cpu_count)
        setFloatArray(msg, ParamKeyDefine.total_cpu_usage, total_cpu_usage)
        setFloatArrayArray(msg, ParamKeyDefine.separate_cpu_usage, separate_cpu_usage)
        setUIntArray(msg, ParamKeyDefine.total_memory, total_memory)
        setUIntArray(msg, ParamKeyDefine.available_memory, available_memory)

        setStringArrayArray(msg, ParamKeyDefine.disk_device, disk_device)
        setStringArrayArray(msg, ParamKeyDefine.disk_bus_type, disk_bus_type)
        setStringArrayArray(msg, ParamKeyDefine.disk_source, disk_source)
        setUIntArrayArray(msg, ParamKeyDefine.disk_used, disk_used)
        setUIntArrayArray(msg, ParamKeyDefine.disk_volume, disk_volume)
        setUIntArray(msg, ParamKeyDefine.total_volume, total_volume)
        setUIntArray(msg, ParamKeyDefine.used_volume, used_volume)
        setUIntArray(msg, ParamKeyDefine.read_request, read_request)
        setUIntArray(msg, ParamKeyDefine.read_bytes, read_bytes)
        setUIntArray(msg, ParamKeyDefine.write_request, write_request)
        setUIntArray(msg, ParamKeyDefine.write_bytes, write_bytes)
        setUIntArray(msg, ParamKeyDefine.io_error, io_error)
        setUIntArray(msg, ParamKeyDefine.read_speed, read_speed)
        setUIntArray(msg, ParamKeyDefine.write_speed, write_speed)
            
        setStringArrayArray(msg, ParamKeyDefine.network_device, network_device)
        setStringArrayArray(msg, ParamKeyDefine.ethernet_address, ethernet_address)
        setStringArrayArray(msg, ParamKeyDefine.ip, ip)
        setUIntArrayArray(msg, ParamKeyDefine.network_type, network_type)
        setUIntArrayArray(msg, ParamKeyDefine.received_bytes, received_bytes)
        setUIntArrayArray(msg, ParamKeyDefine.recevied_packets, recevied_packets)
        setUIntArrayArray(msg, ParamKeyDefine.recevied_errors, recevied_errors)
        setUIntArrayArray(msg, ParamKeyDefine.received_drop, received_drop)
        setUIntArrayArray(msg, ParamKeyDefine.sent_bytes, sent_bytes)
        setUIntArrayArray(msg, ParamKeyDefine.sent_packets, sent_packets)
        setUIntArrayArray(msg, ParamKeyDefine.sent_errors, sent_errors)
        setUIntArrayArray(msg, ParamKeyDefine.sent_drop, sent_drop)
        setUIntArrayArray(msg, ParamKeyDefine.received_speed, received_speed)
        setUIntArrayArray(msg, ParamKeyDefine.sent_speed, sent_speed)
        setUIntArray(msg, ParamKeyDefine.total_received_speed, total_received_speed)
        setUIntArray(msg, ParamKeyDefine.total_sent_speed, total_sent_speed)

        setStringArray(msg , ParamKeyDefine.server_room, server_room)
        setStringArray(msg , ParamKeyDefine.computer_rack, computer_rack)
        setStringArray(msg, ParamKeyDefine.node_name, node_name)
        
        setStringArray(msg, ParamKeyDefine.operation_system, operation_system)
        setStringArray(msg, ParamKeyDefine.timestamp,timestamp)
        setUIntArray(msg, ParamKeyDefine.port, port)
