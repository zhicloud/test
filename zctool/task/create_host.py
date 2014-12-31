#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class CreateHostTask(BaseTask):
    operate_timeout = 20
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.create_host"
        BaseTask.__init__(self, task_type, RequestDefine.create_host,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.create_host, result_success,
                             self.onCreateSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.create_host, result_fail,
                             self.onCreateFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onCreateTimeout)        
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.ack, result_any,
                             self.onCreateStart, state_initial)        
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.report, result_any,
                             self.onCreateProgress, state_initial)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.create_host)
        param = self.case_manager.getParam()
        control_server = param["control_server"]       
        
        ##build from image
        host_name = param["host_name"]
        cpu_count = int(param["cpu_core"])
        memory = int(param["memory_size"])*1024*1024
        system_disk = int(param["system_disk_size"])*1024*1024*1024

        data_disk = int(param["data_disk_size"])*1024*1024*1024
        use_image = param["use_image"]
        image_id = param["image_id"]
        user_data_disk = param["user_data_disk"]
        auto_start = param["auto_start"]
        
        disk_volume = [system_disk]
        if user_data_disk == True:
            disk_volume.append(data_disk)

        port = param["port"]
        user = "akumas"
        group = "admin"
        display = "zhiuser"
        #Get monitor_pwd
        authentication = param["monitor_pwd"]
        network = ""
        inbound_bandwidth = int(int(param["inbound_bandwidth"])*1024*1024/8)
        outbound_bandwidth = int(int(param["inbound_bandwidth"])*1024*1024/8)

        request.setString(ParamKeyDefine.pool, param["pool"])
        request.setString(ParamKeyDefine.name, host_name)
        request.setUInt(ParamKeyDefine.cpu_count, cpu_count)
        request.setUInt(ParamKeyDefine.memory, memory)
        option = []
        if use_image:
            option.append(1)
        else:
            option.append(0)

        if user_data_disk:
            option.append(1)
        else:
            option.append(0)

        if auto_start:
            option.append(1)
        else:
            option.append(0)
        
        request.setUIntArray(ParamKeyDefine.option, option)
        request.setString(ParamKeyDefine.image, image_id)
        request.setUIntArray(ParamKeyDefine.disk_volume, disk_volume)
        request.setUIntArray(ParamKeyDefine.port, port)

        request.setString(ParamKeyDefine.user, user)
        request.setString(ParamKeyDefine.group, group)
        request.setString(ParamKeyDefine.display, display)
        request.setString(ParamKeyDefine.authentication, authentication)
        request.setString(ParamKeyDefine.network, network)

        request.setUInt(ParamKeyDefine.inbound_bandwidth, inbound_bandwidth)
        request.setUInt(ParamKeyDefine.outbound_bandwidth, outbound_bandwidth)
        
        self.info("[%08X]request create host '%s' to control server '%s'"%
                       (session.session_id, host_name, control_server))
        session.target = host_name
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)

    def onCreateSuccess(self, msg, session):
        self.clearTimer(session)
        uuid = msg.getString(ParamKeyDefine.uuid)
        param = self.case_manager.getParam()
        param["host" ] = uuid
        self.info("[%08X]create host success, name '%s'('%s')"%
                       (session.session_id, session.target, uuid))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onCreateFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]create host fail, name '%s'"%
                  (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onCreateTimeout(self, msg, session):
        self.info("[%08X]create host timeout, name '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()

    def onCreateStart(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]create host started"%
                  (session.session_id))
        self.setTimer(session, self.operate_timeout)

    def onCreateProgress(self, msg, session):
        self.clearTimer(session)
        progress = msg.getUInt(ParamKeyDefine.level)
        self.info("[%08X]create host process, %d %%"%
                  (session.session_id, progress))
        self.setTimer(session, self.operate_timeout)
