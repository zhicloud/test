#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class GetBoundDomainTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.get_bound_domain,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.get_bound_domain, result_success,
                             self.onRunSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.get_bound_domain, result_fail,
                             self.onRunFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRunTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.get_bound_domain)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        name = param["name"]
        request.setString(ParamKeyDefine.name, name)
        
        self.info("[%08X]request get bound domain,name is '%s'"%
                       (session.session_id,name))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onRunSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]get bound domain success, id '%s'"%
                       (session.session_id, session.target))
        #print result
        ip = msg.getStringArray(ParamKeyDefine.ip)
        htype = msg.getUIntArray(ParamKeyDefine.type)
        uuid = msg.getStringArray(ParamKeyDefine.uuid)

        ntype = ChangeResuleStatus(htype,Sturus_bound_domain)

        title = ['ip','Type','UUID']
        print_test_result(title,ip,ntype,uuid)
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRunFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]get bound domain fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRunTimeout(self, msg, session):
        self.info("[%08X]get bound domain timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
