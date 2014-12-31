#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class StartHostTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.start_host"
        BaseTask.__init__(self, task_type, RequestDefine.start_host,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.start_host, result_success,
                             self.onDeleteSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.start_host, result_fail,
                             self.onDeleteFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onDeleteTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.start_host)
        param = self.case_manager.getParam()
        session.target = param["host"]
        control_server = param["control_server"]
        iso_id = param["iso_id"]
        request.setString(ParamKeyDefine.uuid, param["host"])
        ##0 = boot from disk
        boot = int(param["boot"])
        #print boot
        request.setUInt(ParamKeyDefine.boot, boot)
        request.setString(ParamKeyDefine.image, iso_id)
        ##1 = boot from cdrom
##        request.setUInt(ParamKeyDefine.boot, 1)
##        request.setString(ParamKeyDefine.image, "86d60a42852a48919819121470075af7")
        
        self.info("[%08X]request start host '%s' to control server '%s'"%
                       (session.session_id, session.target, control_server))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onDeleteSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]start host success, id '%s'"%
                       (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onDeleteFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]start host fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onDeleteTimeout(self, msg, session):
        self.info("[%08X]start host timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
