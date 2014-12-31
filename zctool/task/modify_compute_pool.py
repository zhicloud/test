#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class ModifyComputePoolTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager

        BaseTask.__init__(self, task_type, RequestDefine.modify_compute_pool,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.modify_compute_pool, result_success,
                             self.onModifyuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.modify_compute_pool, result_fail,
                             self.onModifyFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onModifyTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.modify_compute_pool)
        param = self.case_manager.getParam()
        
        request.setString(ParamKeyDefine.uuid, param["uuid"])
        request.setString(ParamKeyDefine.name, param["name"])
        request.setUInt(ParamKeyDefine.network_type, int(param["network_type"]))
        request.setString(ParamKeyDefine.network, param["network"])
        request.setUInt(ParamKeyDefine.disk_type, int(param["disk_type"]))
        request.setString(ParamKeyDefine.disk_source, param["disk_source"])
        
        self.info("[%08X]request modify compute resource '%s'"%
                       (session.session_id, param["name"]))
        
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, param["control_server"])

    def onModifyuccess(self, msg, session):
        self.clearTimer(session)

        self.info("[%08X]modify compute resource success, name '%s'"%
                       (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onModifyFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]modify compute resource fail, name '%s'"%
                  (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onModifyTimeout(self, msg, session):
        self.info("[%08X]modify compute resource timeout, name '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
