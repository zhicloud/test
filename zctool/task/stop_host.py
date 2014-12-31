#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class StopHostTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.stop_host"
        BaseTask.__init__(self, task_type, RequestDefine.stop_host,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.stop_host, result_success,
                             self.onStopSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.stop_host, result_fail,
                             self.onStopFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onStopTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.stop_host)
        param = self.case_manager.getParam()
        session.target = param["host"]
        control_server = param["control_server"]
        request.setString(ParamKeyDefine.uuid, param["host"])
        self.info("[%08X]request stop host '%s' to control server '%s'"%
                       (session.session_id, session.target, control_server))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onStopSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]stop host success, id '%s'"%
                       (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onStopFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]stop host fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onStopTimeout(self, msg, session):
        self.info("[%08X]stop host timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
