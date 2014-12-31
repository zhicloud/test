#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class DeleteComputePoolTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager

        BaseTask.__init__(self, task_type, RequestDefine.delete_compute_pool,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.delete_compute_pool, result_success,
                             self.onDeletesuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.delete_compute_pool, result_fail,
                             self.onDeleteFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onDeleteTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.delete_compute_pool)
        param = self.case_manager.getParam()
        
        request.setString(ParamKeyDefine.uuid, param["uuid"])
        
        self.info("[%08X]request delete compute resource"%
                       (session.session_id))
        
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, param["control_server"])

    def onDeletesuccess(self, msg, session):
        self.clearTimer(session)

        self.info("[%08X]delete compute resource success, name '%s'"%
                       (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onDeleteFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]create compute resource fail, name '%s'"%
                  (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onDeleteTimeout(self, msg, session):
        self.info("[%08X]create compute resource timeout, name '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
