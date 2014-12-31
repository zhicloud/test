#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *
from ts_format import *

class QueryAddressResourceTask(BaseTask):
    operate_timeout = 20
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        ##logger_name = "task.query_service"
        BaseTask.__init__(self, task_type, RequestDefine.query_address_resource,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_address_resource, result_success,
                             self.onQuerySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_address_resource, result_fail,
                             self.onQueryFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """        
        request = getRequest(RequestDefine.query_address_resource)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        pool_uuid = param["pool"]
        request.setString(ParamKeyDefine.pool, pool_uuid)
        #self.info("[%08X]request query address resource in pool'%s'to control server '%s'"%
                       #(session.session_id,pool_uuid, control_server))
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onQuerySuccess(self, msg, session):
        self.clearTimer(session)
        ip = msg.getStringArray(ParamKeyDefine.ip)
        status = msg.getUIntArray(ParamKeyDefine.status)
        count = msg.getUIntArrayArray(ParamKeyDefine.count)
        self.info("[%08X]query address resource SUCCESS"%
                       (session.session_id))
##        for i in range(count):
##            self.info("[%08X]Service No.%d,name=%s,ip=%s,port=%d,status=%d"%(
##                session.session_id, (i+1), name[i], ip[i],port[i],status[i]))

        #show query result
        newstatus=ChangeResuleStatus(status,Status_Address_Resource)
        title = ['IP','Status','Count']
        print_test_result(title,ip,newstatus,count)
        
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onQueryFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query address resource FAIL"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onQueryTimeout(self, msg, session):
        self.info("[%08X]query address resource TIMEOUT"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
