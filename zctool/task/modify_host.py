#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class ModifyHostTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.modify_host"
        BaseTask.__init__(self, task_type, RequestDefine.modify_host,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.modify_host, result_success,
                             self.onModifySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.modify_host, result_fail,
                             self.onModifyFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onModifyTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.modify_host)
        param = self.case_manager.getParam()
        uuid = param["host"]
        control_server = param["control_server"]

        cpu_count = int(param["cpu_core"])
        memory = int(param["memory_size"])*1024*1024
        auto_start = param["auto"]
        port = param["port"]
        display = "display_a"
        authentication = param["monitor_pwd"]
        network = param["network"]
        name = param["name"]

        inbound_bandwidth = int(int(param["inbound"])*1024*1024/8)
        outbound_bandwidth = int(int(param["outbound"])*1024*1024/8)

        
        request.setString(ParamKeyDefine.uuid, uuid)
        request.setString(ParamKeyDefine.name, name)
        request.setUInt(ParamKeyDefine.cpu_count, cpu_count)
        request.setUInt(ParamKeyDefine.memory, memory)
        if auto_start:
            request.setUIntArray(ParamKeyDefine.option, [1])
        else:
            request.setUIntArray(ParamKeyDefine.option, [0])
        request.setUIntArray(ParamKeyDefine.port, port)
        request.setString(ParamKeyDefine.display, display)
        request.setString(ParamKeyDefine.authentication, authentication)
        request.setString(ParamKeyDefine.network, network)
        request.setUInt(ParamKeyDefine.inbound_bandwidth, inbound_bandwidth)
        request.setUInt(ParamKeyDefine.outbound_bandwidth, outbound_bandwidth)
        
        self.info("[%08X]request modify host '%s'"%
                       (session.session_id, uuid))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onModifySuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]modify host success"%
                       (session.session_id))
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onModifyFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]modify host fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onModifyTimeout(self, msg, session):
        self.info("[%08X]modify host timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
