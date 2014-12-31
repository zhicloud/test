#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class RemoveForwarderTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.remove_forwarder,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.remove_forwarder, result_success,
                             self.onRunSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.remove_forwarder, result_fail,
                             self.onRunFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRunTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.remove_forwarder)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        
        target = param["uuid"]
        htype = int(param["type"])
        fid  = param["fid"]

        request.setString(ParamKeyDefine.target, target)        
        request.setUInt(ParamKeyDefine.type, htype)
        request.setString(ParamKeyDefine.uuid, fid)
                             
        self.info("[%08X]remove forwarder host '%s' from forwarder:'%s'"%
                       (session.session_id, target, fid))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onRunSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]remove forwarder success, id '%s'"%
                       (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRunFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]remove forwarder fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRunTimeout(self, msg, session):
        self.info("[%08X]remove forwarder timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
