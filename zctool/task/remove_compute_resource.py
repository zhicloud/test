#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class RemoveComputeResourceTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.remove_compute_resource"
        BaseTask.__init__(self, task_type, RequestDefine.remove_compute_resource,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.remove_compute_resource, result_success,
                             self.onRemoveSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.remove_compute_resource, result_fail,
                             self.onRemoveFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRemoveTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.remove_compute_resource)
        param = self.case_manager.getParam()
##        param["pool"] = "353db275178a463283df2a31cd3679a5"
##        param["resource"] = "node_client_0050563c7a20"
        request.setString(ParamKeyDefine.pool, param["pool"])
        request.setString(ParamKeyDefine.name, param["resource"])
        self.info("[%08X]request remove compute resource '%s' to pool '%s'"%
                       (session.session_id, param["resource"], param["pool"]))
        session.target = param["resource"]
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, param["control_server"])

    def onRemoveSuccess(self, msg, session):
        self.clearTimer(session)

        self.info("[%08X]remove compute resource success, name '%s'"%
                       (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRemoveFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]remove compute resource fail, name '%s'"%
                  (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRemoveTimeout(self, msg, session):
        self.info("[%08X]remove compute resource timeout, name '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
