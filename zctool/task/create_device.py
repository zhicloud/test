#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class CreateDeviceTask(BaseTask):
    operate_timeout = 20
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.create_device"
        BaseTask.__init__(self, task_type, RequestDefine.create_device,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.create_device, result_success,
                             self.onCreateSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.create_device, result_fail,
                             self.onCreateFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onCreateTimeout)        
 

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.create_device)
        param = self.case_manager.getParam()
        control_server = param["control_server"]       
        
        ##build from image
        device_name = param["device_name"]
        pool = param["pool"]
        disk_volume = int(param["disk_volume"])*1024*1024*1024
        page_size = int(param["page_size"])*1024
        replic = int(param["replic"])
        disk_type = int(param["disk_type"])
        authen_user = param["authen_user"]
        authen_pwd = param["authen_pwd"]
        crypt = param["crypt"]
        ss_uuid = param["ss_uuid"]      
        authen = param["authen"]
        crypt_trans = param["crypt_trans"]
        cmp_trans = param["cmp_trans"]
        crypt_stor = param["crypt_stor"]
        cmp_stor = param["cmp_stor"]
        pre_alloc = param["pre_alloc"]

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
        if crypt_stor:
            option.append(1)
        else:
            option.append(0)

        if cmp_stor:
            option.append(1)
        else:
            option.append(0)

        if pre_alloc:
            option.append(1)
        else:
            option.append(0) 
        request.setString(ParamKeyDefine.name,device_name)
        request.setString(ParamKeyDefine.pool, pool)
        request.setUInt(ParamKeyDefine.disk_volume, disk_volume)
        request.setUInt(ParamKeyDefine.page,page_size)     
        request.setUInt(ParamKeyDefine.replication, replic)
        request.setUIntArray(ParamKeyDefine.option, option)
        request.setUInt(ParamKeyDefine.disk_type, disk_type)
        request.setString(ParamKeyDefine.user, authen_user)

        request.setString(ParamKeyDefine.authentication, authen_pwd)
        request.setString(ParamKeyDefine.crypt, crypt)
        request.setString(ParamKeyDefine.snapshot,ss_uuid)
        
        self.info("[%08X]request create device '%s' to control server '%s'"%
                       (session.session_id, device_name, control_server))
        session.target = device_name
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)

    def onCreateSuccess(self, msg, session):
        self.clearTimer(session)
        uuid = msg.getString(ParamKeyDefine.uuid)
        self.info("[%08X]create host success, name '%s'('%s')"%
                       (session.session_id, session.target, uuid))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onCreateFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]create device fail, name '%s'"%
                  (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onCreateTimeout(self, msg, session):
        self.info("[%08X]create device timeout, name '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()

