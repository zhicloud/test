#!/usr/bin/python

class PhysicalPage(object):
    status_idle = 0
    status_allocate = 1
    status_dirty = 2
    status_suspend = 3

    def __init__(self):
        self.id = 0
        self.pile = 0
        self.version = 0
        self.data = []
        self.page_size = 0
        self.device = ""
        self.block = 0
        self.page = 0
        self.status = PhysicalPage.status_idle
        self.crc = 0
        
