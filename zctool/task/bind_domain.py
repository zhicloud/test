#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class BindDomainTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.bind_domain,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.bind_domain, result_success,
                             self.onRunSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.bind_domain, result_fail,
                             self.onRunFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRunTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.bind_domain)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        
        name = param["name"]
        dtype = param["type"]
        uuid  = param["uuid"]
        request.setString(ParamKeyDefine.uuid, uuid)
        
        request.setUInt(ParamKeyDefine.type, dtype)
        request.setString(ParamKeyDefine.name, name)        
        
        self.info("[%08X]request bind host '%s' to domain '%s'"%
                       (session.session_id, uuid, name))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onRunSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]bind domain success, id '%s'"%
                       (session.session_id, session.target))
        #print result
        ip = msg.getStringArray(ParamKeyDefine.ip)

        title = ['IP']
        print_test_result(title,ip)
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRunFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]bind domain fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRunTimeout(self, msg, session):
        self.info("[%08X]bind domain timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
