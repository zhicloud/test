#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class DeleteStoragePoolTask(BaseTask):
    operate_timeout = 20
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.delete_storage_pool,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.delete_storage_pool, result_success,
                             self.onCreateSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.delete_storage_pool, result_fail,
                             self.onCreateFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onCreateTimeout)             

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.delete_storage_pool)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        storage_pool_id = param["storage_pool_id"]

        request.setString(ParamKeyDefine.uuid, storage_pool_id)
       
        self.info("[%08X]request delete storage pool('%s') to control server '%s'"%
                       (session.session_id,storage_pool_id, control_server))
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)

    def onCreateSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]delete storage pool '%s' success"%
                       (session.session_id,session.target))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onCreateFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]delete storage pool '%s' fail"%
                  (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onCreateTimeout(self, msg, session):
        self.info("[%08X]delete storage pool '%s' timeout"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()

   
