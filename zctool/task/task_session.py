#!/usr/bin/python
# -*- coding: utf-8 -*-
from transaction.base_session import *

class TaskSession(BaseSession):
    def reset(self):
        """
        reset session params,should override
        """
        BaseSession.reset(self)
        self.control_server = ""
        self.param = {}
        ##new added for 2.0
        self.target_list = []
        self.offset = 0
        self.total = 0
        self.target = ""
        self.task_id = 0
        self.remote_session = 0

        

