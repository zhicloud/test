#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *
from ts_format import *

class QuerystorageResourceTask(BaseTask):
    operate_timeout = 20
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.query_storage_resource,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_storage_resource, result_success,
                             self.onRunSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_storage_resource, result_fail,
                             self.onRunFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRunTimeout)             

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.query_storage_resource)
        param = self.case_manager.getParam()
        control_server = param["control_server"]       
        storage_pool_id = param["storage_pool_id"]
        
        request.setString(ParamKeyDefine.pool, storage_pool_id)
       
        self.info("[%08X]request query storage resource '%s'"%
                       (session.session_id, storage_pool_id))
        session.target = storage_pool_id
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)

    def onRunSuccess(self, msg, session):
        self.clearTimer(session)
        
        name = msg.getStringArray(ParamKeyDefine.name)
        cpu_count = msg.getUIntArray(ParamKeyDefine.cpu_count)
        cpu_usage = msg.getFloatArray(ParamKeyDefine.cpu_usage)
        memory = msg.getUIntArrayArray(ParamKeyDefine.memory)
        memory_usage = msg.getFloatArray(ParamKeyDefine.memory_usage)
        disk_volume = msg.getUIntArrayArray(ParamKeyDefine.disk_volume)
        disk_usage = msg.getFloatArray(ParamKeyDefine.disk_usage)       
        status = msg.getUIntArray(ParamKeyDefine.status)
        ip = msg.getStringArray(ParamKeyDefine.ip)

        count = len(name)
        self.info("[%08X]query storage pool success, %d pool(s) available"%
                       (session.session_id, count))

        #show query result
        newstatus = ChangeResuleStatus(status,Status_storage_pool)
        title = ['Name','CPU','Memory','Disk','IP','Status']
        print_test_result(title,name,cpu_count,memory,disk_volume,ip,newstatus)
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRunFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query storage resource fail, name '%s'"%
                  (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRunTimeout(self, msg, session):
        self.info("[%08X]query storage resource timeout, name '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()

   
