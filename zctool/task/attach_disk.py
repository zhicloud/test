#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class AttachDiskTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.attach_disk"
        BaseTask.__init__(self, task_type, RequestDefine.attach_disk,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.attach_disk, result_success,
                             self.onAttachSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.attach_disk, result_fail,
                             self.onAttachFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onAttachTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.attach_disk)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        host = param["host"]
        session.target = param["host"]
        disk_volume = int(param["disk_volume"])*1024*1024*1024
        disk_type = int(param["disk_type"])
        disk_source = param["disk_source"]
        mode = int(param["mode"])

        request.setString(ParamKeyDefine.uuid, host)
        request.setUInt(ParamKeyDefine.disk_volume, disk_volume)
        request.setUInt(ParamKeyDefine.disk_type, disk_type)
        request.setString(ParamKeyDefine.disk_source, disk_source)
        request.setUInt(ParamKeyDefine.mode, mode)

       
        self.info("[%08X]request attach disk to host '%s' to control server '%s'"%
                       (session.session_id, session.target, control_server))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onAttachSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]attach disk to host(%s) success"%
                       (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onAttachFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]attach disk to host(%s) fail"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onAttachTimeout(self, msg, session):
        self.info("[%08X]attach disk to host(%s) timeout'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
