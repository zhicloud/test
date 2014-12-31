#!/usr/bin/python
##from transport.app_message_pb2 import *
##ControlMessage_

##from transport.app_message_pb2 import *
from transport.app_message import *
##AppMessage_

class DefaultValues:
    domain = "zhicloud"
    multicast_ip = "224.6.6.6"
    multicast_port = 5666
    service_pipe_path = "/tmp/pipe"

class NodeTypeDefine:
    invalid = 0
    data_server = 1
    control_server = 2
    node_client = 3
    storage_server = 4
    statistic_server = 5
    manage_terminal = 6
    http_gateway = 7
    data_index = 8
    data_node = 9
    storage_manager = 10
    storage_client = 11
    storage_portal = 12
    storage_object = 13
    intelligent_router = 14

class RequestDefine:
    invalid = 0
    """
    request/response id define
    """
    create_guest_domain = 1
    delete_guest_domain = 2
    start_guest_domain = 3
    stop_guest_domain = 4
    pause_guest_domain = 5
    resume_guest_domain = 6
    save_guest_domain = 7
    restore_guest_domain = 8
    create_network = 9
    delete_network = 10
    start_network = 11
    stop_network = 12
    """
    join/leave data server's domain
    """
    join_domain = 13
    leave_domain = 14
    """
    start/stop observe node status
    """
    start_observe_node = 15
    stop_observe_node = 16
    """
    start/stop moniter
    """
    start_monitor = 17
    stop_monitor = 18
    """
    query system config
    """
    query_server_room = 19
    query_computer_rack = 20
    query_node = 21
    load_config = 22
    """
    add/modify/remove room/rack/node
    """
    add_server_room = 23
    modify_server_room = 24
    remove_server_room = 25
    add_computer_rack = 26
    modify_computer_rack = 27
    remove_computer_rack = 28
    add_node = 29
    modify_node = 30
    remove_node = 31
    """
    query image, for storage server
    """
    query_disk_image = 32
    query_storage_file = 33
    """
    vm operation, for client
    """
    query_network = 34
    query_domain = 35
    modify_guest_domain = 36
    modify_network = 37

    """
    create/delete/modify iso image for storage server
    """
    create_iso = 38
    delete_iso = 39
    modify_iso = 40

    query_storage_service = 41

    """
    storage index node&data node
    """    
    add_snapshot_node = 42
    remove_snapshot_node = 43
    
    create_snapshot_pool = 44    
    delete_snapshot_pool = 45
    query_snapshot_pool = 46

    write_snapshot = 47
    read_snapshot = 48
    remove_snapshot = 49    
    restore_snapshot = 50
    query_snapshot = 51

    """
    statistic collect data
    """
    start_statistic = 52
    stop_statistic = 53

    query_operate_detail = 54
    query_operate_summary = 55
    query_service_detail = 56
    query_service_summary = 57

    reboot_guest_domain = 58
    reset_guest_domain = 59
    clone_guest_domain = 60
    migrate_guest_domain = 61
    restart_network = 62
    """
    host node control
    """
    start_node = 63
    reboot_node = 64
    stop_node = 65

    """
    connect/disconnect domain node
    """
    connect_node = 66
    disconnect_node = 67

    """
    storage
    ********************************************************
    """
    create_page_pile = 68
    delete_page_pile = 69
##    delete_storage_pool = 70
    flush = 71

    """
    logical device
    """
    query_device = 72
    create_device = 73
    delete_device = 74
    modify_device = 75
    extend_device = 76
    shrink_device = 77
    connect_device = 78
    disconnect_device = 79
    
    """
    pages
    """
    allocate_page = 80
    deallocate_page = 81
    load_page = 82
    update_page = 83
    get_page = 84
    write_page = 85
    read_page = 86
    query_page = 87

    """
    page data
    """
    suspend_device = 88
    resume_device = 89
    
    start_capture_page = 90
    stop_capture_page = 91
    
    """
    define for 2.0
    """

    """
    server&service
    """
    query_service_type = 92
    query_service_group = 93
    query_service = 94
    modify_service = 95
