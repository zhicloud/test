#!/usr/bin/python
from machine_status import *
from service.message_define import *
        
class HostStatus(MachineStatus):    
    hostname = ""
    fullname = ""
    version = ""
    actived = False
    ##list of domain uuid
    domains = []
    ##list of vlan uuid
    vlans = []

    def fromMessage(self, msg):
        """
        parse from message
        """
        self.server_room = getString(msg, ParamKeyDefine.server_room)
        self.computer_rack = getString(msg, ParamKeyDefine.computer_rack)
        self.node_name = getString(msg, ParamKeyDefine.node_name)
        self.fullname = "%s.%s.%s"%(self.server_room, self.computer_rack,
                                    self.node_name)
        
        self.actived = getBool(msg, ParamKeyDefine.actived)
        self.hostname = getString(msg, ParamKeyDefine.hostname)
        self.cpu_count = getUInt(msg, ParamKeyDefine.cpu_count)
        self.total_cpu_usage = getFloat(msg, ParamKeyDefine.total_cpu_usage)
        self.separate_cpu_usage = getFloatArray(msg, ParamKeyDefine.separate_cpu_usage)
        self.total_memory = getUInt(msg, ParamKeyDefine.total_memory)
        self.available_memory = getUInt(msg, ParamKeyDefine.available_memory)
        self.memory_usage = float(self.total_memory - self.available_memory )/self.total_memory

        disk_device = getStringArray(msg, ParamKeyDefine.disk_device)
        disk_bus_type = getStringArray(msg, ParamKeyDefine.disk_bus_type)
        disk_source = getStringArray(msg, ParamKeyDefine.disk_source)
        disk_used = getUIntArray(msg, ParamKeyDefine.disk_used)
        disk_volume = getUIntArray(msg, ParamKeyDefine.disk_volume)
        self.disks = []
        for index in range(len(disk_device)):
            self.disks.append(Disk(disk_device[index],
                                   disk_bus_type[index],
                                   disk_source[index],
                                   disk_used[index],
                                   disk_volume[index]))
            
        self.total_volume = getUInt(msg, ParamKeyDefine.total_volume)
        self.used_volume = getUInt(msg, ParamKeyDefine.used_volume)
        self.disk_usage = float(self.used_volume)/self.total_volume
        
        rd_req = getUInt(msg, ParamKeyDefine.read_request)
        rd_bytes = getUInt(msg, ParamKeyDefine.read_bytes)
        wr_req = getUInt(msg, ParamKeyDefine.write_request)
        wr_bytes = getUInt(msg, ParamKeyDefine.write_bytes)
        io_error = getUInt(msg, ParamKeyDefine.io_error)
        rd_speed = getUInt(msg, ParamKeyDefine.read_speed)
        wr_speed = getUInt(msg, ParamKeyDefine.write_speed)
        self.disk_statistic = DiskStatistic(rd_req, rd_bytes, wr_req, wr_bytes,
                                            io_error, rd_speed, wr_speed)
        
        network_device = getStringArray(msg, ParamKeyDefine.network_device)
        ethernet_address = getStringArray(msg, ParamKeyDefine.ethernet_address)
        ip = getStringArray(msg, ParamKeyDefine.ip)
        network_type = getUIntArray(msg, ParamKeyDefine.network_type)
        received_bytes = getUIntArray(msg, ParamKeyDefine.received_bytes)
        recevied_packets = getUIntArray(msg, ParamKeyDefine.recevied_packets)
        recevied_errors = getUIntArray(msg, ParamKeyDefine.recevied_errors)
        received_drop = getUIntArray(msg, ParamKeyDefine.received_drop)
        sent_bytes = getUIntArray(msg, ParamKeyDefine.sent_bytes)
        sent_packets = getUIntArray(msg, ParamKeyDefine.sent_packets)
        sent_errors = getUIntArray(msg, ParamKeyDefine.sent_errors)
        sent_drop = getUIntArray(msg, ParamKeyDefine.sent_drop)
        received_speed = getUIntArray(msg, ParamKeyDefine.received_speed)
        sent_speed = getUIntArray(msg, ParamKeyDefine.sent_speed)
        self.network_statistic = NetworkStatistic()
        self.networks = {}
        for index in range(len(network_device)):
            statistic = NetworkStatistic(received_bytes[index],
                                         recevied_packets[index],
                                         recevied_errors[index],
                                         received_drop[index],
                                         sent_bytes[index],
                                         sent_packets[index],
                                         sent_errors[index],
                                         sent_drop[index],
                                         received_speed[index],
                                         sent_speed[index])
            self.network_statistic += statistic
            mac = ethernet_address[index]
            self.networks[mac] = NetworkInterface(network_device[index],
                                                  ethernet_address[index],
                                                  ip[index],
                                                  network_type[index],
                                                  statistic)
        self.version = getString(msg, ParamKeyDefine.version)
        self.timestamp = getString(msg, ParamKeyDefine.timestamp)
        self.operation_system = getString(msg, ParamKeyDefine.operation_system)
        ##end for index in range(len(network_device)):    

        self.domains = getStringArray(msg, ParamKeyDefine.domain_id)
        self.vlans = getStringArray(msg, ParamKeyDefine.network_id)
        
    def toMessage(self, msg):
        setString(msg , ParamKeyDefine.server_room, self.server_room)
        setString(msg , ParamKeyDefine.computer_rack, self.computer_rack)            
        setString(msg, ParamKeyDefine.node_name, self.node)
        
        setString(msg, ParamKeyDefine.hostname, self.hostname)
        setUInt(msg, ParamKeyDefine.cpu_count, self.cpu_count)
        setFloat(msg, ParamKeyDefine.total_cpu_usage, self.total_cpu_usage)
        setFloatArray(msg, ParamKeyDefine.separate_cpu_usage, self.separate_cpu_usage)
        setUInt(msg, ParamKeyDefine.total_memory, self.total_memory)
        setUInt(msg, ParamKeyDefine.available_memory, self.available_memory)
        disk_device = []
        disk_bus_type = []
        disk_source = []
        disk_used = []
        disk_volume = []
        for disk in self.disks:
            disk_device.append(disk.device)
            disk_bus_type.append(disk.bus_type)
            disk_source.append(disk.source)
            disk_used.append(disk.used_volume)
            disk_volume.append(disk.total_volume)
        setStringArray(msg, ParamKeyDefine.disk_device, disk_device)
        setStringArray(msg, ParamKeyDefine.disk_bus_type, disk_bus_type)
        setStringArray(msg, ParamKeyDefine.disk_source, disk_source)
        setUIntArray(msg, ParamKeyDefine.disk_used, disk_used)
        setUIntArray(msg, ParamKeyDefine.disk_volume, disk_volume)
        
        setUInt(msg, ParamKeyDefine.total_volume, self.total_volume)
        setUInt(msg, ParamKeyDefine.used_volume, self.used_volume)
        setFloat(msg, ParamKeyDefine.disk_usage, self.disk_usage)
        
        setUInt(msg, ParamKeyDefine.read_request, self.disk_statistic.rd_req)
        setUInt(msg, ParamKeyDefine.read_bytes, self.disk_statistic.rd_bytes)
        setUInt(msg, ParamKeyDefine.write_request, self.disk_statistic.wr_req)
        setUInt(msg, ParamKeyDefine.write_bytes, self.disk_statistic.wr_bytes)
        setUInt(msg, ParamKeyDefine.io_error, self.disk_statistic.io_error)
        setUInt(msg, ParamKeyDefine.read_speed, self.disk_statistic.rd_speed)
        setUInt(msg, ParamKeyDefine.write_speed, self.disk_statistic.wr_speed)
        
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
        for interface in self.networks.values():
            network_device.append(interface.device)
            ethernet_address.append(interface.mac)
            ip.append(interface.ip)
            network_type.append(interface.network_type)
            
            received_bytes.append(interface.statistic.rx_bytes)
            recevied_packets.append(interface.statistic.rx_packets)
            recevied_errors.append(interface.statistic.rx_errs)
            received_drop.append(interface.statistic.rx_drop)
            sent_bytes.append(interface.statistic.tx_bytes)
            sent_packets.append(interface.statistic.tx_packets)
            sent_errors.append(interface.statistic.tx_errs)
            sent_drop.append(interface.statistic.tx_drop)
            received_speed.append(interface.statistic.rx_speed)
            sent_speed.append(interface.statistic.tx_speed)

            
        setStringArray(msg, ParamKeyDefine.network_device, network_device)
        setStringArray(msg, ParamKeyDefine.ethernet_address, ethernet_address)
        setStringArray(msg, ParamKeyDefine.ip, ip)
        setUIntArray(msg, ParamKeyDefine.network_type, network_type)
        setUIntArray(msg, ParamKeyDefine.received_bytes, received_bytes)
        setUIntArray(msg, ParamKeyDefine.recevied_packets, recevied_packets)
        setUIntArray(msg, ParamKeyDefine.recevied_errors, recevied_errors)
        setUIntArray(msg, ParamKeyDefine.received_drop, received_drop)
        setUIntArray(msg, ParamKeyDefine.sent_bytes, sent_bytes)
        setUIntArray(msg, ParamKeyDefine.sent_packets, sent_packets)
        setUIntArray(msg, ParamKeyDefine.sent_errors, sent_errors)
        setUIntArray(msg, ParamKeyDefine.sent_drop, sent_drop)
        setUIntArray(msg, ParamKeyDefine.received_speed, received_speed)
        setUIntArray(msg, ParamKeyDefine.sent_speed, sent_speed)
        setUInt(msg, ParamKeyDefine.total_received_speed, self.network_statistic.rx_speed)
        setUInt(msg, ParamKeyDefine.total_sent_speed, self.network_statistic.tx_speed)
        setString(msg, ParamKeyDefine.version, self.version)
        setString(msg, ParamKeyDefine.operation_system, self.operation_system)
        setString(msg, ParamKeyDefine.timestamp, self.timestamp)
        setBool(msg, ParamKeyDefine.actived, self.actived)
        setStringArray(msg, ParamKeyDefine.domain_id, self.domains)
        setStringArray(msg, ParamKeyDefine.network_id, self.vlans)           

    @staticmethod
    def unpackFromMessage(msg):
        server_room = getStringArray(msg, ParamKeyDefine.server_room)
        computer_rack = getStringArray(msg, ParamKeyDefine.computer_rack)        
        node_name = getStringArray(msg, ParamKeyDefine.node_name)
        
        actived = getUIntArray(msg, ParamKeyDefine.actived)
        hostname = getStringArray(msg, ParamKeyDefine.hostname)
        
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

        domains = getStringArrayArray(msg, ParamKeyDefine.domain_id)
        vlans = getStringArrayArray(msg, ParamKeyDefine.network_id)
        version = getStringArray(msg, ParamKeyDefine.version)
        
        result = []
        for i in range(len(node_name)):
            data = HostStatus()
            data.server_room = server_room[i]
            data.computer_rack = computer_rack[i]
            data.node_name = node_name[i]
            data.hostname = hostname[i]
            data.fullname = "%s.%s.%s"%(data.server_room, data.computer_rack,
                                        data.node_name)
            if 1 == actived[i]:
                data.actived = True
            else:
                data.actived = False
                
            data.operation_system = operation_system[i]
            data.timestamp = timestamp[i]
            data.cpu_count = cpu_count[i]
            data.total_cpu_usage = total_cpu_usage[i]
            data.separate_cpu_usage = separate_cpu_usage[i]
            data.total_memory = total_memory[i]
            data.available_memory = available_memory[i]
            if (data.actived) and (data.available_memory <= data.total_memory):
                data.memory_usage = float(data.total_memory - data.available_memory)/data.total_memory
            else:
                data.memory_usage = 0.0
                
            data.disk = []
            for j in range(len(disk_device[i])):
                data.disk.append(Disk(disk_device[i][j],
                                        disk_bus_type[i][j],
                                        disk_source[i][j],
                                        disk_used[i][j],
                                        disk_volume[i][j]))
                
                                        
            data.total_volume = total_volume[i]
            data.used_volume = used_volume[i]
            if 0 != data.total_volume:
                data.disk_usage = float(data.used_volume)/data.total_volume
            else:
                ##initial host status,total volume = 0
                data.disk_usage = 0.0
            data.disk_statistic = DiskStatistic(read_request[i],
                                                read_bytes[i],
                                                write_request[i],
                                                write_bytes[i],
                                                io_error[i],
                                                read_speed[i],
                                                write_speed[i])
            
            data.network_statistic = NetworkStatistic()
            data.networks = {}
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
                data.network_statistic += statistic
                mac = ethernet_address[i][j]
                data.networks[mac] = NetworkInterface(network_device[i][j],
                                                        mac,
                                                        ip[i][j],
                                                        network_type[i][j],
                                                        statistic)

            data.domains.extend(domains[i])
            data.vlans.extend(vlans[i])
            data.version = version[i]
            result.append(data)
        return result

    @staticmethod
    def packToMessage(msg, data_list):
        hostname = []
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
        actived = []
        operation_system = []
        timestamp = []
        domains = []
        vlans = []
        version = []
        for data in data_list:
            hostname.append(data.hostname)
            node_name.append(data.node_name)
            server_room.append(data.server_room)
            computer_rack.append(data.computer_rack)            
            if data.actived:
                actived.append(1)
            else:
                actived.append(0)
            
            cpu_count.append(data.cpu_count)
            total_cpu_usage.append(data.total_cpu_usage)
            separate_cpu_usage.append(data.separate_cpu_usage)
            total_memory.append(data.total_memory)
            available_memory.append(data.available_memory)

            domains.append(data.domains)
            vlans.append(data.vlans)
            version.append(data.version)
            
            host_disk_device = []
            host_disk_bus_type = []
            host_disk_source = []
            host_disk_used = []
            host_disk_volume = []
            for disk in data.disks:
                host_disk_device.append(disk.device)
                host_disk_bus_type.append(disk.bus_type)
                host_disk_source.append(disk.source)
                host_disk_used.append(disk.used_volume)
                host_disk_volume.append(disk.total_volume)
                
            disk_device.append(host_disk_device)
            disk_bus_type.append(host_disk_bus_type)
            disk_source.append(host_disk_source)
            disk_used.append(host_disk_used)
            disk_volume.append(host_disk_volume)

            total_volume.append(data.total_volume)
            used_volume.append(data.used_volume)
            
            read_request.append(data.disk_statistic.rd_req)
            read_bytes.append(data.disk_statistic.rd_bytes)
            write_request.append(data.disk_statistic.wr_req)
            write_bytes.append(data.disk_statistic.wr_bytes)
            io_error.append(data.disk_statistic.io_error)
            read_speed.append(data.disk_statistic.rd_speed)
            write_speed.append(data.disk_statistic.wr_speed)
            
            host_network_device = []
            host_ethernet_address = []
            host_ip = []
            host_network_type = []
            host_received_bytes = []
            host_recevied_packets = []
            host_recevied_errors = []
            host_received_drop = []
            host_sent_bytes = []
            host_sent_packets = []
            host_sent_errors = []
            host_sent_drop = []
            host_received_speed = []
            host_sent_speed = []
            for interface in data.networks.values():
                host_network_device.append(interface.device)
                host_ethernet_address.append(interface.mac)
                host_ip.append(interface.ip)
                host_network_type.append(interface.network_type)
                host_received_bytes.append(interface.statistic.rx_bytes)
                host_recevied_packets.append(interface.statistic.rx_packets)
                host_recevied_errors.append(interface.statistic.rx_errs)
                host_received_drop.append(interface.statistic.rx_drop)
                host_sent_bytes.append(interface.statistic.tx_bytes)
                host_sent_packets.append(interface.statistic.tx_packets)
                host_sent_errors.append(interface.statistic.tx_errs)
                host_sent_drop.append(interface.statistic.tx_drop)
                host_received_speed.append(interface.statistic.rx_speed)
                host_sent_speed.append(interface.statistic.tx_speed)            

            network_device.append(host_network_device)
            ethernet_address.append(host_ethernet_address)
            ip.append(host_ip)
            network_type.append(host_network_type)
            received_bytes.append(host_received_bytes)
            recevied_packets.append(host_recevied_packets)
            recevied_errors.append(host_recevied_errors)
            received_drop.append(host_received_drop)
            sent_bytes.append(host_sent_bytes)
            sent_packets.append(host_sent_packets)
            sent_errors.append(host_sent_errors)
            sent_drop.append(host_sent_drop)
            received_speed.append(host_received_speed)
            sent_speed.append(host_sent_speed)

            total_received_speed.append(data.network_statistic.rx_speed)
            total_sent_speed.append(data.network_statistic.tx_speed)
            operation_system.append(data.operation_system)
            timestamp.append(data.timestamp)

        ##end for domain in self.node_status.domains:
        setUIntArray(msg, ParamKeyDefine.actived, actived)
        setStringArray(msg, ParamKeyDefine.hostname, hostname)
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
        setStringArray(msg, ParamKeyDefine.timestamp, timestamp)
        setStringArray(msg, ParamKeyDefine.version, version)
        setStringArrayArray(msg, ParamKeyDefine.domain_id, domains)
        setStringArrayArray(msg, ParamKeyDefine.network_id, vlans)        
