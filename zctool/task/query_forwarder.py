#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *
from ts_format import *

class QueryForWarderTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.query_forwarder,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_forwarder, result_success,
                             self.onQuerySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_forwarder, result_fail,
                             self.onQueryFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.query_forwarder)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        ptype = int(param["type"])
        request.setUInt(ParamKeyDefine.type, ptype)
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onQuerySuccess(self, msg, session):
        self.clearTimer(session)
        uuid = msg.getStringArray(ParamKeyDefine.uuid)
        ip = msg.getStringArrayArray(ParamKeyDefine.ip)
        host = msg.getStringArray(ParamKeyDefine.host)
        name = msg.getStringArray(ParamKeyDefine.name)
        port = msg.getUIntArrayArray(ParamKeyDefine.port)

        domain = msg.getStringArray(ParamKeyDefine.domain)
        status = msg.getUIntArray(ParamKeyDefine.status)
        
        count = len(uuid)
        self.info("[%08X]query forwarder success, %d forwarder(s) available"%
                       (session.session_id, count))

        newstatus = ChangeResuleStatus(status,Status_Port_Pool)
        
        title = ['Name','UUID','IP','Host','Port','Domain','Status']
        print_test_result(title,name,uuid,ip,host,port,domain,newstatus)

        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onQueryFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query forwarder fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onQueryTimeout(self, msg, session):
        self.info("[%08X]query forwarder timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
