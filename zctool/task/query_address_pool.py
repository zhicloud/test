#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *
from ts_format import *

class QueryAddressPoolTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        ##logger_name = "task.query_compute_pool"
        BaseTask.__init__(self, task_type, RequestDefine.query_address_pool,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_address_pool, result_success,
                             self.onQuerySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_address_pool, result_fail,
                             self.onQueryFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.query_address_pool)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        self.info("[%08X]request query address pool to control server '%s'"%
                       (session.session_id, control_server))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onQuerySuccess(self, msg, session):
        self.clearTimer(session)
        name = msg.getStringArray(ParamKeyDefine.name)
        uuid = msg.getStringArray(ParamKeyDefine.uuid)
        status = msg.getUIntArray(ParamKeyDefine.status)
        count = msg.getUIntArrayArray(ParamKeyDefine.count)
        self.info("[%08X]query address pool SUCCESS"%
                       (session.session_id))
        
        newstatus=ChangeResuleStatus(status,Status_Address_Pool)
        try:
            title = ['Pool Name','UUID','Status','Count']
            print_test_result(title,name,uuid,newstatus,count)
        except:
            print "There are some items is None,please check it."
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onQueryFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query address pool FAIL"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onQueryTimeout(self, msg, session):
        self.info("[%08X]query address pool TIMEOUT"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