##    query_server_room = 19
    create_server_room = 97
##    modify_server_room = 24
    delete_server_room = 99
    
    query_server_rack = 100
    create_server_rack = 101
    modify_server_rack = 102
    delete_server_rack = 103

    query_server = 104
    add_server = 105
    modify_server = 106
    remove_server = 107

    start_observe = 108
    stop_observe = 109

    query_address_pool = 110
    create_address_pool = 111
    delete_address_pool = 112
    add_address_resource = 113
    remove_address_resource = 114
    query_address_resource = 115
    
    query_port_pool = 116
    create_port_pool = 117
    delete_port_pool = 118
    add_port_resource = 119
    remove_port_resource = 120
    query_port_resource = 121
    
    query_compute_pool = 122
    create_compute_pool = 123
    delete_compute_pool = 124
    add_compute_resource = 125
    remove_compute_resource = 126
    query_compute_resource = 127
    
    query_storage_pool = 128
    create_storage_pool = 129
    delete_storage_pool = 130
    add_storage_resource = 131
    remove_storage_resource = 132
    query_storage_resource = 133

    query_resource_pool = 134

    create_host = 135
    delete_host = 136
    modify_host = 137
    start_host = 138
    stop_host = 139
    restart_host = 140
    query_host = 141
    halt_host = 142
    """
    iso&disk storage 
    """
    query_iso_image = 143
    upload_iso_image = 144
    modify_iso_image = 145
    delete_iso_image = 146

##    query_disk_image = 32/147
    create_disk_image = 148
    delete_disk_image = 149
    modify_disk_image = 150
    read_disk_image = 151

    insert_media = 152
    change_media = 153
    eject_media = 154

    reboot_server = 155
    shutdown_server = 156
    query_whisper = 157
    query_application = 158
    query_resource_pool = 159
    query_struct = 160

    query_host_info = 161

    """
    forwarder
    """
    add_forwarder = 162
    modify_forwarder = 163
    remove_forwarder = 164
    set_forwarder_status = 165
    query_forwarder_summary = 166
    query_forwarder = 167
    get_forwarder = 168
    """
    load balancer
    """
    create_load_balancer = 169
    add_balancer_node = 170
    remove_balancer_node = 171
    modify_balancer_node = 172
    enable_load_balancer = 173
    disable_load_balancer = 174
    delete_load_balancer = 175
    query_balancer_summary = 176
    query_load_balancer = 177
    query_balancer_detail = 178
    get_load_balancer = 179
    add_load_balancer = 180
    update_balancer_node = 181
    remove_load_balancer = 182
    """
    domain binding
    """
    bind_domain = 183
    unbind_domain = 184
    query_domain_summary = 185
    query_domain_name = 186
    get_bound_domain = 187
    """
    pool
    """
    attach_address = 188
    detach_address = 189
    migrate_address_resource = 190
    migrate_port_resource = 191
    check_config = 192
    modify_compute_pool = 193
    modify_storage_pool = 194

    """
    dynamic disk in host
    """
    attach_disk = 195
    detach_disk = 196

    monitor_heart_beat = 197
    monitor_data = 198

    
    
    
class EventDefine:
    invalid = 0
    """
    event id define
    """
    channel_connected = 1
    channel_disconnected = 2
    node_initialed = 3
    vlan_initialed = 4
    domain_initialed = 5
    domain_status_changed = 6
    vlan_status_changed = 7
    domain_config_changed = 8
    domain_created = 9
    domain_removed = 10
    vlan_config_changed = 11
    vlan_created = 12
    vlan_removed = 13
    node_status_update = 14
    domain_status_update = 15
    vlan_status_update = 16
    client_config_update = 17
    monitor_data = 18
    timeout = 19
    keep_alive = 20
    monitor_heart_beat = 21
    statistic_data = 22
    service_available = 23
    service_check = 24
    session_check = 25
    report = 26
    ready = 27
    ack = 28
    finish = 29
    data = 30
    """
    define for 2.0
    """
    host_added = 31
    host_status_changed = 32
    host_removed = 33
    server_status = 34
    host_status = 35
    service_status_changed = 36
    service_update = 37
    page_stored = 38
    page_changed = 39
    terminate = 40

