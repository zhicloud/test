#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class EnableLoadBalancerTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.add_balancer_node"
        BaseTask.__init__(self, task_type, RequestDefine.enable_load_balancer,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.enable_load_balancer, result_success,
                             self.onEnableSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.enable_load_balancer, result_fail,
                             self.onEnableFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onEnableTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.add_balancer_node)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        balancer_id = param["balancer_id"]
        
        request.setString(ParamKeyDefine.uuid, balancer_id)
        self.info("[%08X]request enable load balancer node"%
                       (session.session_id))
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, param["control_server"])

    def onEnableSuccess(self, msg, session):
        self.clearTimer(session)

        self.info("[%08X]enable load balancer success"%
                       (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onEnableFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]enable load balancer fail"%
                  (session.session_id))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onEnableTimeout(self, msg, session):
        self.info("[%08X]enable load balancer timeout"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
