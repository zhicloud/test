#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class QueryLoadBalancerTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.query_load_balancer,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_load_balancer, result_success,
                             self.onRunSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_load_balancer, result_fail,
                             self.onRunFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRunTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.query_load_balancer)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        
        btype  = param["type"]
        request.setUInt(ParamKeyDefine.type, btype)       
        
        self.info("[%08X]request query load balancer,uuid is '%s'"%
                       (session.session_id, uuid))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onRunSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query load balancer success, id '%s'"%
                       (session.session_id, session.target))
        #print result
        uuid = msg.getStringArray(ParamKeyDefine.uuid)
        ip = msg.getStringArrayArray(ParamKeyDefine.ip)
        host = msg.getStringArrayArray(ParamKeyDefine.host)
        name = msg.getStringArray(ParamKeyDefine.name)
        port = msg.getStringArrayArray(ParamKeyDefine.port)
        domain = msg.getStringArray(ParamKeyDefine.domain)

        nstatus = ChangeResuleStatus(status,Sturus_balancer_detail)

        title = ['Name','UUID','IP','Host','Port','Domain']
        print_test_result(title,name,uuid,ip,host,port,domain)
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRunFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query load balancer fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRunTimeout(self, msg, session):
        self.info("[%08X]query load balancer timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