class ParamKeyDefine:
    """
    param key id
    """
    domain = 0
    node_name = 1
    node_type = 2
    ethernet_address = 3
    ip = 4
    port = 5
    hostname = 6
    guestname = 7
    version = 8
    count = 9
    cpu_count = 10
    total_cpu_usage = 11
    separate_cpu_usage = 12
    total_memory = 13
    available_memory = 14
    disk_device = 15
    disk_bus_type = 16
    disk_source = 17
    disk_used = 18
    disk_volume = 19
    total_volume = 20
    used_volume = 21
    read_request = 22
    read_bytes = 23
    write_request = 24
    write_bytes = 25
    io_error = 26
    read_speed = 27
    write_speed = 28
    network_device = 29
    received_bytes = 30
    recevied_packets = 31
    recevied_errors = 32
    received_drop = 33
    sent_bytes = 34
    sent_packets = 35
    sent_errors = 36
    sent_drop = 37
    received_speed = 38
    sent_speed = 39
    total_received_speed = 40
    total_sent_speed = 41
    timestamp = 42
    uuid = 43
    actived = 44
    status = 45
    network_address = 46
    network_id = 47
    name = 48
    vlan = 49
    server_room = 50
    computer_rack = 51
    level = 52
    task = 53
    memory_usage = 54
    disk_usage = 55
    operation_system = 56
    target = 57
    network = 58
    network_type = 59
    domain_id = 60
    display = 61
    description = 62
    identity = 63
    catalog = 64
    path = 65
    filename = 66
    netmask = 67
    bridge = 68
    dhcp = 69
    range_start = 70
    range_end = 71
    host_mac = 72
    host_ip = 73
    inbound_bandwidth = 74
    inbound_peak = 75
    inbound_burst = 76
    outbound_bandwidth = 77
    outbound_peak = 78
    outbound_burst = 79
    qos = 80
    auto_start = 81
    architecture = 82
    type = 83
    boot = 84
    file_type = 85
    network_source = 86
    disk_type = 87
    read_only = 88
    cdrom = 89
    upload_port = 90
    upload_address = 91
    replication = 92
    physical_node = 93
    virtual_node = 94
    begin = 95
    end = 96
    server = 97
    cpu_seconds = 98
    nat = 99
    size = 100
    pool = 101
    storage_pool = 102
    mode = 103
    allocate = 104
    encryption = 105
    raid = 106
    block = 107
    serial = 108
    zone = 109
    unit = 110
    device = 111
    page = 112
    pile = 113
    address = 114
    length = 115
    offset = 116
    data = 117
    verify = 118
    index = 119
    available = 120
    session = 121
    """
    define  for 2.0
    """
    
    group = 122
##    server = 123
    rack = 124
    room = 125
    server_name = 126
##    cpu_count = 10
    cpu_usage = 128
    memory = 129
##    memory_usage = 54/130
##    disk_volume = 19/131
##    disk_usage = 55/132
    disk_io = 133
    network_io = 134
    speed = 135
##    timestamp = 42/136
    user = 137
    authentication = 138
    option = 139
    image = 140
##    ip = 4/141
##    port = 5/142
##    inbound_bandwidth = 74/143
##    outbound_bandwidth = 77/144
    display_port = 145
##    nat = 99/146
    node = 147
    host = 148
    disk = 149
    terminal = 150
    iso_image = 151
    disk_image = 152
    range = 153
    forward = 154
    balance = 155
    security = 156
    crypt = 157
    snapshot = 158
    io = 159
    
    #storage
    identify = 160
    
