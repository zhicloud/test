#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class SetForwarderStatusTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.remove_compute_resource"
        BaseTask.__init__(self, task_type, RequestDefine.set_forwarder_status,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.set_forwarder_status, result_success,
                             self.onSetSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.set_forwarder_status, result_fail,
                             self.onSetFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onSetTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.set_forwarder_status)
        param = self.case_manager.getParam()
        uuid = param["id"]
        status = param["status"]
        
        request.setString(ParamKeyDefine.uuid, uuid)
        request.setUInt(ParamKeyDefine.status, status)

        self.info("[%08X]request set forwarder status,uuid is:: '%s'"%
                       (session.session_id, param["id"]))

        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, param["control_server"])

    def onSetSuccess(self, msg, session):
        self.clearTimer(session)

        self.info("[%08X]remove compute resource success, name '%s'"%
                       (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onSetFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]remove compute resource fail, name '%s'"%
                  (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onSetTimeout(self, msg, session):
        self.info("[%08X]remove compute resource timeout, name '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
