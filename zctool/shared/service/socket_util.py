#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import select
import random
"""
recv(socket, buf_size, timeout = 1)
@return:
success- True, content
fail- False, None
"""
def recv(receive_socket, buf_size, timeout = 1):
    incoming = [receive_socket]
    readable, writable, exceptional = select.select(incoming, [], incoming, timeout)
    if readable:
        try:
            content = receive_socket.recv(buf_size)
            return True, content
        except Exception:
            return False, None

    return False, None
"""
recvfrom(socket, buf_size, timeout = 1)
@return:
success- True, content, address
fail- False, None
"""
def recvfrom(receive_socket, buf_size, timeout = 1):
    incoming = [receive_socket]
    readable, writable, exceptional = select.select(incoming, [], incoming, timeout)
    if readable:
        try:
            content, address = receive_socket.recvfrom(buf_size)
            return True, content, address
        except Exception:
            return False, None, None

    return False, None, None

"""
sendto(send_socket, content, address, timeout = 1)
@return:
success- True, number_of_sent
fail- False, None
"""
def sendto(send_socket, content, address, timeout = 1):
    outcoming = [send_socket]
    readable, writable, exceptional = select.select([], outcoming, outcoming, timeout)
    if writable:
        try:
            count = send_socket.sendto(content, address)
            return True, count
        except Exception:
            return False, None

    return False, None

def getNetworkPrefix(ip, mask):
    values = []
    ip_values = ip.split(".")
    mask_values = mask.split(".")
    count = 0
    for i in range(4):
        check_value = int(mask_values[i])
        values.append(int(ip_values[i])&check_value)
        for j in range(8):
            if (check_value & (1 << j)) != 0:
                count += 1
        
    prefix = "%d.%d.%d.%d"%(values[0], values[1], values[2], values[3])
    ##prefix size
    return prefix, count

def getHostPart(ip, mask):
    values = []
    ip_values = ip.split(".")
    mask_values = mask.split(".")
    for i in range(4):
        values.append(int(ip_values[i])&(~int(mask_values[i])))
        
    host = "%d.%d.%d.%d"%(values[0], values[1], values[2], values[3])
    return host

def convertAddressToInt(ip):
    values = ip.split(".")
    result = 0
    for i in range(4):
        result |= int(values[i]) << (8*(3-i))
        
    return result

def convertIntToAddress(value):
    address = []
    for i in range(4):
        address.append( 0xFF&(value >> (8* (3-i))))

    return "%d.%d.%d.%d"%(address[0], address[1], address[2], address[3])

def generateMAC(lower = False):
    mac = ["00", "16", "3e"]
    mac.append("%02X"%(random.randint(0, 127)))
    mac.append("%02X"%(random.randint(0, 255)))
    mac.append("%02X"%(random.randint(0, 255)))
    if lower:
        return ":".join(mac).lower()
    else:
        return ":".join(mac).upper()
