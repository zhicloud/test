#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class RestartHostTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.restart_host"
        BaseTask.__init__(self, task_type, RequestDefine.restart_host,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.restart_host, result_success,
                             self.onRestartSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.restart_host, result_fail,
                             self.onRestartFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRestartTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.restart_host)
        param = self.case_manager.getParam()
        session.target = param["host"]
        control_server = param["control_server"]
        startup_mode=int(param["mode"])
        image=param["image"]
        request.setString(ParamKeyDefine.uuid, param["host"])
        request.setUInt(ParamKeyDefine.boot, startup_mode)
        request.setString(ParamKeyDefine.image, image)
        self.info("[%08X]request restart host '%s' to control server '%s'"%
                       (session.session_id, session.target, control_server))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onRestartSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]restart host success, id '%s'"%
                       (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRestartFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]restart host fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRestartTimeout(self, msg, session):
        self.info("[%08X]restart host timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
