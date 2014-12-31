#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *
from ts_format import *

class QueryDeviceTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.query_device"
        BaseTask.__init__(self, task_type, RequestDefine.query_device,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_device, result_success,
                             self.onQuerySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_device, result_fail,
                             self.onQueryFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.query_device)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        
        pool_id = param["pool"]
        query_type = int(param["type"])              
        request.setString(ParamKeyDefine.target, pool_id)

        request.setUInt(ParamKeyDefine.type, query_type)
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onQuerySuccess(self, msg, session):
        self.clearTimer(session)
        name = msg.getStringArray(ParamKeyDefine.name)
        uuid = msg.getStringArray(ParamKeyDefine.uuid)
        disk_volume = msg.getUIntArrayArray(ParamKeyDefine.disk_volume)
        status = msg.getUIntArray(ParamKeyDefine.status)
        level = msg.getUIntArray(ParamKeyDefine.level)
        identify = msg.getStringArray(ParamKeyDefine.identify)
        security = msg.getUIntArray(ParamKeyDefine.security)
        crypt = msg.getUIntArray(ParamKeyDefine.crypt)
        page = msg.getUIntArray(ParamKeyDefine.page)

        newstatus = ChangeResuleStatus(status,Status_device)
        new_security = ChangeResuleStatus(security,Status_security)
        new_crypt = ChangeResuleStatus(crypt,Status_crypt)
        new_level = GetPresentValue(level)

        print identify
        print page
        
        newdisk=[]
        for disksize in disk_volume:
            newdisk.append(Change_Bit_to_Gb(disksize))
        newpage=[]
        for pagesize in page:
            newpage.append(Change_Bit_to_Kb(pagesize))
            
        count = len(uuid)
        self.info("[%08X]query device success, %d device(s) available"%
                       (session.session_id, count))

        title = ['Device Name','UUID','Disk(GB)','Page','level','Security','crypt','Status']
        print_test_result(title,name,uuid,newdisk,newpage,new_level,new_security,new_crypt,newstatus)

        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onQueryFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query device fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onQueryTimeout(self, msg, session):
        self.info("[%08X]query device timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
