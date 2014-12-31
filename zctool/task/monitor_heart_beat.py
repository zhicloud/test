#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class MonitorHeartBeatTask(BaseTask):
    operate_timeout = 20
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.monitor_heart_beat,
                          messsage_handler, logger_name) 
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.monitor_heart_beat, result_success,
                             self.onRunSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.monitor_heart_beat, result_fail,
                             self.onRunFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRunTimeout)             

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.monitor_heart_beat)
        param = self.case_manager.getParam()
        control_server = param["control_server"]       
        taskid = int(param["task_id"])

        request.setUInt(ParamKeyDefine.task, task_id)
       
        self.info("[%08X]request monitor heart beat '%d'"%
                       (session.session_id, taskid))
        #session.target = storage_pool_name
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)

    def onRunSuccess(self, msg, session):
        self.clearTimer(session)
        uuid = msg.getUInt(ParamKeyDefine.task)
        self.info("[%08X]monitor heart beat success"%
                       (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRunFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]monitor heart beat fail"%
                  (session.session_id))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRunTimeout(self, msg, session):
        self.info("[%08X]monitor heart beat timeout"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()

   
