#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *
from ts_format import *

class AddPortRescourceTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.add_port_resource,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.add_port_resource, result_success,
                             self.onAddSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.add_port_resource, result_fail,
                             self.onAddFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onAddTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.add_port_resource)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        pool = param["pool"]
        ip = param["ip"]
        iprange = param["range"]
        
        iplist = ip.split(',')
        iprangelist = iprange.split(',')
        newrange = []
        for rg in iprangelist:
            newrange.append(int(rg))

        request.setString(ParamKeyDefine.pool, pool)
        request.setStringArray(ParamKeyDefine.ip, iplist)
        request.setUIntArray(ParamKeyDefine.range, newrange)
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onAddSuccess(self, msg, session):
        self.clearTimer(session)
        #uuid = msg.getString(ParamKeyDefine.uuid)
        
        self.info("[%08X]Add port pool success."%
                       (session.session_id))       

        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onAddFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]Add port pool fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onAddTimeout(self, msg, session):
        self.info("[%08X]Add port pool timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
