#!/usr/bin/python
from collections import namedtuple

node_data = namedtuple("NodeData", "server_room, computer_rack, node_name, ip, version, status")
host_data = namedtuple("HostData", "server_room, computer_rack, node_name, hostname, ip, total_cpu_usage, memory_usage, disk_usage, status, timestamp, operation_system")
guest_domain_data = namedtuple("GuestDomainData", "server_room, computer_rack, node_name, name, ip, mac, total_cpu_usage, memory_usage, disk_usage, status, timestamp, operation_system")
