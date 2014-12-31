#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class ModifyDeviceTask(BaseTask):
    operate_timeout = 20
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.modify_device"
        BaseTask.__init__(self, task_type, RequestDefine.modify_device,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.modify_device, result_success,
                             self.onModifySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.modify_device, result_fail,
                             self.onModifyFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onModifyTimeout)        
 

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.modify_device)
        param = self.case_manager.getParam()
        control_server = param["control_server"]       
        
        ##build from image
        device_name = param["device_name"]
        uuid = param["device"]
        disk_type = int(param["disk_type"])
        authen_user = param["authen_user"]
        authen_pwd = param["authen_pwd"]
        ss_uuid = param["ss_uuid"]      
        authen = param["authen"]
        crypt_trans = param["crypt_trans"]
        cmp_trans = param["cmp_trans"]

        option = []
        if authen:
            option.append(1)
        else:
            option.append(0)

        if crypt_trans:
            option.append(1)
        else:
            option.append(0)

        if cmp_trans:
            option.append(1)
        else:
            option.append(0)        
 
        request.setString(ParamKeyDefine.name,device_name)
        request.setString(ParamKeyDefine.uuid, uuid)
        request.setUIntArray(ParamKeyDefine.option, option)
        request.setUInt(ParamKeyDefine.disk_type, disk_type)
        request.setString(ParamKeyDefine.user, authen_user)
        request.setString(ParamKeyDefine.authentication, authen_pwd)
        request.setString(ParamKeyDefine.snapshot,ss_uuid)
        
        self.info("[%08X]request modify device '%s' to control server '%s'"%
                       (session.session_id, device_name, control_server))
        session.target = device_name
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)

    def onModifySuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]modify host success, name '%s'"%
                       (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onModifyFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]modify device fail, name '%s'"%
                  (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onModifyTimeout(self, msg, session):
        self.info("[%08X]modify device timeout, name '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()

