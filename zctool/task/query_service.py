#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *
from ts_format import *

class QueryServiceTask(BaseTask):
    operate_timeout = 20
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        ##logger_name = "task.query_service"
        BaseTask.__init__(self, task_type, RequestDefine.query_service,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_service, result_success,
                             self.onQuerySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_service, result_fail,
                             self.onQueryFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.query_service)
        param = self.case_manager.getParam()
        request.setUInt(ParamKeyDefine.type, param["type"])
        type=param["type"]
        request.setString(ParamKeyDefine.group, param["group"])
        group=param["group"]

        control_server = param["control_server"]
        self.info("[%08X]request query service to control server '%s'"%
                       (session.session_id, control_server))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onQuerySuccess(self, msg, session):
        self.clearTimer(session)
        name = msg.getStringArray(ParamKeyDefine.name)
        ip = msg.getStringArray(ParamKeyDefine.ip)
        port = msg.getUIntArray(ParamKeyDefine.port)
        status = msg.getUIntArray(ParamKeyDefine.status)
        count = len(name)
        self.info("[%08X]query service SUCCESS, %d service name(s) available"%
                       (session.session_id, count))

        #show query result
        newstatus = ChangeResuleStatus(status,Stutus_service_type)
        title = ['Service Name','IP','Port','Status']
        print_test_result(title,name,ip,port,newstatus)
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onQueryFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query service FAIL, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onQueryTimeout(self, msg, session):
        self.info("[%08X]query service TIMEOUT, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
