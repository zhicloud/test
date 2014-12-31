#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
from service.node_service import *
from service.message_define import *
from task.task_manager import *
from task.task_type import *
from case_manager import *
from test_result_enum import *
from test_case import *
from transport.whisper import *
from whisper_proxy import *
import os

class TestService(NodeService):
    """
    base:NodeService
    
    usage:
    attrib:
        server_rack
        server
        server_name
        domain
        group
        node
        type
        version
        local_ip
        local_port
        domain_server

    methods:
    
    bind(ip):
    start():
    stop():
    sendMessage(msg, receiver):
    sendMessageToSelf(msg):
    connectRemoteNode(remote_ip, remote_port):
    
    setTimer(timeout, receive_session):
        invoke timeout event to [receive_session] after [timeout] seconds
        @return:timer_id
        
    setLoopTimer(timeout, receive_session):
        continues invoke timeout event to [receive_session] after [timeout] seconds
        @return:timer_id
        stop by clearTimer()
        
    setTimedEvent(event, timeout):
        invoke specified [event] to handler after [timeout] seconds
        @return:timer_id
        
    setLoopTimedEvent(event, timeout):
        continues invoke specified [event] to handler after [timeout] seconds
        @return:timer_id
        stop by clearTimer()
        
    clearTimer(timer_id):
        cancel timeout count down
    

    methods need override by subclass:
    onStart():
        onStart:subclass must call NodeService.onStart() first
        @return:
        False = initial fail, stop service
        True = initial success, start main service
        
    onStop():
        onStop:subclass must call NodeService.onStop() first

    onChannelConnected(node_name, node_type, remote_ip, remote_port):
    onChannelDisconnected(node_name, node_type):
    onTransportEstablished(ip, port):
    onDomainJoined():
    onDomainLeft():
    handleEventMessage(event, sender):
    handleRequestMessage(request, sender):
    handleResponseMessage(response, sender):
    """
    
    def __init__(self,                  
                 service_name, domain, ip, group_ip, group_port,
                 server, rack, server_name, proxy):
        NodeService.__init__(self, NodeTypeDefine.manage_terminal,
                             service_name, domain, ip, 5600, 200,
                             group_ip, group_port, "0.0",
                             server, rack, server_name, proxy)

        self.zc_node_name = None
        self.case_manager = CaseManager(self.onTestCaseFinished)
        #get file path
        tmppath = os.path.join(os.getcwd(),"tmp")
        self.whisper = Whisper(ip, 10, tmppath, "%s.whisper"%(self.name))
        self.proxy = WhisperProxy(self.whisper, self)

        self.trans_manager = TaskManager("%s.task"%(self.name),
                                         self,
                                         self.case_manager,
                                         self.proxy)

            
    def initialize(self):
        self.whisper.initial()
        ##add test case
        enviro = self.case_manager.getParam()         
        enviro["pool"] = "060b8aff6fb04ca092534c6540425776"
        #enviro["resource"] = "node_client_0050563c7a20"
        enviro["resource"] = "node_client_047d7b87143d"
        enviro["iso"] = "a2a0ba94f6584ed58a263627a151d978"
        ##original
        ##clone1
        enviro["host"] = "e3990406-5f3e-4fe7-8b9c-e408abc2e5b8"        
        enviro["disk"] = "ce44c035daa94e53b98810b222ccb580"
##        self.case_manager.addTestCase(TestCase("add_compute_resource", add_compute_resource))
##        self.case_manager.addTestCase(TestCase("create_host", create_host))
##        self.case_manager.addTestCase(TestCase("modify_host", modify_host))
##        self.case_manager.addTestCase(TestCase("halt_host", halt_host))
##        self.case_manager.addTestCase(TestCase("start_host", start_host))
##        self.case_manager.addTestCase(TestCase("stop_host", stop_host))
##        self.case_manager.addTestCase(TestCase("insert_media", insert_media))
##        self.case_manager.addTestCase(TestCase("change_media", change_media))
##        self.case_manager.addTestCase(TestCase("eject_media", eject_media))
##        self.case_manager.addTestCase(TestCase("halt_host", halt_host))
##        self.case_manager.addTestCase(TestCase("delete_host", delete_host))
##        self.case_manager.addTestCase(TestCase("remove_compute_resource", remove_compute_resource))
##        self.case_manager.addTestCase(TestCase("query_iso_image", query_iso_image))
##        self.case_manager.addTestCase(TestCase("upload_iso_image", upload_iso_image))
##        self.case_manager.addTestCase(TestCase("modify_iso_image", modify_iso_image))
##        self.case_manager.addTestCase(TestCase("delete_iso_image", delete_iso_image))
        
