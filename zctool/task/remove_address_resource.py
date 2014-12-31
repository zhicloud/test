#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class RemoveAddressResourceTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.remove_compute_resource"
        BaseTask.__init__(self, task_type, RequestDefine.remove_address_resource,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.remove_address_resource, result_success,
                             self.onRemoveSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.remove_address_resource, result_fail,
                             self.onRemoveFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRemoveTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.remove_address_resource)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        pool_uuid = param["pool"]
        ip = param["ip"]
        print "ip : %s" % ip
        
        iplist = ip.split(',')

        print "ip address list: %s" % str(iplist)
        
        request.setString(ParamKeyDefine.pool, pool_uuid)
        request.setStringArray(ParamKeyDefine.ip, iplist)
        self.info("[%08X]request remove address resource '%s' from pool '%s'"%
                       (session.session_id, ip, pool_uuid))
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, param["control_server"])

    def onRemoveSuccess(self, msg, session):
        self.clearTimer(session)

        self.info("[%08X]remove addresss resource success"%
                       (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onRemoveFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]remove address resource fail"%
                  (session.session_id))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onRemoveTimeout(self, msg, session):
        self.info("[%08X]remove address resource timeout"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
