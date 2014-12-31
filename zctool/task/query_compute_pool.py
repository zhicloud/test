#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *
from ts_format import *

class QueryComputePool(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        ##logger_name = "task.query_compute_pool"
        BaseTask.__init__(self, task_type, RequestDefine.query_compute_pool,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_compute_pool, result_success,
                             self.onQuerySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_compute_pool, result_fail,
                             self.onQueryFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.query_compute_pool)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        self.info("[%08X]request query compute pool to control server '%s'"%
                       (session.session_id, control_server))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onQuerySuccess(self, msg, session):
        self.clearTimer(session)
        name = msg.getStringArray(ParamKeyDefine.name)
        uuid = msg.getStringArray(ParamKeyDefine.uuid)
        node = msg.getUIntArrayArray(ParamKeyDefine.node)
        host = msg.getUIntArrayArray(ParamKeyDefine.host)
        cpu_count = msg.getUIntArray(ParamKeyDefine.cpu_count)
        cpu_usage = msg.getFloatArray(ParamKeyDefine.cpu_usage)
        memory = msg.getUIntArrayArray(ParamKeyDefine.memory)
        memory_usage=msg.getFloatArray(ParamKeyDefine.memory_usage)
        disk_volume =msg.getUIntArrayArray(ParamKeyDefine.disk_volume) 
        disk_usage = msg.getFloatArray(ParamKeyDefine.disk_usage)
        status = msg.getUIntArray(ParamKeyDefine.status)
        count = len(uuid)
        self.info("[%08X]query compute pool SUCCESS, %d compute pool(s) available"%
                       (session.session_id, count))

        #show query result
        newstatus = ChangeResuleStatus(status,Stutus_compute_pool)
        title = ['Pool Name','UUID','Status']

        print_test_result(title,name,uuid,newstatus)
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onQueryFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query compute pool FAIL, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onQueryTimeout(self, msg, session):
        self.info("[%08X]query compute pool TIMEOUT, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
