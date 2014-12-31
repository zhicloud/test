#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class RemoveStorageResourceTask(BaseTask):
    operate_timeout = 20
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.remove_storage_resource,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.remove_storage_resource, result_success,
                             self.onRunSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.remove_storage_resource, result_fail,
                             self.onRunFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRunTimeout)             

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.remove_storage_resource)
        param = self.case_manager.getParam()
        control_server = param["control_server"]       
        storage_pool_id = param["storage_pool_id"]
        storage_pool_name = param["name"]
        
        request.setString(ParamKeyDefine.pool, storage_pool_id)
        request.setString(ParamKeyDefine.name, storage_pool_name)
       
        self.info("[%08X]request remove storage resource '%s' from storage pool '%s'"%
                       (session.session_id, storage_pool_name, storage_pool_id))
        session.target = storage_pool_name
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)

    def onRunSuccess(self, msg, session):
        self.clearTimer(session)
        uuid = msg.getString(ParamKeyDefine.uuid)
        self.info("[%08X]remove storage resource success,name '%s'"%
                       (session.session_id,session.target))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRunFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]remove storage resource fail, name '%s'"%
                  (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRunTimeout(self, msg, session):
        self.info("[%08X]remove storage resource timeout, name '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()

   
