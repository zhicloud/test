#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class StopMonitorTask(BaseTask):
    operate_timeout = 20
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.create_host"
        BaseTask.__init__(self, task_type, RequestDefine.stop_monitor,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.stop_monitor, result_success,
                             self.onRunSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.stop_monitor, result_fail,
                             self.onRunFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRunTimeout)             

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.stop_monitor)
        param = self.case_manager.getParam()
        control_server = param["control_server"]       
        taskid = int(param["task_id"])
        
        request.setUInt(ParamKeyDefine.task, taskid)
       
        self.info("[%08X]request stop monitor '%d'"%
                       (session.session_id, taskid))
        #session.target = storage_pool_name
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)

    def onRunSuccess(self, msg, session):
        self.clearTimer(session)
        #uuid = msg.getUInt(ParamKeyDefine.task)
        self.info("[%08X]stop monitor success"%
                       (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRunFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]stop monitor fail"%
                  (session.session_id))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRunTimeout(self, msg, session):
        self.info("[%08X]stop monitor timeout"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()

   
