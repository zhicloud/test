#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class DeleteLoadBalancerTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.delete_load_balancer,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.delete_load_balancer, result_success,
                             self.onRunSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.delete_load_balancer, result_fail,
                             self.onRunFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRunTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.delete_load_balancer)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        
        uuid = param["uuid"] 
        request.setString(ParamKeyDefine.uuid, uuid)
             
        self.info("[%08X]request delete load banlancer '%s'"%
                       (session.session_id, uuid))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onRunSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]delete load banlancer success"%
                       (session.session_id))
        #print result
        ip = msg.getStringArray(ParamKeyDefine.ip)

        title = ['IP']
        print_test_result(title,ip)
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRunFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]delete load banlancer fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRunTimeout(self, msg, session):
        self.info("[%08X]delete load banlancer timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
