#!/usr/bin/python
import io
import os.path
import os
import logging
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class CreateDiskImageTask(BaseTask):
    operate_timeout = 20
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.create_disk_image"
        BaseTask.__init__(self, task_type, RequestDefine.create_disk_image,
                          messsage_handler, logger_name)
        
        stTransport = 2
        self.addState(stTransport)

        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.ack, result_success,
                             self.onStartSuccess, stTransport)        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.create_disk_image, result_fail,
                             self.onStartFail)        
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onStartTimeout)

        self.addTransferRule(stTransport, AppMessage.RESPONSE,
                             RequestDefine.create_disk_image, result_success,
                             self.onTransportSuccess)        
        self.addTransferRule(stTransport, AppMessage.RESPONSE,
                             RequestDefine.create_disk_image, result_fail,
                             self.onTransportFail)
        self.addTransferRule(stTransport, AppMessage.EVENT,
                             EventDefine.report, result_success,
                             self.onTransportProgress, stTransport)        
        self.addTransferRule(stTransport, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onTransportTimeout)    

    def invokeSession(self, session):
        """
        task start, must override
        """
        param = self.case_manager.getParam()
        session.control_server = param["control_server"]
        host = param["host"]
        name = param["disk_image_name"]

        description = param["disk_image_description"]
        identity = list(param["disk_image_tag"].split(','))
        #identity = ["linux", "64bit"]
        group = "system"
        user = "test"
        
        request = getRequest(RequestDefine.create_disk_image)
        request.setString(ParamKeyDefine.name, name)
        request.setString(ParamKeyDefine.uuid, host)
        request.setString(ParamKeyDefine.description, description)
        request.setStringArray(ParamKeyDefine.identity, identity)
        request.setString(ParamKeyDefine.group, group)
        request.setString(ParamKeyDefine.user, user)
        request.session = session.session_id       
        
        logging.info("[%08X]request create disk image to control server '%s'"%
                       (session.session_id, session.control_server))        
        
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, session.control_server)    

    def onStartSuccess(self, msg, session):
        self.clearTimer(session)
        logging.info("[%08X]create disk image started"%
                       (session.session_id))
        self.setTimer(session, self.operate_timeout)

    def onStartFail(self, msg, session):
        self.clearTimer(session)
        logging.error("[%08X]create disk image fail due to remote service"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onStartTimeout(self, msg, session):
        logging.error("[%08X]create disk image timeout"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
        
    def onTransportSuccess(self, msg, session):
        self.clearTimer(session)
        uuid = msg.getString(ParamKeyDefine.uuid)
        size = msg.getUInt(ParamKeyDefine.size)

        param = self.case_manager.getParam()
        param["iso"] = uuid
        logging.info("[%08X]create disk image success, id '%s', size %d bytes"%
                  (session.session_id, uuid, size))
        
        self.case_manager.finishTestCase(TestResultEnum.success)
        session.finish()
        
    def onTransportProgress(self, msg, session):
        self.clearTimer(session)
        level = msg.getUInt(ParamKeyDefine.level)
        logging.info("[%08X]transport on progess, %d %%"%
                  (session.session_id, level))
        self.setTimer(session, self.operate_timeout)

    def onTransportFail(self, msg, session):
        self.clearTimer(session)
        logging.error("[%08X]remote service transport data fail"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
        
    def onTransportTimeout(self, msg, session):
        logging.error("[%08X]remote service transport data timeout"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
