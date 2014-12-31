#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class ModifyBalancerNodeTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.modify_balancer_node"
        BaseTask.__init__(self, task_type, RequestDefine.modify_balancer_node,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.modify_balancer_node, result_success,
                             self.onModifySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.modify_balancer_node, result_fail,
                             self.onModifyFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onModifyTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.modify_balancer_node)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        balancer_id = param["balancer_id"]
        host_id = param["host_id"]
        server_ip = param["server_ip"]
        server_port = param["server_port"]
        
        request.setString(ParamKeyDefine.uuid, balancer_id)
        request.setString(ParamKeyDefine.host, host_id)
        request.setString(ParamKeyDefine.ip, server_ip)
        request.setUIntArray(ParamKeyDefine.port, server_port)
        self.info("[%08X]request modify balancer node"%
                       (session.session_id))
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, param["control_server"])

    def onModifySuccess(self, msg, session):
        self.clearTimer(session)

        self.info("[%08X]modify balancer node success"%
                       (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onModifyFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]modify balancer node fail"%
                  (session.session_id))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onModifyTimeout(self, msg, session):
        self.info("[%08X]modify balancer node timeout"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
