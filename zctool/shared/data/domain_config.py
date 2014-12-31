#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import namedtuple
from xml.etree.ElementTree import *
from service.message_define import *

class DomainConfig(object):
    class NatRule(object):
        rule_all = 0
        rule_tcp = 1
        rule_udp = 2
        def __init__(self):
            self.type = self.rule_all
            self.source = 0
            self.target = 0

    class NetworkType(object):
        isolate = 0
        virtual_network = 1
        bridge = 2
        
    def __init__(self):
        self.node_name = ""
        self.type = ""
        self.name = ""
        self.uuid = ""
        self.total_memory = 0
        self.cpu_count = 0
        self.operation_system = ""
        self.architecture = ""
        self.boot = []
        self.disk_type = ""
        self.disk_source = ""
        ##disk driver
        self.disk_device = ""
        self.file_type = ""
        self.disk_bus_type = ""
        self.disk_volume = 0
        self.ethernet_address = ""
        self.network_type = 0
        self.network_source = ""
        ##driver model
        self.network_device = ""
        self.cdrom = False
        ##iso file for cdrom
        self.filename = ""
        self.auto_start = False
        ##vnc
        self.vnc_port = 0
        self.nat_rule = []
        self.ip = ""

    def usingVirtualNetwork(self):
        return (self.network_type == DomainConfig.NetworkType.virtual_network)

    def addNatRule(self, virtual_port, protocol_type, host_port = 0):
        rule = DomainConfig.NatRule()
        rule.type = protocol_type
        rule.target = virtual_port
        rule.source = host_port
        self.nat_rule.append(rule)

    def toXML(self):
        root = Element("domain")
        if 0 != len(self.type):
            root.set("type", self.type)
        if 0 != len(self.name):
            name = SubElement(root, "name")
            name.text = self.name
        if 0 != len(self.uuid):
            uuid = SubElement(root, "uuid")
            uuid.text = self.uuid
        if 0 != self.total_memory:
            memory = SubElement(root, "memory")
            memory.set("unit", "KiB")
            memory.text = str(self.total_memory/1024)
        if 0 != self.cpu_count:
            cpu = SubElement(root, "vcpu")
            cpu.text = str(self.cpu_count)
        os = SubElement(root, "os")
        os_type = SubElement(os, "type")
        os_type.text = "hvm"
        if 0 != len(self.operation_system):
            os_type.set("machine", self.operation_system)
        if 0 != len(self.architecture):
            os_type.set("arch", self.architecture)
        if 0 != len(self.boot):
            for i in range(len(self.boot)):
                boot = SubElement(os, "boot")
                boot.set("dev", self.boot[i])
            bootmenu = SubElement(os, "bootmenu")
            bootmenu.set("enable", "yes")
        devices = SubElement(root, "devices")
        
        if 0 != len(self.disk_type):
            disk_element = SubElement(devices, "disk")
            disk_element.set("type", self.disk_type)
            disk_element.set("device", "disk")                
            if 0 != len(self.disk_device):
                driver = SubElement(disk_element, "driver")
                driver.set("name", self.disk_device)
                driver.set("type", self.file_type)
            if 0 != len(self.disk_source):
                source = SubElement(disk_element, "source")
                source.set("file", self.disk_source)
            if 0 != len(self.disk_bus_type):
                target = SubElement(disk_element, "target")
                target.set("bus", self.disk_bus_type)
        if self.cdrom:
            ##has cdrom
            disk_element = SubElement(devices, "disk")
            disk_element.set("type", self.disk_type)
            disk_element.set("device", "cdrom")
            read_only = SubElement(disk_element, "readonly")
            if 0 != self.filename:
                source = SubElement(disk_element, "source")
                source.set("file", self.filename)
                    
        if DomainConfig.NetworkType.isolate != self.network_type:
            interface = SubElement(devices, "interface")
            if DomainConfig.NetworkType.network == self.network_type:
                interface.set("type", "network")
                source = SubElement(interface, "source")
                source.set("network", self.network_source)
            elif DomainConfig.NetworkType.bridge == self.network_type:
                interface.set("type", "bridge")
                source = SubElement(interface, "source")
                source.set("bridge", self.network_source)
                
            if 0 != len(self.ethernet_address):
                mac = SubElement(interface, "mac")
                mac.set("address", self.ethernet_address)
                
            if 0 != len(self.network_device):
                model = SubElement(interface, "model")
                model.set("type", self.network_device)

        if 0 != self.vnc_port:
            graphics = SubElement(devices, "graphics")
            graphics.set("type", "spice")
            graphics.set("port", str(self.vnc_port))
            graphics.set("listen", "0.0.0.0")
            
        ##sound device
        sound = SubElement(devices, "sound")
        sound.set("model", "es1370")
        ##spicevmc channel
        channel = SubElement(devices, "channel")
        channel.set("type", "spicevmc")
        channel_target = SubElement(channel, "target")
        channel_target.set("type", "virtio")
            
        return tostring(root, "utf-8")

    def fromXML(self, xml_content):
        root = fromstring(xml_content)
        self.type = root.get("type")
        name = root.find("name")
        if name is not None:
            self.name = name.text
        uuid = root.find("uuid")
        if uuid is not None:
            self.uuid = uuid.text
        memory = root.find("memory")
        if memory is not None:
            if "KiB" == memory.get("unit"):
                self.total_memory = int(memory.text)*1024
        vcpu = root.find("vcpu")
        if vcpu is not None:
            self.cpu_count = int(vcpu.text)
        ##OS
        os = root.find("os")
        if os is not None:
            os_type = os.find("type")
            if os_type is not None:
                self.operation_system = os_type.get("machine")
                self.architecture = os_type.get("arch")

            ##boot order
            self.boot = []
            for boot in os.findall("boot"):
                self.boot.append(boot.get("dev"))
        devices = root.find("devices")
        if devices is not None:
            ##disk
            for disk in devices.findall("disk"):  
                if "disk" == disk.get("device"):
                    ##disk file
                    self.disk_type = disk.get("type")
                    source = disk.find("source")
                    if source is not None:
                        self.disk_source = source.get("file")
                    driver = disk.find("driver")
                    if driver is not None:
                        self.disk_device = driver.get("name")
                        self.file_type = driver.get("type")
                    target = disk.find("target")
                    if target is not None:
                        self.disk_bus_type = target.get("bus")                    
                        
                elif "cdrom" == disk.get("device"):
                    ##cdrom iso
                    self.cdrom = True
                    source = disk.find("source")
                    if source is not None:
                        filename = source.get("file")
                        if filename is not None:
                            self.filename = filename
                
            ##network
            network = devices.find("interface")
            if network is not None:                
                mac = network.find("mac")
                if mac is not None:
                    self.ethernet_address = mac.get("address")
                    
                source = network.find("source")
                if "network" == network.get("type"):
                    self.network_type = DomainConfig.NetworkType.virtual_network
                    self.network_source = source.get("network")
                elif "bridge" == network.get("type"):
                    self.network_type = DomainConfig.NetworkType.bridge
                    self.network_source = source.get("bridge")                    

                model = network.find("model")
                if model is not None:
                    self.network_device = model.get("type")

            ##vnc port
            graphics = devices.find("graphics")
            if graphics is not None:
                graphic_type = graphics.get("type")
                if graphic_type is not None:
                    if "spice" == graphic_type:
                        ##spice
                        vnc_port = graphics.get("port")
                        if vnc_port is not None:
                            self.vnc_port = int(vnc_port)
                
        return True
        
    def toMessage(self, msg):
        setString(msg, ParamKeyDefine.type, self.type)
        setString(msg, ParamKeyDefine.name, self.name)
        setString(msg, ParamKeyDefine.node_name, self.node_name)
        setString(msg, ParamKeyDefine.uuid, self.uuid)
        setUInt(msg, ParamKeyDefine.total_memory, self.total_memory)
        setUInt(msg, ParamKeyDefine.cpu_count, self.cpu_count)
        setString(msg, ParamKeyDefine.operation_system, self.operation_system)
        setString(msg, ParamKeyDefine.architecture, self.architecture)
        setStringArray(msg, ParamKeyDefine.boot, self.boot)
        
        setString(msg, ParamKeyDefine.disk_type, self.disk_type)
        setString(msg, ParamKeyDefine.disk_device, self.disk_device)
        setString(msg, ParamKeyDefine.disk_source, self.disk_source)
        setString(msg, ParamKeyDefine.file_type, self.file_type)
        setString(msg, ParamKeyDefine.disk_bus_type, self.disk_bus_type)
        setUInt(msg, ParamKeyDefine.disk_volume, self.disk_volume)
        setString(msg, ParamKeyDefine.ethernet_address, self.ethernet_address)
        setUInt(msg, ParamKeyDefine.network_type, self.network_type)
        setString(msg, ParamKeyDefine.network_source, self.network_source)
        setString(msg, ParamKeyDefine.network_device, self.network_device)
        setBool(msg, ParamKeyDefine.cdrom, self.cdrom)
        setString(msg, ParamKeyDefine.filename, self.filename)        
        setBool(msg, ParamKeyDefine.auto_start, self.auto_start)

        setUInt(msg, ParamKeyDefine.display, self.vnc_port)
        setString(msg, ParamKeyDefine.ip, self.ip)
        rule_array = []
        if 0 != len(self.nat_rule):            
            ##nat enabled
            for rule in self.nat_rule:
                rule_array.extend([rule.type, rule.source, rule.target])
        setUIntArray(msg, ParamKeyDefine.nat, rule_array)
        return True

    def fromMessage(self, msg):
        self.type = getString(msg, ParamKeyDefine.type)
        self.name = getString(msg, ParamKeyDefine.name)
        self.node_name = getString(msg, ParamKeyDefine.node_name)
        self.uuid = getString(msg, ParamKeyDefine.uuid)
        self.total_memory = getUInt(msg, ParamKeyDefine.total_memory)
        self.cpu_count = getUInt(msg, ParamKeyDefine.cpu_count)
        self.operation_system = getString(msg, ParamKeyDefine.operation_system)
        self.architecture = getString(msg, ParamKeyDefine.architecture)
        self.boot = getStringArray(msg, ParamKeyDefine.boot)
        self.disk_type = getString(msg, ParamKeyDefine.disk_type)
        self.disk_device = getString(msg, ParamKeyDefine.disk_device)
        self.disk_source = getString(msg, ParamKeyDefine.disk_source)
        self.file_type = getString(msg, ParamKeyDefine.file_type)
        self.disk_bus_type = getString(msg, ParamKeyDefine.disk_bus_type)
        self.disk_volume = getUInt(msg, ParamKeyDefine.disk_volume)
        self.ethernet_address = getString(msg, ParamKeyDefine.ethernet_address)
        self.network_type = getUInt(msg, ParamKeyDefine.network_type)
        self.network_source = getString(msg, ParamKeyDefine.network_source)
        self.network_device = getString(msg, ParamKeyDefine.network_device)
        self.cdrom = getBool(msg, ParamKeyDefine.cdrom)
        self.filename = getString(msg, ParamKeyDefine.filename)        
        self.auto_start = getBool(msg, ParamKeyDefine.auto_start)
        self.vnc_port = getUInt(msg, ParamKeyDefine.display)
        self.ip = getString(msg, ParamKeyDefine.ip)
        rule_array = getUIntArray(msg, ParamKeyDefine.nat)
        if rule_array and 0 != len(rule_array):
            for i in range(0, len(rule_array), 3):
                self.addNatRule(rule_array[i + 2], rule_array[i],
                                rule_array[i + 1])
        return True
        
    @staticmethod
    def packToMessage(msg, data_list):
        node_name = []
        domain_type = []
        name = []
        uuid = []
        total_memory = []
        cpu_count = []
        operation_system = []
        architecture = []
        boot = []
        
        disk_type = []
        disk_device = []
        disk_source = []
        file_type = []
        disk_bus_type = []
        disk_volume = []
        
        ethernet_address = []
        network_type = []
        network_source = []
        network_device = []
        
        cdrom = []
        filename = []
        
        auto_start = []

        vnc_port = []
        ip = []

        rules = []
        
        for domain in data_list:
            node_name.append(domain.node_name)
            domain_type.append(domain.type)
            name.append(domain.name)
            uuid.append(domain.uuid)
            total_memory.append(domain.total_memory)
            cpu_count.append(domain.cpu_count)
            operation_system.append(domain.operation_system)
            architecture.append(domain.architecture)
            boot.append(domain.boot)
            
            disk_type.append(domain.disk_type)
            disk_device.append(domain.disk_device)
            disk_source.append(domain.disk_source)
            file_type.append(domain.file_type)
            disk_bus_type.append(domain.disk_bus_type)
            disk_volume.append(domain.disk_volume)
            
            ethernet_address.append(domain.ethernet_address)
            network_type.append(domain.network_type)
            network_source.append(domain.network_source)
            network_device.append(domain.network_device)
            
            if domain.cdrom:
                cdrom.append(1)
            else:
                cdrom.append(0)
                
            filename.append(domain.filename)
            
            if domain.auto_start:
                auto_start.append(1)
            else:
                auto_start.append(0)
            vnc_port.append(domain.vnc_port)
            ip.append(domain.ip)
            
            rule_array = []
            if 0 != len(domain.nat_rule):                
                ##nat enabled
                for rule in domain.nat_rule:
                    rule_array.extend([rule.type, rule.source, rule.target])
                    
            rules.append(rule_array)
                
        ##end for domain in data_list:
        setStringArray(msg, ParamKeyDefine.type, domain_type)
        setStringArray(msg, ParamKeyDefine.name, name)
        setStringArray(msg, ParamKeyDefine.node_name, node_name)
        setStringArray(msg, ParamKeyDefine.uuid, uuid)
        setUIntArray(msg, ParamKeyDefine.total_memory, total_memory)
        setUIntArray(msg, ParamKeyDefine.cpu_count, cpu_count)
        setStringArray(msg, ParamKeyDefine.operation_system, operation_system)
        setStringArray(msg, ParamKeyDefine.architecture, architecture)
        setStringArrayArray(msg, ParamKeyDefine.boot, boot)
        setStringArray(msg, ParamKeyDefine.disk_type, disk_type)
        setStringArray(msg, ParamKeyDefine.disk_device, disk_device)
        setStringArray(msg, ParamKeyDefine.disk_source, disk_source)
        setStringArray(msg, ParamKeyDefine.file_type, file_type)
        setStringArray(msg, ParamKeyDefine.disk_bus_type, disk_bus_type)
        setUIntArray(msg, ParamKeyDefine.disk_volume, disk_volume)
        
        setStringArray(msg, ParamKeyDefine.ethernet_address, ethernet_address)
        setUIntArray(msg, ParamKeyDefine.network_type, network_type)
        setStringArray(msg, ParamKeyDefine.network_source, network_source)
        setStringArray(msg, ParamKeyDefine.network_device, network_device)

        setUIntArray(msg, ParamKeyDefine.cdrom, cdrom)
        setStringArray(msg, ParamKeyDefine.filename, filename)        
        setUIntArray(msg, ParamKeyDefine.auto_start, auto_start)

        setUIntArray(msg, ParamKeyDefine.display, vnc_port)
        setStringArray(msg, ParamKeyDefine.ip, ip)        
        setUIntArrayArray(msg, ParamKeyDefine.nat, rules)
        
    @staticmethod
    def unpackFromMessage(msg):
        data_list = []
        
        domain_type = getStringArray(msg, ParamKeyDefine.type)
        name = getStringArray(msg, ParamKeyDefine.name)
        node_name = getStringArray(msg, ParamKeyDefine.node_name)
        uuid = getStringArray(msg, ParamKeyDefine.uuid)
        total_memory = getUIntArray(msg, ParamKeyDefine.total_memory)
        cpu_count = getUIntArray(msg, ParamKeyDefine.cpu_count)
        operation_system = getStringArray(msg, ParamKeyDefine.operation_system)
        architecture = getStringArray(msg, ParamKeyDefine.architecture)
        boot = getStringArrayArray(msg, ParamKeyDefine.boot)
        
        disk_type = getStringArray(msg, ParamKeyDefine.disk_type)
        disk_device = getStringArray(msg, ParamKeyDefine.disk_device)
        disk_source = getStringArray(msg, ParamKeyDefine.disk_source)
        file_type = getStringArray(msg, ParamKeyDefine.file_type)
        disk_bus_type = getStringArray(msg, ParamKeyDefine.disk_bus_type)        
        disk_volume = getUIntArray(msg, ParamKeyDefine.disk_volume)
        
        ethernet_address = getStringArray(msg, ParamKeyDefine.ethernet_address)
        network_type = getUIntArray(msg, ParamKeyDefine.network_type)
        network_source = getStringArray(msg, ParamKeyDefine.network_source)
        network_device = getStringArray(msg, ParamKeyDefine.network_device)
        cdrom = getUIntArray(msg, ParamKeyDefine.cdrom)
        filename = getStringArray(msg, ParamKeyDefine.filename)        
        auto_start = getUIntArray(msg, ParamKeyDefine.auto_start)
        vnc_port = getUIntArray(msg, ParamKeyDefine.display)
        ip = getStringArray(msg, ParamKeyDefine.ip)
        nat_rule = getUIntArrayArray(msg, ParamKeyDefine.nat)
        
        domain_count = len(name)        
        for i in range(domain_count):
            domain = DomainConfig()
            domain.type = domain_type[i]
            domain.name = name[i]
            domain.node_name = node_name[i]
            domain.uuid = uuid[i]
            domain.total_memory = total_memory[i]
            domain.cpu_count = cpu_count[i]
            domain.operation_system = operation_system[i]
            domain.architecture = architecture[i]
            domain.boot = boot[i]
            
            domain.disk_type = disk_type[i]
            domain.disk_device = disk_device[i]
            domain.disk_source = disk_source[i]
            domain.file_type = file_type[i]
            domain.disk_bus_type = disk_bus_type[i]
            domain.disk_volume = disk_volume[i]
            domain.ethernet_address = ethernet_address[i]
            domain.network_type = network_type[i]
            domain.network_source = network_source[i]
            ##driver model
            domain.network_device = network_device[i]
            if 1 == cdrom[i]:
                domain.cdrom = True
            else:
                domain.cdrom = False
                
            ##iso file for cdrom
            domain.filename = filename[i]           
                
            if 1 == auto_start[i]:
                domain.auto_start = True
            else:
                domain.auto_start = False

            domain.vnc_port = vnc_port[i]
            domain.ip = ip[i]
            if nat_rule is not None:
                rule_array = nat_rule[i]
                if 0 != len(rule_array):
                    for i in range(0, len(rule_array), 3):
                        domain.addNatRule(rule_array[i + 2], rule_array[i],
                                          rule_array[i + 1])     
            data_list.append(domain)
                
        return data_list

