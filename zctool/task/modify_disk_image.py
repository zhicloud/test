#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class ModifyDiskImageTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.modify_disk_image"
        BaseTask.__init__(self, task_type, RequestDefine.modify_disk_image,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.modify_disk_image, result_success,
                             self.onModifySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.modify_disk_image, result_fail,
                             self.onModifyFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onModifyTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.modify_disk_image)
        param = self.case_manager.getParam()
        session.target = param["host"]
        control_server = param["control_server"]
        new_name = param["disk_image_name"]
        new_desc = param["disk_image_description"]
        #new_name = "new_disk_image_name"
        #new_desc = "this is modified description"
        tags = param["tag"].split(',')
        #tags = ["linux", "64bit"]
        request.setString(ParamKeyDefine.uuid, session.target)
        request.setString(ParamKeyDefine.name, new_name)
        request.setString(ParamKeyDefine.description, new_desc)
        request.setStringArray(ParamKeyDefine.identity, tags)
        self.info("[%08X]request modify disk image '%s' to control server '%s'"%
                       (session.session_id, session.target, control_server))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onModifySuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]modify disk image success, id '%s'"%
                       (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onModifyFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]modify disk image fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onModifyTimeout(self, msg, session):
        self.info("[%08X]modify disk image timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
