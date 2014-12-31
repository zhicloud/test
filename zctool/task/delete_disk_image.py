#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class DeleteDiskImageTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.delete_disk_image"
        BaseTask.__init__(self, task_type, RequestDefine.delete_disk_image,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.delete_disk_image, result_success,
                             self.onDeleteSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.delete_disk_image, result_fail,
                             self.onDeleteFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onDeleteTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.delete_disk_image)
        param = self.case_manager.getParam()
        session.target = param["disk"]
        control_server = param["control_server"]
        request.setString(ParamKeyDefine.uuid, session.target)
        self.info("[%08X]request delete disk image '%s' to control server '%s'"%
                       (session.session_id, session.target, control_server))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onDeleteSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]delete disk image success, id '%s'"%
                       (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onDeleteFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]delete disk image fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onDeleteTimeout(self, msg, session):
        self.info("[%08X]delete disk image timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
