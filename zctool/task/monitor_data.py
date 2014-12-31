#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class MonitorDataTask(BaseTask):
    operate_timeout = 20
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.monitor_data,
                          messsage_handler, logger_name)        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.monitor_data, result_success,
                             self.onRunSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.monitor_data, result_fail,
                             self.onRunFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRunTimeout)             

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.monitor_data)
        param = self.case_manager.getParam()
        control_server = param["control_server"]       
        level = int(param["monitor_level"])
        taskid = int(param["task_id"])
        
        request.setUInt(ParamKeyDefine.level, level)
        request.setUInt(ParamKeyDefine.task, taskid)
       
        self.info("[%08X]request start monitor '%s'"%
                       (session.session_id, storage_pool_name))
        session.target = storage_pool_name
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)

    def onRunSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]get monitor data success"%
                       (session.session_id))
        
        cpu_count = msg.getUIntArray(ParamKeyDefine.cpu_count)
        cpu_usage = msg.getFloatArray(ParamKeyDefine.cpu_usage)
        memory = msg.getUIntArrayArray(ParamKeyDefine.memory)
        memory_usage = msg.getFloatArray(ParamKeyDefine.memory_usage)
        disk_volume = msg.getUIntArrayArray(ParamKeyDefine.disk_volume)
        disk_usage = msg.getFloatArray(ParamKeyDefine.disk_usage)       
        disk_io = msg.getUIntArray(ParamKeyDefine.disk_io)
        network_io = msg.getUIntArray(ParamKeyDefine.network_io)
        speed = msg.getUIntArray(ParamKeyDefine.speed)
        name = msg.getStringArray(ParamKeyDefine.name)
        timestamp = msg.getStringArray(ParamKeyDefine.timestamp)
        count = msg.getUIntArray(ParamKeyDefine.count)
        
        #show query result
        #newstatus = ChangeResuleStatus(status,Status_storage_pool)
        title = ['Name','Speed','disk_io','Count']
        print_test_result(title,name,speed,disk_io,count)
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRunFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]get monitor data fail"%
                  (session.session_id))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRunTimeout(self, msg, session):
        self.info("[%08X]get monitor data timeout"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()

   
