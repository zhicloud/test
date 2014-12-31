#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class ModifyISOImageTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.modify_iso_image"
        BaseTask.__init__(self, task_type, RequestDefine.modify_iso_image,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.modify_iso_image, result_success,
                             self.onModifySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.modify_iso_image, result_fail,
                             self.onModifyFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onModifyTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.modify_iso_image)
        param = self.case_manager.getParam()
        session.target = param["iso"]
        control_server = param["control_server"]
        new_name = param["iso_image_name"]
        new_desc = param["iso_image_description"]
        #print new_name
        #print new_desc
        #new_name = "new_iso_image_name"
        #new_desc = "this is modified description"
        request.setString(ParamKeyDefine.uuid, session.target)
        request.setString(ParamKeyDefine.name, new_name)
        request.setString(ParamKeyDefine.description, new_desc)
        self.info("[%08X]request modify iso image '%s' to control server '%s'"%
                       (session.session_id, session.target, control_server))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onModifySuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]modify iso image success, id '%s'"%
                       (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onModifyFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]modify iso image fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onModifyTimeout(self, msg, session):
        self.info("[%08X]modify iso image timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