"""
helper methods:
getRequest(id):
getResponse(id):
getEvent(id):

setInt(msg, key, value):
setUInt(msg, key, value):
setBool(msg, key, value):
setString(msg, key, value):
setFloat(msg, key, value):
setUIntArray(msg, key, value):
setStringArray(msg, key, value):
setFloatArray(msg, key, value):
setUIntArrayArray(msg, key, list_of_list):
setStringArrayArray(msg, key, list_of_list):
setFloatArrayArray(msg, key, list_of_list):

getInt(msg, key):
getUInt(msg, key):
getBool(msg, key):
getString(msg, key):
getFloat(msg, key):
getUIntArray(msg, key):
getFloatArray(msg, key):
getStringArray(msg, key):
getUIntArrayArray(msg, key):
getStringArrayArray(msg, key):
getFloatArrayArray(msg, key):


"""

def getRequest(id):
    req = AppMessage()
    req.id = id
    req.type = AppMessage.REQUEST
    return req

def getResponse(id):
    resp = AppMessage()
    resp.id = id
    resp.type = AppMessage.RESPONSE
    return resp

def getEvent(id):
    event = AppMessage()
    event.id = id
    event.type = AppMessage.EVENT
    return event

def setInt(msg, key, value):
    msg.setInt(key, value)

def setUInt(msg, key, value):
    msg.setUInt(key, value)
        
def setBool(msg, key, value):
    msg.setBool(key, value)
        
def setString(msg, key, value):
    msg.setString(key, value)

def setFloat(msg, key, value):
    msg.setFloat(key, value)
        
def setUIntArray(msg, key, value):
    msg.setUIntArray(key, value)

def setStringArray(msg, key, value):
    msg.setStringArray(key, value)

def setFloatArray(msg, key, value):
    msg.setFloatArray(key, value)

def setUIntArrayArray(msg, key, list_of_list):
    msg.setUIntArrayArray(key, list_of_list)

def setStringArrayArray(msg, key, list_of_list):
    msg.setStringArrayArray(key, list_of_list)    
        
def setFloatArrayArray(msg, key, list_of_list):
    msg.setFloatArrayArray(key, list_of_list)     
        
def getInt(msg, key):
    return msg.getInt(key)

def getUInt(msg, key):
    return msg.getUInt(key)

def getBool(msg, key):
    return msg.getBool(key)
    
def getString(msg, key):
    return msg.getString(key)
    
def getFloat(msg, key):
    return msg.getFloat(key)
    
def getUIntArray(msg, key):
    return msg.getUIntArray(key)

def getFloatArray(msg, key):
    return msg.getFloatArray(key)
    
def getStringArray(msg, key):
    return msg.getStringArray(key)

def getUIntArrayArray(msg, key):
    return msg.getUIntArrayArray(key)

def getStringArrayArray(msg, key):
    return msg.getStringArrayArray(key)
    
def getFloatArrayArray(msg, key):
    return msg.getFloatArrayArray(key)

