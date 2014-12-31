#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *
from ts_format import *

class QueryServerTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.query_server"
        BaseTask.__init__(self, task_type, RequestDefine.query_server,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_server, result_success,
                             self.onQuerySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_server, result_fail,
                             self.onQueryFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.query_server)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        
        rack = param["rack"]        
        request.setString(ParamKeyDefine.rack, rack)
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onQuerySuccess(self, msg, session):
        self.clearTimer(session)
        name = msg.getStringArray(ParamKeyDefine.name)
        uuid = msg.getStringArray(ParamKeyDefine.uuid)
        status = msg.getUIntArray(ParamKeyDefine.status)
        ip = msg.getStringArray(ParamKeyDefine.ip)
        cpu_count = msg.getUIntArray(ParamKeyDefine.cpu_count)
        cpu_usage = msg.getFloatArray(ParamKeyDefine.cpu_usage)
        memory = msg.getUIntArrayArray(ParamKeyDefine.memory)
        memory_usage = msg.getFloatArray(ParamKeyDefine.memory_usage)
        disk_volume = msg.getUIntArrayArray(ParamKeyDefine.disk_volume)
        disk_usage = msg.getFloatArray(ParamKeyDefine.disk_usage)

        newstatus = ChangeResuleStatus(status,Status_server)
        new_cpu_usage = GetPresentValue(cpu_usage)
        new_memory_usage = GetPresentValue(memory_usage)
        new_disk_usage = GetPresentValue(disk_usage)

        newmemory = []
        for size in memory:
            newmemory.append(Change_Bit_to_Gb(size))
        newdisk=[]
        for disksize in disk_volume:
            newdisk.append(Change_Bit_to_Gb(disksize))

        self.info("[%08X]query server"%
                       (session.session_id))
        
        title = ['Name','UUID','CPU','CPU usage','Mem(GB)','Mem usage','Disk(GB)','Disk usage','Status','IP']
        print_test_result(title,name,uuid,cpu_count,new_cpu_usage,newmemory,new_memory_usage,newdisk,new_disk_usage,newstatus,ip)

        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onQueryFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query server fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onQueryTimeout(self, msg, session):
        self.info("[%08X]query server tiemout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
