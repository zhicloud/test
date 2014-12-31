#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class DeleteAddressPoolTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.delete_host"
        BaseTask.__init__(self, task_type, RequestDefine.delete_address_pool,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.delete_address_pool, result_success,
                             self.onDeleteSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.delete_address_pool, result_fail,
                             self.onDeleteFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onDeleteTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.delete_address_pool)
        param = self.case_manager.getParam()
        pool_uuid=param["pool_uuid"]
        control_server = param["control_server"]
        request.setString(ParamKeyDefine.uuid, pool_uuid)
        self.info("[%08X]request delete address pool '%s' to control server '%s'"%
                       (session.session_id, pool_uuid, control_server))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onDeleteSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]delete address pool success"%
                       (session.session_id))
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onDeleteFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]delete address pool fail"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onDeleteTimeout(self, msg, session):
        self.info("[%08X]delete addresss pool timeout"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
