#!/usr/bin/python
import datetime
from service.message_define import *

class VlanStatus(object):
    server_room = ""
    computer_rack = ""
    node_name = ""
    name = ""
    fullname = ""
    uuid = ""
    actived = False
    ethernet_address = ""
    ip = ""
    timestamp = ""
    ##list of tuple(domain, uuid, mac, dev)
    members = []

    @staticmethod
    def unpackFromMessage(msg):
        server_room = getStringArray(msg, ParamKeyDefine.server_room)
        computer_rack = getStringArray(msg, ParamKeyDefine.computer_rack)
            
        node_name = getStringArray(msg, ParamKeyDefine.node_name)
        name = getStringArray(msg, ParamKeyDefine.vlan)
        uuid = getStringArray(msg, ParamKeyDefine.network_id)
        actived = getUIntArray(msg, ParamKeyDefine.actived)
        vlan_mac = getStringArray(msg, ParamKeyDefine.network_address)
        vlan_ip = getStringArray(msg, ParamKeyDefine.ip)
        timestamp = getStringArray(msg, ParamKeyDefine.timestamp)
        domain = getStringArrayArray(msg, ParamKeyDefine.domain)
        domain_id = getStringArrayArray(msg, ParamKeyDefine.domain_id)
        ethernet_address = getStringArrayArray(msg, ParamKeyDefine.ethernet_address)
        network_device = getStringArrayArray(msg, ParamKeyDefine.network_device)
        result = []
        
        for index in range(len(name)):
            vlan = VlanStatus()
            vlan.name = name[index]
            vlan.server_room = server_room[index]
            vlan.computer_rack = computer_rack[index]
            vlan.node_name = node_name[index]
            vlan.fullname = "%s.%s.%s.%s"%(vlan.server_room, vlan.computer_rack,
                                           vlan.node_name, vlan.name)
            vlan.uuid = uuid[index]
            if 0 == actived[index]:
                vlan.actived = False
            else:
                vlan.actived = True
            vlan.ethernet_address = vlan_mac[index]
            vlan.ip = vlan_ip[index]
            vlan.members = []
            current_domain = domain[index]
            current_id = domain_id[index]
            current_mac = ethernet_address[index]
            current_dev = network_device[index]
            for i in range(len(current_domain)):
                vlan.members.append((current_domain[i],
                                     current_id[i],
                                     current_mac[i],
                                     current_dev[i]))

            vlan.timestamp = timestamp[index]
            result.append(vlan)

        return result

    @staticmethod
    def packToMessage(msg, data_list):
        node_name = []
        server_room = []
        computer_rack = []
        vlan_name = []
        network_id = []
        actived = []
        network_address = []
        ip = []
        domain = []
        domain_id = []
        ethernet_address = []
        network_device = []
        timestamp = []
        for vlan in data_list:
            vlan_name.append(vlan.name)
            network_id.append(vlan.uuid)
            network_address.append(vlan.ethernet_address)
            ip.append(vlan.ip)
            if vlan.actived:
                actived.append(1)
            else:
                actived.append(0)
            ##(domain, uuid, mac, dev)
            member_domain = []
            member_id = []
            member_mac = []
            member_dev = []
            for member in vlan.members:
                member_domain.append(member[0])
                member_id.append(member[1])
                member_mac.append(member[2])
                member_dev.append(member[3])
                
            domain.append(member_domain)
            domain_id.append(member_id)
            network_device.append(member_dev)
            ethernet_address.append(member_mac)
            node_name.append(vlan.node_name)
            server_room.append(vlan.server_room)
            computer_rack.append(vlan.computer_rack)
            
            timestamp.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
        msg.setStringArray(ParamKeyDefine.vlan, vlan_name)
        setStringArray(msg, ParamKeyDefine.network_id, network_id)
        setUIntArray(msg, ParamKeyDefine.actived, actived)
        setStringArray(msg, ParamKeyDefine.network_address, network_address)
        setStringArray(msg, ParamKeyDefine.ip, ip)
        setStringArrayArray(msg, ParamKeyDefine.domain, domain)
        setStringArrayArray(msg, ParamKeyDefine.domain_id, domain_id)
        setStringArrayArray(msg, ParamKeyDefine.ethernet_address, ethernet_address)
        setStringArrayArray(msg, ParamKeyDefine.network_device, network_device)
        
               
        setStringArray(msg , ParamKeyDefine.server_room, server_room)
        setStringArray(msg , ParamKeyDefine.computer_rack, computer_rack)            
        setStringArray(msg, ParamKeyDefine.node_name, node_name)
        
        setStringArray(msg, ParamKeyDefine.timestamp, timestamp)
        
if __name__ == "__main__":
    network_list = []
    network = VlanStatus()
    network.name = "default"
    network.members = [("spice01", "3fb5743d-2b3b-40d9-86f0-587f65d7738c", "52:54:00:e6:09:0a", ""),
                       ("spice02", "b0029e86-1a6c-4092-af6e-9b106567d242", "52:54:00:c4:52:56", "")]
    network_list.append(network)
    
    network = VlanStatus()
    network.name = "network-02"
    network.members = [("spice01", "3fb5743d-2b3b-40d9-86f0-587f65d7738c", "52:54:00:e6:09:0a", "")]

    network_list.append(network)

    msg = getRequest(11)
    VlanStatus.packToMessage(msg, network_list)
    print msg.params
    
    print "to message"
    content = msg.toString()
   
    print "from message"
    new_msg = AppMessage.fromString(content)
    print new_msg.params
    
    print "unpack message"
    new_list = VlanStatus.unpackFromMessage(new_msg)
    

    for network in new_list:
        print network.name, network.members
    

    
