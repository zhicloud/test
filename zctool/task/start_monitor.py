#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class StartMonitorTask(BaseTask):
    operate_timeout = 20
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.create_host"
        BaseTask.__init__(self, task_type, RequestDefine.start_monitor,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.start_monitor, result_success,
                             self.onRunSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.start_monitor, result_fail,
                             self.onRunFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRunTimeout)             

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.start_monitor)
        param = self.case_manager.getParam()
        control_server = param["control_server"]       
        level = int(param["monitor_level"])
        storage_pool_name = param["storage_pool_name"]
        
        request.setUInt(ParamKeyDefine.level, level)
        request.setString(ParamKeyDefine.name, storage_pool_name)
       
        self.info("[%08X]request start monitor '%s'"%
                       (session.session_id, storage_pool_name))
        session.target = storage_pool_name
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)

    def onRunSuccess(self, msg, session):
        self.clearTimer(session)
        uuid = msg.getUInt(ParamKeyDefine.task)
        self.info("[%08X]start monitor success,task id '%d'"%
                       (session.session_id,uuid))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRunFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]start monitor fail, name '%s'"%
                  (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRunTimeout(self, msg, session):
        self.info("[%08X]start monitor timeout, name '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()

   
