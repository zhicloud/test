#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class AddComputeResourceTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.add_compute_resource"
        BaseTask.__init__(self, task_type, RequestDefine.add_compute_resource,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.add_compute_resource, result_success,
                             self.onAddSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.add_compute_resource, result_fail,
                             self.onAddFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onAddTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.add_compute_resource)
        param = self.case_manager.getParam()
        request.setString(ParamKeyDefine.pool, param["pool"])
        request.setString(ParamKeyDefine.name, param["resource"])
        self.info("[%08X]request add compute resource '%s' to pool '%s'"%
                       (session.session_id, param["resource"], param["pool"]))
        session.target = param["resource"]
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, param["control_server"])

    def onAddSuccess(self, msg, session):
        self.clearTimer(session)

        self.info("[%08X]add compute resource success, name '%s'"%
                       (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onAddFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]add compute resource fail, name '%s'"%
                  (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onAddTimeout(self, msg, session):
        self.info("[%08X]add compute resource timeout, name '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
