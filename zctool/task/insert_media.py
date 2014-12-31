#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class InsertMediaTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager):
        self.case_manager = case_manager
        logger_name = "task.insert_media"
        BaseTask.__init__(self, task_type, RequestDefine.insert_media,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.insert_media, result_success,
                             self.onDeleteSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.insert_media, result_fail,
                             self.onDeleteFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onDeleteTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.insert_media)
        param = self.case_manager.getParam()
        session.target = param["host"]
        control_server = param["control_server"]
        if param.has_key("iso"):
            image_id = param["iso"]
        else:
            image_id = "d3056d60590e4120b834f4323e93b21e"
            
        request.setString(ParamKeyDefine.uuid, session.target)
        request.setString(ParamKeyDefine.image, image_id)
        
        self.info("[%08X]request insert media '%s' into host '%s' to control server '%s'"%
                       (session.session_id, image_id,
                        session.target, control_server))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onDeleteSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]insert media success, id '%s'"%
                       (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onDeleteFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]insert media fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onDeleteTimeout(self, msg, session):
        self.info("[%08X]insert media timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
