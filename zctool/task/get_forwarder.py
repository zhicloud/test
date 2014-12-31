#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class GetForwarderTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.remove_compute_resource"
        BaseTask.__init__(self, task_type, RequestDefine.get_forwarder,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.get_forwarder, result_success,
                             self.onGetSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.get_forwarder, result_fail,
                             self.onGetFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onGetTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.get_forwarder)
        param = self.case_manager.getParam()
        uuid = param["id"]
        
        request.setString(ParamKeyDefine.uuid, uuid)

        self.info("[%08X]get forwarder information,uuid is:: '%s'"%
                       (session.session_id, param["id"]))

        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, param["control_server"])

    def onGetSuccess(self, msg, session):
        self.clearTimer(session)
        querydata = {}
        ftype = msg.getUInt(ParamKeyDefine.type)
        uuid  = msg.getString(ParamKeyDefine.uuid)
        name  = msg.getString(ParamKeyDefine.name)
        ip  = msg.getStringArray(ParamKeyDefine.ip)
        display_port = msg.getUIntArray(ParamKeyDefine.display_port)
        port = msg.getUIntArray(ParamKeyDefine.port)

        newtype = ChangeResuleStatus(ftype,Status_Forwarder)

        querydata["type"] = newtype
        querydata["uuid"] = uuid
        querydata["name"] = name
        querydata["ip"] = ip
        querydata["display_port"] = display_port
        querydata["port"] = port

        print_one_result(querydata)
                         

        self.info("[%08X]get forwarder success, name '%s'"%
                       (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onGetFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]get forwarder fail, name '%s'"%
                  (session.session_id, session.target))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onGetTimeout(self, msg, session):
        self.info("[%08X]get forwarder timeout, name '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
