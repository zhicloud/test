#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class AddAddressResourceTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.add_address_resource"
        BaseTask.__init__(self, task_type, RequestDefine.add_address_resource,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.add_address_resource, result_success,
                             self.onAddSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.add_address_resource, result_fail,
                             self.onAddFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onAddTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.add_address_resource)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        pool_uuid = param["pool"]
        ip= param["ip"]
        arange=param["range"]
        print "ip : %s" % ip

        
        iplist = ip.split(',')
        print "Get ip address: %s" % str(iplist)
        
        iprangelist = arange.split(',')
        newrange = []
        for rg in iprangelist:
            newrange.append(int(rg))            
        
        request.setString(ParamKeyDefine.pool, pool_uuid)
        request.setStringArray(ParamKeyDefine.ip, iplist)
        request.setUIntArray(ParamKeyDefine.range, newrange)
        self.info("[%08X]request add address resource to pool '%s'"%
                       (session.session_id,pool_uuid))
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, param["control_server"])

    def onAddSuccess(self, msg, session):
        self.clearTimer(session)

        self.info("[%08X]add address resource success"%
                       (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onAddFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]add address resource fail"%
                  (session.session_id))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onAddTimeout(self, msg, session):
        self.info("[%08X]add address resource timeout"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