if __name__ == "__main__":
##    ##self test
##    ##response with array
##    response = getResponse(RequestDefine.join_domain)
##    response.success = True
##    node_count = 5
##    setUInt(response, ParamKeyDefine.count, node_count)
##    names = []
##    types = []
##    usages = []
##    for i in range(node_count):
##        names.append("name_%d"%i)
##        types.append(i)
##        usages.append(float(i)/100)
##                    
##    setStringArray(response, ParamKeyDefine.node_name, names)
##    setUIntArray(response, ParamKeyDefine.node_type, types)
##    setFloatArray(response, ParamKeyDefine.total_cpu_usage, usages)
##
##    print getStringArray(response, ParamKeyDefine.node_name)
##    print getUIntArray(response, ParamKeyDefine.node_type)
##    print getFloatArray(response, ParamKeyDefine.total_cpu_usage)
##
##    ##event with array of array
##    event1 = getEvent(EventDefine.node_initialed)
##    uvalues = []
##    svalues = []
##    fvalues = []
##    for row in range(5):
##        u_row = []
##        s_row = []
##        f_row = []
##        for column in range(10):
##            u_row.append(row*20+column)
##            s_row.append("data_%d"%(row*20+column))
##            f_row.append(float(column)/100)
##
##        uvalues.append(u_row)
##        svalues.append(s_row)
##        fvalues.append(f_row)
##
##    setUIntArrayArray(event1, ParamKeyDefine.port, uvalues)
##    setStringArrayArray(event1, ParamKeyDefine.ip, svalues)
##    setFloatArrayArray(event1, ParamKeyDefine.separate_cpu_usage, fvalues)
##
##    print getUIntArrayArray(event1, ParamKeyDefine.port)
##    print getStringArrayArray(event1, ParamKeyDefine.ip)
##    print getFloatArrayArray(event1, ParamKeyDefine.separate_cpu_usage)
        
    import random
    import uuid
    import datetime
    import time
    import logging
    from data.machine_status import *
    from data.host_status import *
    from data.domain_status import *
    from service.time_util import *
    from transport.transport_command import *

    def generateMachineStatus(status, disk_count, network_count):
        status.cpu_count = int(random.random()*3)+1
        status.total_cpu_usage = random.random()*100
        status.separate_cpu_usage = []
        for i in range(status.cpu_count):
            status.separate_cpu_usage.append(random.random()*100)

        status.total_memory = int(random.random()*16*1024*1024*1024)
        status.memory_usage = random.random()*100
        status.available_memory = int(status.total_memory * status.memory_usage)
        status.disks = []
        for i in range(disk_count):
            used = int(random.random()*256*1024*1024*1024)
            status.disks.append(Disk("disk%d"%(i+1), "virtio", "hdx",
                              used, used + int(random.random()*256*1024*1024*1024)))

        status.total_volume = int(random.random()*512*1024*1024*1024)
        status.disk_usage = random.random()*100
        status.used_volume = int(status.total_volume * status.disk_usage)
        status.disk_statistic.rd_req = int(random.random()*1024*1024*1024)
        status.disk_statistic.rd_bytes = int(random.random()*1024*1024*1024)
        status.disk_statistic.wr_req = int(random.random()*1024*1024*1024)
        status.disk_statistic.wr_bytes = int(random.random()*1024*1024*1024)
        status.disk_statistic.io_error = int(random.random()*1024*1024*1024)
        status.disk_statistic.rd_speed = int(random.random()*1024*1024*1024)
        status.disk_statistic.wr_speed = int(random.random()*1024*1024*1024)

        status.networks = {}
        for i in range(network_count):
            mac = uuid.uuid4().hex
            statis = NetworkStatistic(int(random.random()*1024*1024*1024),
                                      int(random.random()*1024*1024*1024),
                                      int(random.random()*1024*1024*1024),
                                      int(random.random()*1024*1024*1024),
                                      int(random.random()*1024*1024*1024),
                                      int(random.random()*1024*1024*1024),
                                      int(random.random()*1024*1024*1024),
                                      int(random.random()*1024*1024*1024),
                                      int(random.random()*1024*1024*1024),
                                      int(random.random()*1024*1024*1024))
                                      
            status.networks[mac] = NetworkInterface("eth%d"%i, mac, "192.168.0.1",
                                                    0, statis)
            status.network_statistic += statis
        status.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status.operation_system = "linux2"
        
    def generateStatusData(domain_count):
        domain_list = []
        server_room = "server_room%d"%(random.random()*100)
        computer_rack = "computer_rack_%d"%(random.random()*1000)
        node_name = "node_%d"%(i+1)
        host = HostStatus()
        host.server_room = server_room
        host.computer_rack = computer_rack
        host.node_name = node_name
        host.hostname = "hostname_%d"%(random.random()*100)
        host.fullname = "%s.%s.%s"%(server_room, computer_rack, node_name)
        host.version = "1.0"
        generateMachineStatus(host, 2, 2)
        host.domains = []
        for j in range(domain_count):
            domain = DomainStatus()
            domain.server_room = server_room
            domain.computer_rack = computer_rack
            domain.node_name = node_name
            domain.name = "domain_%d"%(j + 1)
            domain.fullname = "%s.%s.%s.%s"%(server_room, computer_rack,
                                             node_name, domain.name)
            domain.uuid = uuid.uuid4().hex
            generateMachineStatus(domain, 2, 2)
            host.domains.append(domain.uuid)
            domain_list.append(domain)               
            
        return host, domain_list

    host_count = 500
    domain_per_host = 5
    host_messages = []
    domain_messages = []
    for i in range(host_count):
        host_status, domain_list = generateStatusData(domain_per_host)            

        host_event = getEvent(EventDefine.node_status_update)
        HostStatus.packToMessage(host_event, [host_status])
        host_messages.append(host_event)

        domain_event = getEvent(EventDefine.domain_status_update)
        DomainStatus.packToMessage(domain_event, domain_list)
        domain_messages.append(domain_event)

    length = 0
    elapse_list = []
    content_list = []
    print "start serialize AppMessage"
    for message in host_messages:
        begin = datetime.datetime.now()
        content = message.toString()
        content_list.append(content)
        length += len(content)
        elapse = elapsedMilliseconds(datetime.datetime.now() - begin)
        elapse_list.append(elapse)

    print "serialize %d message into %d bytes"%(len(content_list), length)
    print "total elapsed %.2f ms, avg %.3f ms, %.2f ms ~ %.2f ms"%(
        sum(elapse_list), sum(elapse_list)/len(elapse_list), min(elapse_list), max(elapse_list))
    
    length = 0
    elapse_list = []
    message_list = []
    print "start serialize MessageData"
    for content in content_list:
        begin = datetime.datetime.now()
        message_data = MessageData()
        message_data.serial = 1
        message_data.index = 1
        message_data.total = 1
        message_data.data = content

        message = message_data.toString()
        message_list.append(message)
        length += len(message)
        elapse = elapsedMilliseconds(datetime.datetime.now() - begin)
        elapse_list.append(elapse)

    print "package %d content into %d messages"%(
        len(content_list), len(message_list))
    print "total elapsed %.2f ms, avg %.3f ms, %.2f ms ~ %.2f ms"%(
        sum(elapse_list), sum(elapse_list)/len(elapse_list), min(elapse_list), max(elapse_list))

    elapse_list = []
    data_list = []
    print "start unserialize MessageData"
    for content in message_list:
        begin = datetime.datetime.now()
        messages = unpackageFromRawdata(content)
        data_list.extend(messages)
        elapse = elapsedMilliseconds(datetime.datetime.now() - begin)
        elapse_list.append(elapse)

    print "unpackage %d messages into %d datagrams"%(
        len(message_list), len(data_list))
    print "total elapsed %.2f ms, avg %.3f ms, %.2f ms ~ %.2f ms"%(
        sum(elapse_list), sum(elapse_list)/len(elapse_list), min(elapse_list), max(elapse_list))

    length = 0
    elapse_list = []
    message_list = []
    print "start unserialize AppMessage"
    for datagram in data_list:
        begin = datetime.datetime.now()
        message = AppMessage.fromString(datagram.data)
        message_list.append(message)
        elapse = elapsedMilliseconds(datetime.datetime.now() - begin)
        elapse_list.append(elapse)

    print "unpackage %d messages into %d datagrams"%(
        len(data_list), len(message_list))
    print "total elapsed %.2f ms, avg %.3f ms, %.2f ms ~ %.2f ms"%(
        sum(elapse_list), sum(elapse_list)/len(elapse_list), min(elapse_list), max(elapse_list))

    
