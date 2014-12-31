#!/usr/bin/python
import io
import os.path
import os
import logging
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class UploadISOImageTask(BaseTask):
    operate_timeout = 10
    package_size = 32*1024##32KiB
    buffer_size = 10 * 1024 * 1024##10 MiB
    def __init__(self, task_type, messsage_handler,
                 case_manager, whisper_proxy,logger_name):
        self.case_manager = case_manager
        self.whisper_proxy = whisper_proxy
        #logger_name = "task.upload_iso_image"
        BaseTask.__init__(self, task_type, RequestDefine.upload_iso_image,
                          messsage_handler, logger_name)
        
        stStart = 2
        stTransport = 3
        stCreate = 4
        self.addState(stStart)
        self.addState(stTransport)
        self.addState(stCreate)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_whisper, result_success,
                             self.onQuerySuccess, stStart)        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_whisper, result_fail,
                             self.onQueryFail)        
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryTimeout)

        self.addTransferRule(stStart, AppMessage.EVENT,
                             EventDefine.ack, result_success,
                             self.onStartSuccess, stTransport)        
        self.addTransferRule(stStart, AppMessage.EVENT,
                             EventDefine.finish, result_fail,
                             self.onStartFail)        
        self.addTransferRule(stStart, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onStartTimeout)

        self.addTransferRule(stTransport, AppMessage.EVENT,
                             EventDefine.finish, result_success,
                             self.onTransportSuccess, stCreate)        
        self.addTransferRule(stTransport, AppMessage.EVENT,
                             EventDefine.finish, result_fail,
                             self.onTransportFail)
        self.addTransferRule(stTransport, AppMessage.EVENT,
                             EventDefine.report, result_success,
                             self.onTransportProgress, stTransport)        
        self.addTransferRule(stTransport, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onTransportTimeout)

        self.addTransferRule(stCreate, AppMessage.RESPONSE,
                             RequestDefine.upload_iso_image, result_success,
                             self.onCreateSuccess)        
        self.addTransferRule(stCreate, AppMessage.RESPONSE,
                             RequestDefine.upload_iso_image, result_fail,
                             self.onCreateFail)        
        self.addTransferRule(stCreate, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onCreateTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        param = self.case_manager.getParam()
        session.control_server = param["control_server"]
        
        request = getRequest(RequestDefine.query_whisper)
        request.session = session.session_id       
        
        logging.info("[%08X]request query whisper to control server '%s'"%
                       (session.session_id, session.control_server))        
        
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, session.control_server)        
    
    def onQuerySuccess(self, msg, session):
        self.clearTimer(session)
        whisper_name = msg.getStringArray(ParamKeyDefine.name)
        whisper_ip = msg.getStringArray(ParamKeyDefine.ip)
        whisper_port = msg.getUIntArray(ParamKeyDefine.port)
        if 0 == len(whisper_name):
            logging.error("[%08X]query whipser success, but no whisper available"%
                  (session.session_id))
            self.case_manager.finishTestCase(TestResultEnum.fail)
            session.finish()
            return
        
        remote_ip = whisper_ip[0]
        remote_port = whisper_port[0]
        param = self.case_manager.getParam()
        filename = param["iso_file_path"]
        #filename = "D:\\software\\os\\CentOS-6.4-x86_64-minimal.iso"
##        filename = "D:\\documents\\upload_test.xmind"

        session.task_id = self.whisper_proxy.startWrite(session.session_id, filename,
                                                        remote_ip, remote_port)
        logging.info("[%08X]start write task %d, file '%s', remote address '%s:%d'"%
                       (session.session_id, session.task_id, filename, remote_ip, remote_port))
        self.setTimer(session, self.operate_timeout)

    def onQueryFail(self, msg, session):
        self.clearTimer(session)
        logging.error("[%08X]query whisper fail"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onQueryTimeout(self, msg, session):
        logging.error("[%08X]query whisper timeout"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
        
    def onStartSuccess(self, msg, session):
        self.clearTimer(session)        
        logging.info("[%08X]start transport success, task '%d'"%
                       (session.session_id, session.task_id))

        self.setTimer(session, self.operate_timeout)

    def onStartFail(self, msg, session):
        self.clearTimer(session)
        logging.error("[%08X]start transport fail"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onStartTimeout(self, msg, session):
        logging.error("[%08X]start transport timeout"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
        
    def onTransportSuccess(self, msg, session):
        self.clearTimer(session)
        file_id = msg.getString(ParamKeyDefine.uuid)
        
        param = self.case_manager.getParam()
        #name = "centos_6_4"
        name = param["iso_file_name"]
        #description = "test iso"
        description = param["iso_describe"]
        group = "system"
        user = "akumas"
        session.target = name
        
        request = getRequest(RequestDefine.upload_iso_image)
        request.session = session.session_id
        request.setString(ParamKeyDefine.name, name)
        request.setString(ParamKeyDefine.target, file_id)
        request.setString(ParamKeyDefine.description, description)
        request.setString(ParamKeyDefine.group, group)
        request.setString(ParamKeyDefine.user, user)        
        
        logging.info("[%08X]request upload image '%s'(file '%s') to control server '%s'"%
                       (session.session_id, name, file_id, session.control_server))
        
        
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, session.control_server)        
        
    def onTransportProgress(self, msg, session):
        self.clearTimer(session)
        level = msg.getUInt(ParamKeyDefine.level)
        logging.info("[%08X]transport on progess, level %d..."%
                  (session.session_id, level))
        self.setTimer(session, self.operate_timeout)

    def onTransportFail(self, msg, session):
        self.clearTimer(session)
        logging.error("[%08X]transport data fail"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
        
    def onTransportTimeout(self, msg, session):
        logging.error("[%08X]transport data timeout"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()

    def onCreateSuccess(self, msg, session):
        self.clearTimer(session)
        uuid = msg.getString(ParamKeyDefine.uuid)
        ip = msg.getString(ParamKeyDefine.ip)
        port = msg.getUInt(ParamKeyDefine.port)
        size = msg.getUInt(ParamKeyDefine.size)
        param = self.case_manager.getParam()
        param["iso"] = uuid
        
        logging.info("[%08X]upload iso image success, image '%s', '%s:%d', size %d bytes"%
                  (session.session_id, uuid, ip, port, size))
        
        self.case_manager.finishTestCase(TestResultEnum.success)
        session.finish()        

    def onCreateFail(self, msg, session):
        self.clearTimer(session)
        logging.error("[%08X]create iso fail"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
        
    def onCreateTimeout(self, msg, session):
        logging.error("[%08X]create iso timeout"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
