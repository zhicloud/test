#!/usr/bin/python
class CommandTypeEnum(object):
    write = 1
    read = 2
    data = 3
    finish = 4
    write_ack = 5
    read_ack = 6
    data_ack = 7
    ready = 8
    finish_ack = 9
    check = 10

class WhisperCommand(object):
    def __init__(self, command_type):
        self.type = command_type


class WriteCommand(WhisperCommand):
    def __init__(self, sender, size, block_size, strip_length, channel):
        WhisperCommand.__init__(self, CommandTypeEnum.write)
        self.sender = sender
        self.size = size
        self.block_size = block_size
        self.strip_length = strip_length
        self.channel = channel

class WriteAck(WhisperCommand):
    def __init__(self, sender, receiver, file_id, port_list):
        WhisperCommand.__init__(self, CommandTypeEnum.write_ack)
        self.sender = sender
        self.receiver = receiver
        self.file_id = file_id
        self.port_list = port_list

class Data(WhisperCommand):
    def __init__(self, sender, receiver, strip_id, block_id, size, crc, data):
        WhisperCommand.__init__(self, CommandTypeEnum.data)
        self.sender = sender
        self.receiver = receiver
        self.strip_id = strip_id
        self.block_id = block_id        
        self.size = size
        self.crc = crc        
        self.data = data        

class DataAck(WhisperCommand):
    def __init__(self, sender, strip_id, block_id):
        WhisperCommand.__init__(self, CommandTypeEnum.data_ack)
        self.sender = sender
        self.strip_id = strip_id
        self.block_id = block_id  

class Finish(WhisperCommand):
    def __init__(self, sender, receiver):
        WhisperCommand.__init__(self, CommandTypeEnum.finish)
        self.sender = sender
        self.receiver = receiver

class FinishAck(WhisperCommand):
    def __init__(self, sender):
        WhisperCommand.__init__(self, CommandTypeEnum.finish_ack)
        self.sender = sender        

class Check(WhisperCommand):
    def __init__(self):
        WhisperCommand.__init__(self, CommandTypeEnum.check)

class Read(WhisperCommand):
    def __init__(self, receiver, file_id, port_list):
        WhisperCommand.__init__(self, CommandTypeEnum.read)
        self.receiver = receiver
        self.file_id = file_id
        self.port_list = port_list
        
class ReadAck(WhisperCommand):
    def __init__(self, sender, receiver, size, block_size, strip_length):
        WhisperCommand.__init__(self, CommandTypeEnum.read_ack)
        self.sender = sender
        self.receiver = receiver
        self.size = size
        self.block_size = block_size
        self.strip_length = strip_length

class Ready(WhisperCommand):
    def __init__(self, sender):
        WhisperCommand.__init__(self, CommandTypeEnum.ready)
        self.sender = sender
        
