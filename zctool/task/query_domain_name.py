#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class QueryDomainNameTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.query_domain_name,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_domain_name, result_success,
                             self.onRunSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_domain_name, result_fail,
                             self.onRunFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRunTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.query_domain_name)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        ip = param["ip"]
        request.setString(ParamKeyDefine.ip, ip)
        
        self.info("[%08X]request query domain name,ip is '%s'"%
                       (session.session_id,ip))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onRunSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query domain name success, id '%s'"%
                       (session.session_id, session.target))
        #print result
        name = msg.getStringArray(ParamKeyDefine.name)
        htype = msg.getUIntArray(ParamKeyDefine.type)
        uuid = msg.getStringArrayArray(ParamKeyDefine.uuid)
        host = msg.getStringArrayArray(ParamKeyDefine.host)

        ntype = ChangeResuleStatus(htype,Sturus_bind_domain)

        title = ['Name','Type','UUID','Host']
        print_test_result(title,name,ntype,uuid,host)
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRunFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query domain name fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRunTimeout(self, msg, session):
        self.info("[%08X]query domain name timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
