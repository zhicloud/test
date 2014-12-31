#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *
from ts_format import *

class RemovePortRescourceTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.remove_port_resource,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.remove_port_resource, result_success,
                             self.onRemoveSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.remove_port_resource, result_fail,
                             self.onRemoveFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRemoveTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.remove_port_resource)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        pool = param["pool"]
        ip = param["ip"]
        iprange = param["range"] #???

        request.setString(ParamKeyDefine.pool, pool)
        request.setStringArray(ParamKeyDefine.ip, ip)
        request.setUIntArray(ParamKeyDefine.range, iprange)
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onRemoveSuccess(self, msg, session):
        self.clearTimer(session)
        #uuid = msg.getString(ParamKeyDefine.uuid)
        
        self.info("[%08X]remove port pool success."%
                       (session.session_id))       

        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRemoveFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]remove port pool fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRemoveTimeout(self, msg, session):
        self.info("[%08X]remove port pool timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
