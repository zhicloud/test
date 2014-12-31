#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *
from ts_format import *

class QueryHostTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.query_host"
        BaseTask.__init__(self, task_type, RequestDefine.query_host,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_host, result_success,
                             self.onQuerySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_host, result_fail,
                             self.onQueryFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.query_host)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        
        pool_id = param["pool"]
        #authentication = "123456"
        #optional parameter
        host_disk_size = int(param["disk_size"])*1024*1024*1024
        disk_image = param["disk_image_uuid"]
        auto_start = param["auto"]
        port = param["port"]
        inbound_bandwidth = int(int(param["inbound"]) *1024*1024/8)
        outbound_bandwidth = int(int(param["outbound"]) *1024*1024/8)

              
        request.setString(ParamKeyDefine.pool, pool_id)

        request.setString(ParamKeyDefine.image, disk_image)

        #auto start
        if auto_start:
            request.setUIntArray(ParamKeyDefine.option, [1])
        else:
            request.setUIntArray(ParamKeyDefine.option, [0])
        request.setUIntArray(ParamKeyDefine.port, port)
        request.setUInt(ParamKeyDefine.inbound_bandwidth, inbound_bandwidth)
        request.setUInt(ParamKeyDefine.outbound_bandwidth, outbound_bandwidth)
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onQuerySuccess(self, msg, session):
        self.clearTimer(session)
        name = msg.getStringArray(ParamKeyDefine.name)
        uuid = msg.getStringArray(ParamKeyDefine.uuid)
        cpu_count = msg.getUIntArray(ParamKeyDefine.cpu_count)
        cpu_usage = msg.getFloatArray(ParamKeyDefine.cpu_usage)
        memory = msg.getUIntArray(ParamKeyDefine.memory)
        memory_usage = msg.getFloatArray(ParamKeyDefine.memory_usage)
        disk_volume = msg.getUIntArrayArray(ParamKeyDefine.disk_volume)
        disk_usage = msg.getFloatArray(ParamKeyDefine.disk_usage)
        ip = msg.getStringArrayArray(ParamKeyDefine.ip)
        status = msg.getUIntArray(ParamKeyDefine.status)

        newstatus = ChangeResuleStatus(status,Stutus_host)
        new_cpu_usage = GetPresentValue(cpu_usage)
        new_memory_usage = GetPresentValue(memory_usage)
        new_disk_usage = GetPresentValue(disk_usage)
        
        count = len(uuid)
        self.info("[%08X]query host success, %d host(s) available"%
                       (session.session_id, count))
        
        title = ['Host Name','UUID','CPU','CPU usage','Mem usage','Disk usage','IP','Status']
        print_test_result(title,name,uuid,cpu_count,new_cpu_usage,new_memory_usage,new_disk_usage,ip,newstatus)

        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onQueryFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query host fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onQueryTimeout(self, msg, session):
        self.info("[%08X]query host timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
