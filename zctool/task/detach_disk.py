#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class DetachDiskTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.detach_disk"
        BaseTask.__init__(self, task_type, RequestDefine.detach_disk,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.detach_disk, result_success,
                             self.onDetachSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.detach_disk, result_fail,
                             self.onDetachFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onDetachTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.detach_disk)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        host = param["host"]
        session.target = param["host"]
        index = int(param["index"])

        request.setString(ParamKeyDefine.uuid, host)
        request.setUInt(ParamKeyDefine.index, index)
       
        self.info("[%08X]request detach disk from host '%s' to control server '%s'"%
                       (session.session_id, session.target, control_server))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onDetachSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]detach disk from host(%s) success"%
                       (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onDetachFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]detach disk from host(%s) fail"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onDetachTimeout(self, msg, session):
        self.info("[%08X]detach disk from host(%s) timeout'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
