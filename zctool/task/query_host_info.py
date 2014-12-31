#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *
from ts_format import *

class QueryHostInfoTask(BaseTask):
    operate_timeout = 10
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        BaseTask.__init__(self, task_type, RequestDefine.query_host_info,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_host_info, result_success,
                             self.onQuerySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_host_info, result_fail,
                             self.onQueryFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.query_host_info)
        param = self.case_manager.getParam()
        control_server = param["control_server"]
        
        host_id = param["host"]
        #print host_id
        
        request.setString(ParamKeyDefine.uuid, host_id)
        
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)
        
    def onQuerySuccess_bk(self, msg, session):
        self.clearTimer(session)
        querydata = {}

        querydata["name"] = msg.getString(ParamKeyDefine.name)
        querydata["cpu_count"] = msg.getUInt(ParamKeyDefine.cpu_count)
        querydata["memory"] = msg.getUInt(ParamKeyDefine.memory)
        querydata["option"] = msg.getUIntArray(ParamKeyDefine.option)
        querydata["disk_volume"] = msg.getUIntArray(ParamKeyDefine.disk_volume)
        
        querydata["ip"] = msg.getStringArray(ParamKeyDefine.ip)
        querydata["port"] = msg.getUIntArray(ParamKeyDefine.port)
        querydata["user"] = msg.getString(ParamKeyDefine.user)
        querydata["group"] = msg.getString(ParamKeyDefine.group)
        querydata["display"] = msg.getString(ParamKeyDefine.display)

        querydata["authentication"] = msg.getString(ParamKeyDefine.authentication)
        querydata["network"] = msg.getString(ParamKeyDefine.network)
        querydata["inbound_bandwidth"] = msg.getUInt(ParamKeyDefine.inbound_bandwidth)
        querydata["outbound_bandwidth"] = msg.getUInt(ParamKeyDefine.outbound_bandwidth)
        querydata["display_port"] = msg.getUIntArray(ParamKeyDefine.display_port)
        querydata["forward"] = msg.getString(ParamKeyDefine.forward)
        
        network_type = msg.getUInt(ParamKeyDefine.network_type)
        network_type = ChangeResuleStatus(network_type,Type_host_network)
        querydata["network_type"] = network_type
        querydata["network_source"] = msg.getString(ParamKeyDefine.network_source)

        disk_type =  msg.getUInt(ParamKeyDefine.disk_type)
        disk_type =  ChangeResuleStatus(disk_type,Type_host_disk)
        querydata["disk_type"] = disk_type
        querydata["disk_source"] = msg.getString(ParamKeyDefine.disk_source)
        
        self.info("[%08X]query host info success" % (session.session_id))
             
        print_one_result(querydata)
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onQuerySuccess(self, msg, session):
        self.clearTimer(session)
        title = []
        value = []

        title.append("name")
        value.append(msg.getString(ParamKeyDefine.name))

        title.append("cpu_count")
        value.append(msg.getUInt(ParamKeyDefine.cpu_count))
        
        title.append("memory")
        value.append(msg.getUInt(ParamKeyDefine.memory))

        title.append("option")
        value.append(msg.getUIntArray(ParamKeyDefine.option))

        title.append("disk_volume")
        value.append(msg.getUIntArray(ParamKeyDefine.disk_volume))

        title.append("ip")
        value.append(msg.getStringArray(ParamKeyDefine.ip))

        title.append("port")
        value.append(msg.getUIntArray(ParamKeyDefine.port))             

        title.append("user")
        value.append(msg.getString(ParamKeyDefine.user))             

        title.append("group")
        value.append(msg.getString(ParamKeyDefine.group))             

        title.append("display")
        value.append(msg.getString(ParamKeyDefine.display))            


        title.append("authentication")
        value.append(msg.getString(ParamKeyDefine.authentication))

        title.append("network")
        value.append(msg.getString(ParamKeyDefine.network))

        title.append("inbound_bandwidth")
        value.append(msg.getUInt(ParamKeyDefine.inbound_bandwidth))

        title.append("outbound_bandwidth")
        value.append(msg.getUInt(ParamKeyDefine.outbound_bandwidth))

        title.append("display_port")
        value.append(msg.getUIntArray(ParamKeyDefine.display_port))

        title.append("forward")
        value.append(msg.getString(ParamKeyDefine.forward))

        
        network_type = msg.getUInt(ParamKeyDefine.network_type)
        network_type = ChangeResuleStatus(network_type,Type_host_network)
        title.append("network_type")
        value.append(network_type)            

        title.append("network_source")
        value.append(msg.getString(ParamKeyDefine.network_source)) 

        disk_type =  msg.getUInt(ParamKeyDefine.disk_type)
        disk_type =  ChangeResuleStatus(disk_type,Type_host_disk)
        title.append("disk_type")
        value.append(disk_type)

        title.append("disk_source")
        value.append(msg.getString(ParamKeyDefine.disk_source))

        
        self.info("[%08X]query host info success" % (session.session_id))
             
        #print_one_result(querydata)
        print_one_list(title,value)
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onQueryFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query host info fail, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onQueryTimeout(self, msg, session):
        self.info("[%08X]query host info timeout, id '%s'"%
                  (session.session_id, session.target))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()
