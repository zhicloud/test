#!/usr/bin/python
import threading
from datagram import *

class SendTask(object):    
    def __init__(self, task_id):
        self.task_id = task_id
        self.allocated = False
        self.data = ""
        self.address = None

    def allocate(self):
        self.allocated = True

    def deallocate(self):
        self.allocated = False
            
    def isAllocated(self):
        return self.allocated
                
    def initial(self, content, remote_address):
        if not self.allocated:
            return False
        datagram = Datagram(content, self.task_id)
        ##must change seq before serialize
        self.data = datagram.toString()
        self.address = remote_address
        return True
        
