#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class GetLoadBalancerTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.get_load_balancer,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.get_load_balancer, result_success,
                             self.onRunSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.get_load_balancer, result_fail,
                             self.onRunFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRunTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.get_load_balancer)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        
        uuid = param["uuid"]       
        request.setString(ParamKeyDefine.uuid, uuid)
             
        self.info("[%08X]request Get load balancer '%s'"%
                       (session.session_id, uuid))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onRunSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]Get load balancer success"%
                       (session.session_id))
        try:
            btype = msg.getUInt(ParamKeyDefine.type)
            name = msg.getString(ParamKeyDefine.name)
            uuid = msg.getStringArray(ParamKeyDefine.uuid)
            host = msg.getStringArray(ParamKeyDefine.host)
            ip = msg.getStringArrayArray(ParamKeyDefine.ip)
            port = msg.getUIntArrayArray(ParamKeyDefine.port)

            ntype = ChangeResuleStatus(btype,Status_load_balancer)

            title = ['Type','Host','Name','Uuid','IP','Port']
            print_test_result(title,ntype,host,name,uuid,ip,port)
            
        except:
            print "show result failed! some values is None."


        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRunFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]Get load balancer fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRunTimeout(self, msg, session):
        self.info("[%08X]Get load balancer, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
