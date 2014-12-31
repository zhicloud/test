#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class HaltHostTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.halt_host"
        BaseTask.__init__(self, task_type, RequestDefine.halt_host,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.halt_host, result_success,
                             self.onHaltSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.halt_host, result_fail,
                             self.onHaltFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onHaltTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.halt_host)
        param = self.case_manager.getParam()
        session.target = param["host"]
        control_server = param["control_server"]
        request.setString(ParamKeyDefine.uuid, param["host"])
        self.info("[%08X]request halt host '%s' to control server '%s'"%
                       (session.session_id, session.target, control_server))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onHaltSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]halt host success, id '%s'"%
                       (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onHaltFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]halt host fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onHaltTimeout(self, msg, session):
        self.info("[%08X]halt host timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
