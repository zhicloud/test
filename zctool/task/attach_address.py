#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class AttachAddressTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.attach_address,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.attach_address, result_success,
                             self.onRunSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.attach_address, result_fail,
                             self.onRunFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRunTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.attach_address)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        
        uuid = param["uuid"]
        pool = param["pool"]
        btype = int(param["type"])
        count = int(param["count"])
        
        request.setString(ParamKeyDefine.uuid, uuid)
        request.setString(ParamKeyDefine.pool, pool)
        request.setUInt(ParamKeyDefine.type, btype)
        request.setUInt(ParamKeyDefine.count, count)
             
        self.info("[%08X]request attach address '%s'"%
                       (session.session_id, uuid))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onRunSuccess(self, msg, session):
        self.clearTimer(session)
        ip = msg.getStringArray(ParamKeyDefine.ip)
        self.info("[%08X]attach address success"%
                       (session.session_id))
        #print result        
        #title = ['IP']
        #print_test_result(title,ip)
        print ip
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRunFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]attach address fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRunTimeout(self, msg, session):
        self.info("[%08X]attach address, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
