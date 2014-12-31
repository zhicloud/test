#!/usr/bin/python
from state_define import *

class StateRule(object):
    def __init__(self, msg_type, msg_id, result_type, handler, new_state = state_finish):
        self.msg_type = msg_type
        self.msg_id = msg_id
        self.result_type = result_type
        self.new_state = new_state
        self.handler = handler

    def isMatch(self, msg):
        """
        is condition matched
        @return:True - matched
        """
        if msg.type != self.msg_type:
##            print "unmatched type", msg.type, self.msg_type
            return False
        if msg.id != self.msg_id:
##            print "unmatched id", msg.id, self.msg_id
            return False
        if result_any == self.result_type:
            return True
        elif msg.success and (result_success == self.result_type):
            return True
        elif (not msg.success ) and (result_fail == self.result_type):
            return True
        else:
##            print "unmatched result", msg.success, self.result_type
            return False

    def invoke(self, msg, session):
        if self.handler:
            self.handler(msg, session)
        
