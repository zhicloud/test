#!/usr/bin/python
from collections import namedtuple
from xml.etree.ElementTree import *
from service.message_define import *
static_address = namedtuple("StaticAddress", "mac, ip")

class NetworkConfig(object):
    class ForwardType:
        isolate = 0
        nat = 1
        route = 2
        
    def __init__(self):
        self.name = ""
        self.node_name = ""
        self.uuid = ""
        self.bridge = ""
        self.network_type = NetworkConfig.ForwardType.isolate
        self.target = ""
        self.ethernet_address = ""
        self.qos = False
        self.inbound_bandwidth = 0
        self.outbound_bandwidth = 0
        self.ip = ""
        self.netmask = ""
        self.dhcp = False
        self.range_start = ""
        self.range_end = ""
        self.auto_start = False
        ##key = name, value = static_address
        self.hosts = {}

    def toXML(self):
        root = Element("network")
        if 0 != len(self.name):
            name = SubElement(root, "name")
            name.text = self.name
        if 0 != len(self.uuid):
            uuid = SubElement(root, "uuid")
            uuid.text = self.uuid
        if 0 != len(self.bridge):
            bridge = SubElement(root, "bridge")
            bridge.set("name", self.bridge)
        if NetworkConfig.ForwardType.isolate != self.network_type:
            forward = SubElement(root, "forward")
            if NetworkConfig.ForwardType.nat == self.network_type:
                forward.set("mode", "nat")
            else:
                forward.set("mode", "route")
            if 0 != len(self.target):
                forward.set("dev", self.target)
        if 0 != len(self.ethernet_address):
            mac = SubElement(root, "mac")
            mac.set("address", self.ethernet_address)
        if self.qos:
            bandwidth = SubElement(root, "bandwidth")
            if 0 != self.inbound_bandwidth:
                inbound = SubElement(bandwidth, "inbound")
                inbound.set("average", str(self.inbound_bandwidth))
            if 0 != self.outbound_bandwidth:
                outbound = SubElement(bandwidth, "outbound")
                outbound.set("average", str(self.outbound_bandwidth))
        if 0 != len(self.ip):
            ip = SubElement(root, "ip")
            ip.set("address", self.ip)
            ip.set("netmask", self.netmask)
        if self.dhcp:
            dhcp = SubElement(ip, "dhcp")
            range_element = SubElement(dhcp, "range")
            range_element.set("start", self.range_start)
            range_element.set("end", self.range_end)
            if 0 != len(self.hosts):
                for name in self.hosts.keys():
                    host = SubElement(dhcp, "host")
                    host.set("name", name)
                    host.set("mac", self.hosts[name].mac)
                    host.set("ip", self.hosts[name].ip)
            
        return tostring(root, "utf-8")

    def fromXML(self, xml_content):
        root = fromstring(xml_content)
        name = root.find("name")
        if name is not None:
            self.name = name.text
        uuid = root.find("uuid")
        if uuid is not None:
            self.uuid = uuid.text
        if root.find("bridge") is not None:
            self.bridge = root.find("bridge").get("name")
        if root.find("mac") is not None:
            self.ethernet_address = root.find("mac").get("address")
        forward = root.find("forward")
        if forward is not None:
            mode = forward.get("mode")
            if "nat" == mode:
                self.network_type = NetworkConfig.ForwardType.nat
            else:
                self.network_type = NetworkConfig.ForwardType.route
            dev = forward.get("dev")
            if dev is not None:
                self.target = dev

        bandwidth = root.find("bandwidth")
        if bandwidth is not None:
            self.qos = True
            if bandwidth.find("inbound") is not None:
                self.inbound_bandwidth = int(bandwidth.find("inbound").get("average"))
            if bandwidth.find("outbound") is not None:
                self.outbound_bandwidth = int(bandwidth.find("outbound").get("average"))
        ip = root.find("ip")
        if ip is not None:
            self.ip = ip.get("address")
            self.netmask = ip.get("netmask")
            dhcp = ip.find("dhcp")
            if dhcp is not None:
                self.dhcp = True
                range_element = dhcp.find("range")
                if range_element is not None:
                    self.range_start = range_element.get("start")
                    self.range_end = range_element.get("end")
                for host in dhcp.findall("host"):
                    name = host.get("name")
                    mac = host.get("mac")
                    ip = host.get("ip")
                    self.hosts[name] = static_address(mac, ip)
        return True
        
    def toMessage(self, msg):
        setString(msg, ParamKeyDefine.name, self.name)
        setString(msg, ParamKeyDefine.node_name, self.node_name)
        setString(msg, ParamKeyDefine.uuid, self.uuid)
        setString(msg, ParamKeyDefine.bridge, self.bridge)
        setUInt(msg, ParamKeyDefine.network_type, self.network_type)
        setString(msg, ParamKeyDefine.target, self.target)
        setString(msg, ParamKeyDefine.ethernet_address, self.ethernet_address)        
        setBool(msg, ParamKeyDefine.qos, self.qos)
        setUInt(msg, ParamKeyDefine.inbound_bandwidth, self.inbound_bandwidth)
        setUInt(msg, ParamKeyDefine.outbound_bandwidth, self.outbound_bandwidth)
        setString(msg, ParamKeyDefine.ip, self.ip)
        setString(msg, ParamKeyDefine.netmask, self.netmask)        
        setBool(msg, ParamKeyDefine.dhcp, self.dhcp)
        setString(msg, ParamKeyDefine.range_start, self.range_start)
        setString(msg, ParamKeyDefine.range_end, self.range_end)
        setBool(msg, ParamKeyDefine.auto_start, self.auto_start)
        ##key = name, value = static_address
        hostname = []
        host_mac = []
        host_ip = []
        for name in self.hosts.keys():
            address = self.hosts[name]
            hostname.append(name)
            host_mac.append(address.mac)
            host_ip.append(address.ip)
            
        setStringArray(msg, ParamKeyDefine.hostname, hostname)
        setStringArray(msg, ParamKeyDefine.host_mac, host_mac)
        setStringArray(msg, ParamKeyDefine.host_ip, host_ip)

    def fromMessage(self, msg):
        self.name = getString(msg, ParamKeyDefine.name)
        self.node_name = getString(msg, ParamKeyDefine.node_name)
        self.uuid = getString(msg, ParamKeyDefine.uuid)
        self.bridge = getString(msg, ParamKeyDefine.bridge)
        self.network_type = getUInt(msg, ParamKeyDefine.network_type)
        self.target = getString(msg, ParamKeyDefine.target)
        self.ethernet_address = getString(msg, ParamKeyDefine.ethernet_address)
        self.qos = getBool(msg, ParamKeyDefine.qos)
        self.inbound_bandwidth = getUInt(msg, ParamKeyDefine.inbound_bandwidth)
        self.outbound_bandwidth = getUInt(msg, ParamKeyDefine.outbound_bandwidth)        
        self.ip = getString(msg, ParamKeyDefine.ip)
        self.netmask = getString(msg, ParamKeyDefine.netmask)
        self.dhcp = getBool(msg, ParamKeyDefine.dhcp)
        self.range_start = getString(msg, ParamKeyDefine.range_start)
        self.range_end = getString(msg, ParamKeyDefine.range_end)
        self.auto_start = getBool(msg, ParamKeyDefine.auto_start)
        hostname = getStringArray(msg, ParamKeyDefine.hostname)
        host_mac = getStringArray(msg, ParamKeyDefine.host_mac)
        host_ip = getStringArray(msg, ParamKeyDefine.host_ip)
        self.hosts = {}
        for i in range(len(hostname)):
            self.hosts[hostname[i]] = static_address(host_mac[i], host_ip[i])
        
    @staticmethod
    def packToMessage(msg, data_list):
        name = []
        node_name = []
        uuid = []
        bridge = []
        network_type = []
        target = []
        ethernet_address = []
        qos = []
        inbound_bandwidth = []
        outbound_bandwidth = []
        ip = []
        netmask = []
        dhcp = []
        range_start = []
        range_end = []
        auto_start = []
        hostname = []
        host_mac = []
        host_ip = []
        for data in data_list:
            name.append(data.name)
            node_name.append(data.node_name)
            uuid.append(data.uuid)
            bridge.append(data.bridge)
            network_type.append(data.network_type)
            target.append(data.target)
            ethernet_address.append(data.ethernet_address)
            
            if data.qos:
                qos.append(1)
            else:
                qos.append(0)
                
            inbound_bandwidth.append(data.inbound_bandwidth)
            outbound_bandwidth.append(data.outbound_bandwidth)
            ip.append(data.ip)
            netmask.append(data.netmask)
            if data.dhcp:
                dhcp.append(1)
            else:
                dhcp.append(0)
            
            range_start.append(data.range_start)
            range_end.append(data.range_end)
            if data.auto_start:
                auto_start.append(1)
            else:
                auto_start.append(0)
                
            data_name = []
            data_mac = []
            data_ip = []
            for key in data.hosts.keys():
                address = data.hosts[key]
                data_name.append(key)
                data_mac.append(address.mac)
                data_ip.append(address.ip)

            hostname.append(data_name)
            host_mac.append(data_mac)
            host_ip.append(data_ip)
            
        setStringArray(msg, ParamKeyDefine.name, name)
        setStringArray(msg, ParamKeyDefine.node_name, node_name)
        setStringArray(msg, ParamKeyDefine.uuid, uuid)
        setStringArray(msg, ParamKeyDefine.bridge, bridge)
        setUIntArray(msg, ParamKeyDefine.network_type, network_type)
        setStringArray(msg, ParamKeyDefine.target, target)
        setStringArray(msg, ParamKeyDefine.ethernet_address, ethernet_address)        
        setUIntArray(msg, ParamKeyDefine.qos, qos)
        setUIntArray(msg, ParamKeyDefine.inbound_bandwidth, inbound_bandwidth)
        setUIntArray(msg, ParamKeyDefine.outbound_bandwidth, outbound_bandwidth)
        setStringArray(msg, ParamKeyDefine.ip, ip)
        setStringArray(msg, ParamKeyDefine.netmask, netmask)        
        setUIntArray(msg, ParamKeyDefine.dhcp, dhcp)
        setStringArray(msg, ParamKeyDefine.range_start, range_start)
        setStringArray(msg, ParamKeyDefine.range_end, range_end)
        setUIntArray(msg, ParamKeyDefine.auto_start, auto_start)
        setStringArrayArray(msg, ParamKeyDefine.hostname, hostname)
        setStringArrayArray(msg, ParamKeyDefine.host_mac, host_mac)
        setStringArrayArray(msg, ParamKeyDefine.host_ip, host_ip)   

    @staticmethod
    def unpackFromMessage(msg):
        data_list = []
        name = getStringArray(msg, ParamKeyDefine.name)
        node_name = getStringArray(msg, ParamKeyDefine.node_name)
        uuid = getStringArray(msg, ParamKeyDefine.uuid)
        bridge = getStringArray(msg, ParamKeyDefine.bridge)
        network_type = getUIntArray(msg, ParamKeyDefine.network_type)
        target = getStringArray(msg, ParamKeyDefine.target)
        ethernet_address = getStringArray(msg, ParamKeyDefine.ethernet_address)        
        qos = getUIntArray(msg, ParamKeyDefine.qos)
        inbound_bandwidth = getUIntArray(msg, ParamKeyDefine.inbound_bandwidth)
        outbound_bandwidth = getUIntArray(msg, ParamKeyDefine.outbound_bandwidth)
        ip = getStringArray(msg, ParamKeyDefine.ip)
        netmask = getStringArray(msg, ParamKeyDefine.netmask)        
        dhcp = getUIntArray(msg, ParamKeyDefine.dhcp)
        range_start = getStringArray(msg, ParamKeyDefine.range_start)
        range_end = getStringArray(msg, ParamKeyDefine.range_end)
        auto_start = getUIntArray(msg, ParamKeyDefine.auto_start)
        hostname = getStringArrayArray(msg, ParamKeyDefine.hostname)
        host_mac = getStringArrayArray(msg, ParamKeyDefine.host_mac)
        host_ip = getStringArrayArray(msg, ParamKeyDefine.host_ip)
        for i in range(len(name)):
            config = NetworkConfig()
            config.name = name[i]
            config.node_name = node_name[i]
            config.uuid = uuid[i]
            config.bridge = bridge[i]
            config.network_type = network_type[i]
            config.target = target[i]
            config.ethernet_address = ethernet_address[i]
            
            if 1 == qos[i]:
                config.qos = True
            else:
                config.qos = False
            
            config.inbound_bandwidth = inbound_bandwidth[i]
            config.outbound_bandwidth = outbound_bandwidth[i]
            config.ip = ip[i]
            config.netmask = netmask[i]
            if 1 == dhcp[i]:
                config.dhcp = True
            else:
                config.dhcp = False
            
            config.range_start = range_start[i]
            config.range_end = range_end[i]
            if 1 == auto_start[i]:
                config.auto_start = True
            else:
                config.auto_start = False
            
            data_name = hostname[i]
            data_mac = host_mac[i]
            data_ip = host_ip[i]
            for j in range(len(data_name)):
                config.hosts[data_name[j]] = static_address(
                    data_mac[j], data_ip[j])

            data_list.append(config)
            
        return data_list

if __name__ == "__main__":
    config = NetworkConfig()
    config.name = "some_vlan"
    config.uuid = "asdar234adfe-23423rw"
    config.bridge = "virbr3"
    config.ethernet_address = "asv2346sdf"
    config.network_type = 1
    config.target = "eth0"
    config.qos = True
    config.outbound_bandwidth = 3069
    config.ip = "192.168.1.2"
    config.netmask = "255.255.255.0"
    config.dhcp = True
    config.range_start = "192.168.1.20"
    config.range_end = "192.168.1.50"
    config.hosts["guest1"] = static_address("52:54:00:4e:2f:35", "172.16.0.6")
    string_content =  config.toXML()
    print string_content
    cloned_config = NetworkConfig()
    cloned_config.fromXML(string_content)
    print cloned_config.dhcp
    print cloned_config.toXML()

    
