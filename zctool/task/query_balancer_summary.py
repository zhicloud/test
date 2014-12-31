#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class QueryBalancerSummaryTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.query_balancer_summary,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_balancer_summary, result_success,
                             self.onRunSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_balancer_summary, result_fail,
                             self.onRunFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRunTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.query_balancer_summary)
        param = self.case_manager.getParam()
        control_server = param["control_server"]     
        
        self.info("[%08X]request query balancer summary"%
                       (session.session_id))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onRunSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query balancer summary success"%
                       (session.session_id))
        #print result
        htype = msg.getUIntArray(ParamKeyDefine.type)
        count = msg.getStringArrayArray(ParamKeyDefine.count)

        ntype = ChangeResuleStatus(htype,Sturus_balancer_summary)

        title = ['Type','Count']
        print_test_result(title,ntype,count)
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRunFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query balancer summary fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRunTimeout(self, msg, session):
        self.info("[%08X]query balancer summary timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
