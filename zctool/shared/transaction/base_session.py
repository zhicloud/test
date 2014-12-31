#!/usr/bin/python
from state_define import *

class BaseSession(object):
    session_id = 0
    task_type = 0
    is_used = False
    current_state = 0
    initial_message = None
    request_module = ""
    request_session = 0
    timer_id = 0
    def __init__(self, session_id):
        self.session_id = session_id
        self.reset()

    def reset(self):
        """
        reset session params,should override
        """
        self.task_type = 0
        self.is_used = False
        self.current_state = 0
        self.request_module = ""
        self.request_session = 0
        self.timer_id = 0
        self.initial_message = None
        self.state_specified = False

    def occupy(self, task_type):
        self.task_type = task_type
        self.is_used = True
        return True
    
    def initial(self, msg):
        """
        initial session message,should override
        """
        self.initial_message = msg
        self.current_state = state_initial
        self.request_session = msg.session
        self.request_module = msg.sender

    def isFinished(self):
        return (state_finish == self.current_state)

    def finish(self):
        self.current_state = state_finish

    def setState(self, new_state):
        self.current_state = new_state
        self.state_specified = True
        

        

