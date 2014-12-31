#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *
from ts_format import *

class QueryServerRoomTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.query_server_room"
        BaseTask.__init__(self, task_type, RequestDefine.query_server_room,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_server_room, result_success,
                             self.onQuerySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_server_room, result_fail,
                             self.onQueryFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.query_server_room)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
     
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onQuerySuccess(self, msg, session):
        self.clearTimer(session)
        name = msg.getStringArray(ParamKeyDefine.name)
        uuid = msg.getStringArray(ParamKeyDefine.uuid)
        status = msg.getUIntArray(ParamKeyDefine.status)
        server = msg.getUIntArrayArray(ParamKeyDefine.server)
        cpu_count = msg.getUIntArray(ParamKeyDefine.cpu_count)
        cpu_usage = msg.getFloatArray(ParamKeyDefine.cpu_usage)
        memory = msg.getUIntArrayArray(ParamKeyDefine.memory)
        memory_usage = msg.getFloatArray(ParamKeyDefine.memory_usage)
        disk_volume = msg.getUIntArrayArray(ParamKeyDefine.disk_volume)
        disk_usage = msg.getFloatArray(ParamKeyDefine.disk_usage)

        newstatus = ChangeResuleStatus(status,Status_server_room)
        new_cpu_usage = GetPresentValue(cpu_usage)
        new_memory_usage = GetPresentValue(memory_usage)
        new_disk_usage = GetPresentValue(disk_usage)

        newmemory = []
        for size in memory:
            newmemory.append(Change_Bit_to_Gb(size))
        newdisk=[]
        for disksize in disk_volume:
            newdisk.append(Change_Bit_to_Gb(disksize))

        newserver = []
        for server_status in server:
            newserver.append(ChangeResuleStatus(server_status,Status_server_room))

        count = len(uuid)
        self.info("[%08X]query server room success, %d room(s) available"%
                       (session.session_id, count))

        #show query result
        title = ['Name','UUID','Server','CPU','CPU usage','Mem(GB)','Mem usage','Disk(GB)','Disk usage','Status']
        print_test_result(title,name,uuid,newserver,cpu_count,new_cpu_usage,newmemory,new_memory_usage,newdisk,new_disk_usage,newstatus)
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onQueryFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query server room fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onQueryTimeout(self, msg, session):
        self.info("[%08X]query server room timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
