#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *
from ts_format import *

class QueryPortRescourceTask(BaseTask):
    operate_timeout = 10
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.query_port_resource,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_port_resource, result_success,
                             self.onQuerySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_port_resource, result_fail,
                             self.onQueryFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.query_port_resource)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        
        pool = param["pool"]
        
        request.setString(ParamKeyDefine.pool, pool)
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onQuerySuccess(self, msg, session):
        self.clearTimer(session)
        querydata = {}
                    
        ip = msg.getStringArray(ParamKeyDefine.ip)
        count = msg.getUIntArrayArray(ParamKeyDefine.count)
        status = msg.getUIntArray(ParamKeyDefine.status)

        newstatus = ChangeResuleStatus(status,Status_Port_Rescource)

        
        self.info("[%08X]query port resource info success" % (session.session_id))
        
        title = ['IP','Count','Status']
        print_test_result(ip,count,newstatus)

        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onQueryFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query port resource info fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onQueryTimeout(self, msg, session):
        self.info("[%08X]query port resource info timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
