#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *
from ts_format import *

class QueryForWarderSummaryTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.query_forwarder_summary,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_forwarder_summary, result_success,
                             self.onQuerySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_forwarder_summary, result_fail,
                             self.onQueryFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.query_forwarder_summary)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onQuerySuccess(self, msg, session):
        self.clearTimer(session)
        #name = msg.getStringArray(ParamKeyDefine.name)
        res_type = msg.getUIntArray(ParamKeyDefine.type)
        count = msg.getUIntArrayArray(ParamKeyDefine.count)
        #status = msg.getUIntArray(ParamKeyDefine.status)
        
        count = len(res_type)
        self.info("[%08X]query forwarder summary success, %d forwarder(s) available"%
                       (session.session_id, count))

        newtype = ChangeResuleStatus(res_type,Status_Forwarder_summary)
        
        title = ['Type','Count']
        print_test_result(title,newtype,count)

        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onQueryFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query forwarder summary fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onQueryTimeout(self, msg, session):
        self.info("[%08X]query forwarder summary timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
