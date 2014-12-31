#!/usr/bin/python

class Service(object):
    status_running = 0
    status_warning = 1
    status_error = 2
    status_stop = 3
    
    def __init__(self):
        self.name = ""
        self.type = 0
        self.group = ""
        self.ip = ""
        self.port = 0
        self.version = ""
        self.status = Service.status_stop
        self.server = ""
        self.rack = ""
        self.server_name = ""

    def isRunning(self):
        return (self.status == Service.status_running)
