#!/usr/bin/python

from service.logger_helper import *
from service.message_define import *
from state_define import *
from state_rule import *

class BaseTask(LoggerHelper):
    message_handler = None
    def __init__(self, task_type, resp_msg, message_handler, logger_name):
        LoggerHelper.__init__(self, logger_name)
        self.state_map = {}
        self.state_map[state_initial] = []
        self.message_handler = message_handler
        self.message_id = resp_msg
        self.task_type = task_type        

    def initialSession(self, msg, session):
        session.initial(msg)

    def invokeSession(self, session):
        """
        task start, must override
        """
        raise Exception, "must override BaseTask::invokeSession"
        pass

    def processMessage(self, msg, session):
        state = session.current_state
        if not self.state_map.has_key(state):
            self.warn("task %d:no rule for state %d"%(self.task_type, state))
            return
        for rule in self.state_map[state]:
            if rule.isMatch(msg):
                rule.handler(msg, session)
                ##ignore fail/finished task
                if state_finish != session.current_state:
                    if session.state_specified:
                        ##specified
                        session.state_specified = False
                    else:
                        ##transfer to next state
                        session.current_state = rule.new_state

                return

        self.warn("task %d:no rule for state %d, message(%d)"%(self.task_type, state, msg.id))

    def sendMessage(self, msg, receiver):
        if self.message_handler:
            self.message_handler.sendMessage(msg, receiver)
            
    def sendMessageToSelf(self, msg):
        if self.message_handler:
            self.message_handler.sendMessageToSelf(msg)
            
    def sendToDomainServer(self, msg):
        if self.message_handler:
            self.message_handler.sendToDomainServer(msg)
            
    def setTimer(self, session, interval):
        if self.message_handler:
            session.timer_id = self.message_handler.setTimer(interval, session.session_id)

    def clearTimer(self, session):
        if self.message_handler and 0 != session.timer_id:
            self.message_handler.clearTimer(session.timer_id)
            session.timer_id = 0
        
    def taskFail(self, session):
        response = getResponse(self.message_id)
        response.session = session.request_session
        response.success = False
        session.finish()
        self.sendMessage(response, session.request_module)

    def reportFail(self, session):
        response = getResponse(self.message_id)
        response.session = session.request_session
        response.success = False
        self.sendMessage(response, session.request_module)

    def addState(self, state ):
        if not self.state_map.has_key(state):
            self.state_map[state] = []

    def addTransferRule(self, state, msg_type, msg_id, result_type, handler, new_state = state_finish):
        rule = StateRule(msg_type, msg_id, result_type, handler, new_state)
        if not self.state_map.has_key(state):
            self.state_map[state] = [rule]
        else:
            self.state_map[state].append(rule)
        
