#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class CreateComputePoolTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager

        BaseTask.__init__(self, task_type, RequestDefine.create_compute_pool,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.create_compute_pool, result_success,
                             self.onCreateSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.create_compute_pool, result_fail,
                             self.onCreateFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onCreateTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.create_compute_pool)
        param = self.case_manager.getParam()
        
        #request.setString(ParamKeyDefine.pool, param["pool"])
        request.setString(ParamKeyDefine.name, param["name"])
        request.setUInt(ParamKeyDefine.network_type, int(param["network_type"]))
        request.setString(ParamKeyDefine.network, param["network"])
        request.setUInt(ParamKeyDefine.disk_type, int(param["disk_type"]))
        request.setString(ParamKeyDefine.disk_source, param["disk_source"])
        
        self.info("[%08X]request create compute resource '%s'"%
                       (session.session_id, param["name"]))
        
        #session.target = param["resource"]
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, param["control_server"])

    def onCreateSuccess(self, msg, session):
        self.clearTimer(session)

        self.info("[%08X]create compute resource success, name '%s'"%
                       (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onCreateFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]create compute resource fail, name '%s'"%
                  (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onCreateTimeout(self, msg, session):
        self.info("[%08X]create compute resource timeout, name '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
