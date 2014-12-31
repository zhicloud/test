#!/usr/bin/python
class ServerConfig(object):
    def __init__(self, uuid = "", name = "", rack = ""):
        self.rack = rack
        self.uuid = uuid
        self.name = name
        self.mac = ""
        self.ip = ""
