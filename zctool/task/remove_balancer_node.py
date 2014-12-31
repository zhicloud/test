#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class RemoveBalancerNodeTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.remove_balancer_node"
        BaseTask.__init__(self, task_type, RequestDefine.remove_balancer_node,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.remove_balancer_node, result_success,
                             self.onRemoveSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.remove_balancer_node, result_fail,
                             self.onRemoveFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRemoveTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.remove_balancer_node)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        balancer_id = param["balancer_id"]
        host_id = param["host_id"]
        hostlist = host_id.split(',')
        
        request.setString(ParamKeyDefine.uuid, balancer_id)
        request.setStringArray(ParamKeyDefine.host, hostlist)
        
        self.info("[%08X]request remove balancer node"%
                       (session.session_id))
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, param["control_server"])

    def onRemoveSuccess(self, msg, session):
        self.clearTimer(session)

        self.info("[%08X]remove balancer node success"%
                       (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRemoveFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]remove  balancer node fail"%
                  (session.session_id))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRemoveTimeout(self, msg, session):
        self.info("[%08X]remove balancer node timeout"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