##        self.case_manager.addTestCase(TestCase("query_disk_image", query_disk_image))
##        self.case_manager.addTestCase(TestCase("create_disk_image", create_disk_image))
##        self.case_manager.addTestCase(TestCase("delete_disk_image", delete_disk_image))
##        self.case_manager.addTestCase(TestCase("modify_disk_image", modify_disk_image))
##        self.case_manager.addTestCase(TestCase("read_disk_image", read_disk_image))
        
        ##test case
##        self.case_manager.addTestCase(TestCase("create_host", create_host))
        #print "TestService->initalize->start_host"
        #add case:start_host to CaseManager.case_list
        
        #start host
        #self.case_manager.addTestCase(TestCase("query_disk_image", query_disk_image))
        #self.case_manager.addTestCase(TestCase("query_iso_image", query_iso_image))
       
        self.console("service %s initilized"%self.name)
        self.info("service %s initilized"%self.name)
        ##bind handler
        return True;

    def onStart(self):
        """
        onStart:subclass must call NodeService.onStart() first
        @return:
        False = initial fail, stop service
        True = initial success, start main service
        """
        if not self.initialize():
            return False
        if not NodeService.onStart(self):
            return False
        self.whisper.start()
        return True
        
    def onStop(self):
        """
        onStop:subclass must call NodeService.onStop() first
        """
        NodeService.onStop(self)
        self.whisper.stop()

    def onChannelConnected(self, node_name, node_type, remote_ip, remote_port):
        self.console("channel connected, node name '%s', type: %d"%(node_name, node_type))
        self.info("channel connected, node name '%s', type: %d"%(node_name, node_type))
        if node_type == NodeTypeDefine.control_server:
            self.zc_node_name = node_name
            ##control server
            enviro = self.case_manager.getParam()
            enviro["control_server"] = node_name            
            #self.beginTest()


    def onChannelDisconnected(self, node_name, node_type):
        self.info("channel disconnected, node name '%s', type: %d"%(node_name, node_type))
      
    def handleEventMessage(self, event, sender):
        if 0 != event.session:
            if self.trans_manager.containsTransaction(event.session):
                return self.trans_manager.processMessage(event.session, event)
        
    def handleResponseMessage(self, response, sender):
        if 0 != response.session:
            if self.trans_manager.containsTransaction(response.session):
                return self.trans_manager.processMessage(response.session, response)

    def bindCallback(self, function):
        self.call_back = function

    def onTestCaseFinished(self, name, result):
        if result != TestResultEnum.success:
            if result == TestResultEnum.fail:
                self.error("<TestService>case '%s' fail"%(name))
            else:
                self.error("<TestService>case '%s' timeout"%(name))
            self.error("<TestService>test failed")    
            self.onTestFinished(False)
            return
        self.info("<TestService>case '%s' success"%(name))
        ##next
        if not self.case_manager.hasMoreCase():
            ##all success
            #self.info("<TestService>test passed")
            self.onTestFinished(True)
            return
        testcase = self.case_manager.getNextCase()
        self.info("<TestService>case '%s' begin..."%(testcase.name))
        request = getRequest(RequestDefine.invalid)
        session_id = self.trans_manager.allocTransaction(testcase.id)
        self.trans_manager.startTransaction(session_id, request)
        
    
    def onTestFinished(self, passed):
        if self.call_back is not None:
            self.call_back(passed)

    def beginTest(self):
        testcase = self.case_manager.getFirstCase()
        self.info("<TestService>case '%s' begin..."%(testcase.name))
        request = getRequest(RequestDefine.invalid)
        session_id = self.trans_manager.allocTransaction(testcase.id)
        self.trans_manager.startTransaction(session_id, request)
        