if __name__ == "__main__":
    content = """
<domain type='kvm' id='2'>
  <name>guest4</name>
  <uuid>bfe13018-8f13-a224-ec7d-d38023506322</uuid>
  <memory unit='KiB'>524288</memory>
  <currentMemory unit='KiB'>524288</currentMemory>
  <vcpu placement='static'>1</vcpu>
  <os>
    <type arch='x86_64' machine='rhel6.4.0'>hvm</type>
    <boot dev='fd'/>
    <boot dev='hd'/>
    <boot dev='cdrom'/>
    <bootmenu enable='yes'/>
  </os>
  <features>
    <acpi/>
    <apic/>
    <pae/>
  </features>
  <clock offset='utc'/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <devices>
    <emulator>/usr/libexec/qemu-kvm</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='raw' cache='none'/>
      <source file='/var/lib/libvirt/images/guest4.img'/>
      <target dev='hda' bus='ide'/>
      <alias name='ide0-0-0'/>
      <address type='drive' controller='0' bus='0' target='0' unit='0'/>
    </disk>
    <disk type='file' device='cdrom'>
      <driver name='qemu' type='raw' cache='none'/>
      <source file='/var/lib/libvirt/images/CentOS-6.4-x86_64-minimal.iso'/>
      <target dev='hdc' bus='ide'/>
      <readonly/>
      <address type='drive' controller='0' bus='1' target='0' unit='0'/>
    </disk>
    <controller type='usb' index='0'>
      <alias name='usb0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x2'/>
    </controller>
    <controller type='ide' index='0'>
      <alias name='ide0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x1'/>
    </controller>
    <interface type='network'>
      <mac address='52:54:00:fa:25:a4'/>
      <source network='vlan2'/>
      <target dev='vnet1'/>
      <model type='virtio'/>
      <alias name='net0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
    <serial type='pty'>
      <source path='/dev/pts/2'/>
      <target port='0'/>
      <alias name='serial0'/>
    </serial>
    <console type='pty' tty='/dev/pts/2'>
      <source path='/dev/pts/2'/>
      <target type='serial' port='0'/>
      <alias name='serial0'/>
    </console>
    <input type='tablet' bus='usb'>
      <alias name='input0'/>
    </input>
    <input type='mouse' bus='ps2'/>
    <graphics type='vnc' />
    <video>
      <model type='cirrus' vram='9216' heads='1'/>
      <alias name='video0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
    </video>
    <memballoon model='virtio'>
      <alias name='balloon0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
    </memballoon>
  </devices>
  <seclabel type='dynamic' model='selinux' relabel='yes'>
    <label>unconfined_u:system_r:svirt_t:s0:c30,c461</label>
    <imagelabel>unconfined_u:object_r:svirt_image_t:s0:c30,c461</imagelabel>
  </seclabel>
</domain>
    """
    config = DomainConfig()
    config.fromXML(content)
    string_content =  config.toXML()
    print string_content
    
    cloned_config = DomainConfig()
    cloned_config.fromXML(string_content)
    print "xml cloned"
    print cloned_config.toXML()

    message_clone = DomainConfig()
    msg = getRequest(RequestDefine.create_guest_domain)
    config.toMessage(msg)
    message_clone.fromMessage(msg)
    print "message cloned"
    print message_clone.toXML()        

    config_list = [config, cloned_config, message_clone]
    batch_msg = getRequest(RequestDefine.create_guest_domain)
    DomainConfig.packToMessage(batch_msg, config_list)

    new_list = DomainConfig.unpackFromMessage(batch_msg)
    print "batch message"
    for domain in new_list:
        print domain.toXML()

    
