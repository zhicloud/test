#!/usr/bin/python
from message_define import *
from logger_helper import * 
from base_service import *
from transport.transporter import *
from transport.app_message import *
from timer_service import *
from domain_node import *

class DispatchEvent(object):
    type_message = 0##by service
    type_datagram = 1##by session layer
    type_connected = 2
    type_disconnected = 3
    def __init__(self):
        self.name = ""
        self.type = self.type_message
        self.session_id = 0
        self.sender = ""
        self.message = None    

class NodeEntry(object):
    def __init__(self, name):
        self.name = name
        self.ip = ""
        self.port = 0
        self.type = 0
        self.domain = ""
        self.group = ""
        self.session = 0
        self.connected = False

class NodeService(BaseService):
    """
    service for node communication

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
    
    start():
    stop():
    sendMessage(msg, receiver):
    sendMessageToSelf(msg):
    connectRemoteNode(name, node_type, ip, port):
    
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
    session_check_interval = 10
    def __init__(self,
                 service_type, service_name,
                 domain, ip, start_port = 5600, port_range = 200,
                 mcast_address = "224.6.6.6", mcast_port = 5666,
                 version = "1.0",
                 server = "", rack = "", server_name = "",
                 config_proxy = None, 
                 max_request = 10000, transport_channel = 1, process_channel = 1, notify_channel = 1,
                 max_datagram_size = 548):
        
        self.server_rack = rack
        self.server = server
        self.server_name = server_name
        
        self.domain = domain
        self.group = ""
        self.node = service_name
        self.type = service_type
        self.version = version
        self.local_ip = ip
        self.local_port = 0
        self.start_port = start_port
        self.port_range = port_range

        self.config_proxy = config_proxy
        
        self.domain_server = ""
        self.domain_connected = False
        self.transport_established = False
        self.service_check_timer = 0
        self.service_check_interval = 10
        self.name = "%s.%s"%(domain, service_name)
        timer_logger = "%s.timer"%(self.name)
        BaseService.__init__(self, self.name, max_request)

        ##key = node name, value = node entry
        self.node_map = {}
        ##key = session id, value = node name
        self.session_map = {}

        ##key = service_type, value = list of service name
        self.service_group = {}
        
        self.transport = Transporter(self.node,
                                     "%s.transport"%(self.name),
                                     self,
                                     transport_channel,
                                     process_channel,
                                     notify_channel,
                                     max_datagram_size)
        self.timer = TimerService(timer_logger)
        self.domain_service = DomainNode(domain, "%s.domain"%(self.name), mcast_address, mcast_port)
        
        self.logger.setLevel(logging.INFO)
        self.transport.logger.setLevel(logging.INFO)
        self.timer.logger.setLevel(logging.INFO)
        self.domain_service.logger.setLevel(logging.INFO)
        
        ##bind callback function
        self.timer.bindEventHandler(self.sendMessageToSelf)
        self.domain_service.bindHandler(self.__onServiceAvailable)
        
    """
    new methods
    """
    
    """
    put message into queue tail
    @msg:message
    @sender:sender name
    @return:True - put success
    """
    def putMessage(self, msg, sender):
        event = DispatchEvent()
        event.message = msg
        event.sender = sender
        return self.putRequest(event)

    """
    put message into queue head
    @msg:message
    @sender:sender name
    @return:True - put success
    """
    def insertMessage(self, msg, sender):
        event = DispatchEvent()
        event.message = msg
        event.sender = sender
        return self.insertRequest(event)

    def sendMessage(self, msg, receiver):
        if receiver == self.node:
            ##send to self
            return self.sendMessageToSelf(msg)
        
        if not self.node_map.has_key(receiver):
            self.warn("<NodeService>send message fail, invalid receiver '%s'"%(receiver))
            return False
        node = self.node_map[receiver]
        msg.sender = self.node
##        self.info("<NodeService>send message to '%s'[%08X]"%(
##            receiver, node.session))
        return self.transport.sendMessage(node.session, [msg])

    def sendMessageToSelf(self, msg):
        return self.putMessage(msg, self.node)

    """
    session layer callback
    """
    def onMessageReceived(self, message, session_id):
        event = DispatchEvent()
        event.type = DispatchEvent.type_datagram
        event.message = message
        event.session_id = session_id
        self.putRequest(event)
    
    def onSessionConnected(self, node_name, session_id):
        event = DispatchEvent()
        event.type = DispatchEvent.type_connected
        event.name = node_name
        event.session_id = session_id
        self.putRequest(event)
    
    def onSessionDisconnected(self, node_name, session_id):
        event = DispatchEvent()
        event.type = DispatchEvent.type_disconnected
        event.name = node_name
        event.session_id = session_id
        self.putRequest(event)

    def sendToDomainServer(self, msg):
        if self.domain_connected:
            return self.sendMessage(msg, self.domain_server)
        
    def setTimer(self, timeout, receive_session):
        """
        invoke timeout event to [receive_session] after [timeout] seconds
        @return:timer_id
        """
        return self.timer.setTimer(timeout, receive_session)
        
    def setLoopTimer(self, timeout, receive_session):
        """
        continues invoke timeout event to [receive_session] after [timeout] seconds
        @return:timer_id
        stop by clearTimer()
        """
        return self.timer.setLoopTimer(timeout, receive_session)
        
        
    def setTimedEvent(self, event, timeout):
        """
        invoke specified [event] to handler after [timeout] seconds
        @return:timer_id
        """
        return self.timer.setTimedEvent(event, timeout)
        
    def setLoopTimedEvent(self, event, timeout):
        """
        continues invoke specified [event] to handler after [timeout] seconds
        @return:timer_id
        stop by clearTimer()
        """
        return self.timer.setLoopTimedEvent(event, timeout)
    
    def clearTimer(self, timer_id):
        """
        cancel timeout count down
        """
        return self.timer.clearTimer(timer_id)
    
    """
    methods need override by subclass
    """

    def onStart(self):
        """
        onStart:subclass must call NodeService.onStart() first
        @return:
        False = initial fail, stop service
        True = initial success, start main service
        """
        if (self.type == NodeTypeDefine.data_server) and (0 == len(self.local_ip)):
            ##must specify ip for data server
            self.console("must specify ip for data server")
            self.critical("must specify ip for data server")
            return False            
        
        if not self.domain_service.start():
            self.console("start domain service fail")
            self.critical("start domain service fail")
            return False
        if not self.timer.start():
            self.console("start timer fail")
            self.critical("start timer fail")
            self.domain_service.stop()
            return False            

        if 0 != len(self.local_ip):
            ##local ip specified
            if not self.transport.bind(self.local_ip, self.start_port, self.port_range):
                self.console("bind service to ip address '%s' fail"%self.local_ip)
                self.critical("bind service to ip address '%s' fail"%self.local_ip)
                self.domain_service.stop()
                self.timer.stop()
                return False
            self.local_port = self.transport.getListenPort()
            self.console("bind service success, service address '%s:%d'"%(self.local_ip, self.local_port))
            self.info("bind service success, service address '%s:%d'"%(self.local_ip, self.local_port))
            if not self.transport.start():
                self.console("start transport fail")
                self.critical("start transport fail")
                self.domain_service.stop()
                self.timer.stop()
                return False
            self.console("service %s.%s(version %s) started"%(self.domain, self.node, self.version))
            self.info("service %s.%s(version %s) started"%(self.domain, self.node, self.version))
            self.transport_established = True
            self.onTransportEstablished(self.local_ip, self.local_port)

            if self.type == NodeTypeDefine.data_server:
                ##publish
                self.domain_service.addService(self.node, self.local_ip, self.local_port)
                self.domain_service.publish()
                self.console("service published, %s('%s:%d')"%(self.node, self.local_ip, self.local_port))
                self.info("service published, %s('%s:%d')"%(self.node, self.local_ip, self.local_port))
            else:
                ##query
                self.domain_service.query()
                self.console("query domain service...") 
                self.info("query domain service...") 
            return True

        else:
            ##local ip not specified
            ##query
            self.domain_service.query()
            self.console("query domain service...") 
            self.info("query domain service...")
            self.__enableServiceCheck()
            return True

    def onStop(self):
        """
        onStop:subclass must call NodeService.onStop() first
        """
        self.__leaveDomain()
        ##disconnect all node
        for node_name in self.node_map.keys():
            self.disconnectRemoteNode(node_name)
            
        self.domain_service.stop()
        self.timer.stop()
        self.transport.stop()
        self.console("node %s.%s stopped"%(self.domain, self.node))
        self.info("node %s.%s stopped"%(self.domain, self.node))        

    def onChannelConnected(self, node_name, node_type, remote_ip, remote_port):
        pass

    def onChannelDisconnected(self, node_name, node_type):
        pass

    def onTransportEstablished(self, ip, port):
        pass
    
    def handleEventMessage(self, event, sender):
        pass
    def handleRequestMessage(self, request, sender):
        pass
    def handleResponseMessage(self, response, sender):
        pass

    def onDomainJoined(self):
        pass
    def onDomainLeft(self):
        pass

    def OnRequestReceived(self, event):
        if event.type == DispatchEvent.type_message:
            return self.handleMessageReceived(event.message, event.sender)
        elif event.type == DispatchEvent.type_datagram:
            return self.handleDatagramReceived(event.message, event.session_id)
        elif event.type == DispatchEvent.type_connected:
            return self.handleSessionConnected(event.name, event.session_id)
        elif event.type == DispatchEvent.type_disconnected:
            return self.handleSessionDisconnected(event.name, event.session_id)


    def handleDatagramReceived(self, message, session_id):
##        self.info("<NodeService>receive datagram from session [%08X], id %d"%(session_id, message.id))
        if not self.session_map.has_key(session_id):
            self.warn("<NodeService>ignore received message, invalid session [%08X]"%(session_id))
            return False
        node_name = self.session_map[session_id]
        if not self.node_map.has_key(node_name):
            self.warn("<NodeService>ignore received message, can't find node for session [%08X]"%(session_id))
            return False
        self.handleMessageReceived(message, node_name)        
    
    def handleSessionConnected(self, node_name, session_id):
        if self.node_map.has_key(node_name):
            entry = self.node_map[node_name]
            ##connect by self
##            self.info("<NodeService>session connected by local node, node '%s', session [%08X]"%(node_name, session_id))
            ##update session
            entry.session = session_id
            self.session_map[session_id] = node_name

            ##send connect request
            request = getRequest(RequestDefine.connect_node)
            setString(request, ParamKeyDefine.domain, self.domain)
            setString(request, ParamKeyDefine.name, self.node)
            setUInt(request, ParamKeyDefine.type, self.type)
            setString(request, ParamKeyDefine.ip, self.local_ip)
            setUInt(request, ParamKeyDefine.port, self.local_port)
            setString(request, ParamKeyDefine.group, "")
            self.sendMessage(request, node_name)
        
        else:
            ##connect by remote
##            self.info("<NodeService>session connected by remote node, node '%s'"%(node_name))
            self.allocateNode(node_name, session_id)
    
    def handleSessionDisconnected(self, node_name, session_id):
        if not self.node_map.has_key(node_name):
            self.warn("<NodeService>session disconnected, but can't find node '%s'"%(node_name))
            return False
        entry = self.node_map[node_name]
        if session_id != entry.session:
            if self.session_map.has_key(session_id):
                ##link disconnected, but session reconnected
##                self.info("<NodeService>link disconnected, remove session [%08X] for node '%s'"%(
##                    session_id, entry.name))
                del self.session_map[session_id]            
        else:
##            self.warn("<NodeService>session disconnected, node '%s'"%(entry.name))
            ##notify disconnected
            event = getEvent(EventDefine.channel_disconnected)
            setString(event, ParamKeyDefine.node_name, entry.name)
            setUInt(event, ParamKeyDefine.node_type, entry.type)
            self.sendMessageToSelf(event)
            ##only set status        
            entry.connected = False
            
            check = getEvent(EventDefine.session_check)
            check.session = session_id
            setString(check, ParamKeyDefine.node_name, entry.name)
            
            self.setTimedEvent(check, self.session_check_interval)
            
    def __onCheckSession(self, node_name, session_id):
        if not self.session_map.has_key(session_id):
            self.warn("<NodeService>session check fail, invalid session [%08X]"%(
                session_id))
            return False
        if node_name != self.session_map[session_id]:
            self.warn("<NodeService>session check fail, session [%08X] changed for node '%s'"%(
                session_id, self.session_map[session_id]))
            return False
        if not self.node_map.has_key(node_name):
            self.warn("<NodeService>session check fail, can't find node '%s'"%(node_name))
            return False
        entry = self.node_map[node_name]
        if not entry.connected:
            ##still in disconnected
            self.deallocateNode(node_name)
##            self.info("<NodeService>session check success, deallocate invalid node '%s'(session [%08X])"%(
##                node_name, session_id))            
            

    def allocateNode(self, node_name, session_id):
        entry = NodeEntry(node_name)
        entry.session = session_id
        self.node_map[node_name] = entry
        self.session_map[session_id] = node_name
##        self.info("<NodeService>node allocated, name '%s', session [%08X]"%(node_name, session_id))
        return entry

    def deallocateNode(self, node_name):
        if self.node_map.has_key(node_name):
            entry = self.node_map[node_name]
            if 0 != entry.session:
                if self.session_map.has_key(entry.session):
                    del self.session_map[entry.session]
##            self.info("<NodeService>node deallocated, name '%s', session [%08X]"%(entry.name, entry.session))
            ##update service group
            if self.service_group.has_key(entry.type):
                service_group = self.service_group[entry.type]
                if entry.name in service_group:
                    ##remove service
                    del service_group[service_group.index(entry.name)]
                if 0 == len(service_group):
                    ##empty group
                    del self.service_group[entry.type]
                    
            del self.node_map[node_name]

    def connectRemoteNode(self, name, node_type, ip, port, group = "default"):
        if self.node_map.has_key(name):
            ##allocated
            entry = self.node_map[name]
            if entry.connected:
                self.warn("<NodeService>ignore connect node request, remote node '%s' already connected"%(name))
                return True
            ##disconnected
            entry.ip = ip
            entry.port = port
            entry.session = 0
            ##point to new address
##            self.info("<NodeService>reconnect remote node, name '%s', address '%s:%d'"%(
##                name, ip, port))
            return True            
        entry = self.allocateNode(name, 0)
        if not entry:
            self.error("<NodeService>connect remote node fail, can't allocate node '%s'"%(name))
            return False
        entry.type = node_type
        entry.ip = ip
        entry.port = port
        entry.group = group
##        self.info("<NodeService>connecting remote node, name '%s', type %d, address '%s:%d'"%(name, node_type, ip, port))
        self.transport.connect(ip, port)
        
    def disconnectRemoteNode(self, service_name):    
        request = getRequest(RequestDefine.disconnect_node)
##        self.info("<NodeService>disconnecting node '%s'..."%(service_name))
        self.sendMessage(request, service_name)        
        
    def handleMessageReceived(self, message, sender):
##        self.info("<NodeService>receive message from sender '%s', id %d"%(sender, message.id))
        message.sender = sender
        if self.__isSystemMessage(message):
            return self.__handleSystemMessage(message, sender)
        else:
            return self.__onMessageReceived(message, sender)
        
        
    def __isSystemMessage(self, message):
        if message.type == AppMessage.EVENT:
            """
            sysytem event
            """
            if message.id == EventDefine.channel_connected:
                return True
            elif message.id == EventDefine.channel_disconnected:
                return True
            elif message.id == EventDefine.service_available:
                return True
            elif message.id == EventDefine.service_check:
                return True
            elif message.id == EventDefine.session_check:
                return True
            
        elif message.type == AppMessage.RESPONSE:
            if message.id == RequestDefine.join_domain:
                return True
            elif message.id == RequestDefine.leave_domain:
                return True
            elif message.id == RequestDefine.connect_node:
                return True
            elif message.id == RequestDefine.disconnect_node:
                return True
            
        elif message.type == AppMessage.REQUEST:
            if message.id == RequestDefine.connect_node:
                return True
            elif message.id == RequestDefine.disconnect_node:
                return True
            
        return False

    def __handleSystemMessage(self, message, sender):
        if message.type == AppMessage.EVENT:
            """
            sysytem event
            """
            if message.id == EventDefine.channel_connected:
                ##node connected
                node_name = getString(message, ParamKeyDefine.node_name)
                node_type = getUInt(message, ParamKeyDefine.node_type)
                remote_ip = getString(message, ParamKeyDefine.ip)
                remote_port = getUInt(message, ParamKeyDefine.port) 
                self.onChannelConnected(node_name, node_type, remote_ip, remote_port)
                if (self.type != NodeTypeDefine.data_server) and (node_type == NodeTypeDefine.data_server):
                    ##auto join domain server when domain server connected
                    self.__joinDomain(node_name)
                return
            elif message.id == EventDefine.channel_disconnected:
                ##node disconnected
                node_name = getString(message, ParamKeyDefine.node_name)
                node_type = getUInt(message, ParamKeyDefine.node_type)
                self.onChannelDisconnected(node_name, node_type)
                if node_type == NodeTypeDefine.data_server:
                    self.__onDataServerDisconnected(node_name)
                return
            elif message.id == EventDefine.service_available:
                service_name = getString(message, ParamKeyDefine.name)
                remote_ip = getString(message, ParamKeyDefine.ip)
                remote_port = getUInt(message, ParamKeyDefine.port) 
                self.__handleServiceAvailable(service_name, remote_ip, remote_port, sender)
                return
            elif message.id == EventDefine.service_check:
                return self.__onCheckService()
            elif message.id == EventDefine.session_check:
                node_name = getString(message, ParamKeyDefine.node_name)
                session = message.session
                return self.__onCheckSession(node_name, session)                
        elif message.type == AppMessage.RESPONSE:
            if message.id == RequestDefine.join_domain:
                return self.__onJoinDomainResponse(message, sender)
            elif message.id == RequestDefine.leave_domain:
                return self.__onLeaveDomainResponse(message, sender)
            elif message.id == RequestDefine.connect_node:
                return self.__onConnectResponse(message, sender)
            elif message.id == RequestDefine.disconnect_node:
                return self.__onDisconnectResponse(message, sender)
            
        elif message.type == AppMessage.REQUEST:
            if message.id == RequestDefine.connect_node:
                return self.__onConnectRequest(message, sender)
            elif message.id == RequestDefine.disconnect_node:
                return self.__onDisconnectRequest(message, sender)
            
    def __joinDomain(self, dataserver):
        request = getRequest(RequestDefine.join_domain)
        setString(request, ParamKeyDefine.domain, self.domain)
        setString(request, ParamKeyDefine.name, self.node)
        setUInt(request, ParamKeyDefine.type, self.type)
        setString(request, ParamKeyDefine.ip, self.local_ip)
        setUInt(request, ParamKeyDefine.port, self.local_port)
        setString(request, ParamKeyDefine.version, self.version)
        setString(request, ParamKeyDefine.server, self.server)
        request.setString(ParamKeyDefine.server_name, self.server_name)
        self.console("<NodeService>request join domain '%s' to '%s'..."%
                     (self.domain, dataserver))
        self.info("<NodeService>request join domain '%s' to '%s'..."%
                  (self.domain, dataserver))
        
        self.sendMessage(request, dataserver)

    def __onJoinDomainResponse(self, response, sender):
        if not response.success:
            self.console("<NodeService>join domain fail")
            self.error("<NodeService>join domain fail")
            ##disconnect from domain server
            self.disconnectRemoteNode(sender)
            return
        ##location
        self.server_rack = getString(response, ParamKeyDefine.rack)
        self.group = response.getString(ParamKeyDefine.group)
        
        if 0 != len(self.server_rack):
            self.console("<NodeService>join domain success, server rack '%s'"%
                         (self.server_rack))
            self.info("<NodeService>join domain success, server rack '%s'"%
                         (self.server_rack))
            ##store server location
            self.modifyServer(self.server, self.server_rack)
        else:
            self.console("<NodeService>join domain success")
            self.info("<NodeService>join domain success")        

        ##success
        service_count = getUInt(response, ParamKeyDefine.count)
        self.domain_server = sender
        self.domain_connected = True
        self.__disableServiceCheck()
        
        if 0 == service_count:
            self.console("<NodeService>no relative service available")
            self.info("<NodeService>no relative service available")
            self.onDomainJoined()
            return
        name_list = getStringArray(response, ParamKeyDefine.name)
        type_list = getUIntArray(response, ParamKeyDefine.type)
        group_list = getStringArray(response, ParamKeyDefine.group)
        ip_list = getStringArray(response, ParamKeyDefine.ip)
        port_list = getUIntArray(response, ParamKeyDefine.port)
        version = response.getStringArray(ParamKeyDefine.version)
        
        self.console("<NodeService>%d relative services available"%service_count)
        self.info("<NodeService>%d relative services available"%service_count)
        for index in range(service_count):
            self.connectRemoteNode(name_list[index], type_list[index],
                                   ip_list[index], port_list[index],
                                   group_list[index])
            
        self.onDomainJoined()
        
    def __leaveDomain(self):
        if self.domain_connected:
            request = getRequest(RequestDefine.leave_domain)
            setString(request, ParamKeyDefine.domain, self.domain)
            setString(request, ParamKeyDefine.name, self.node)
            self.info("<NodeService>request leave domain '%s' to '%s'..."%(
                self.domain, self.domain_server))
            self.sendMessage(request, self.domain_server)
        

    def __onLeaveDomainResponse(self, response, sender):        
        if not response.success:
            self.console("leave domain fail")
            self.error("leave domain fail")
        else:
            self.console("leave domain success")
            self.info("leave domain success")
            self.onDomainLeft()
            self.domain_server = ""
            self.domain_connected = False
            
    def __onMessageReceived(self, msg, sender):
        if msg.type == AppMessage.EVENT:
            return self.handleEventMessage(msg, sender)
        elif msg.type == AppMessage.REQUEST:
            return self.handleRequestMessage(msg, sender)
        elif msg.type == AppMessage.RESPONSE:
            return self.handleResponseMessage(msg, sender)

    def __onServiceAvailable(self, service_name, service_ip, serivce_port, request_ip):
        if "" == request_ip:
            ##from notify
            self.domain_service.query()
##            self.info("<NodeService>service notifyed, query domain service immediately")
            return
        if not self.transport_established:
            ##continue service startup
            self.console("<NodeService>domain service available('%s'@'%s:%d'),establish transport with local ip '%s'"%(
                service_name, service_ip, serivce_port, request_ip))
            self.info("<NodeService>domain service available('%s'@'%s:%d'),establish transport with local ip '%s'"%(
                service_name, service_ip, serivce_port, request_ip))

            self.local_ip = request_ip
            if not self.transport.bind(self.local_ip, self.start_port, self.port_range):
                self.console("bind service to ip address '%s' fail"%self.local_ip)
                self.critical("bind service to ip address '%s' fail"%self.local_ip)
##                self.domain_service.stop()
##                self.timer.stop()
                return 
            self.local_port = self.transport.getListenPort()
            self.console("bind service success, service address '%s:%d'"%(self.local_ip, self.local_port))
            self.info("bind service success, service address '%s:%d'"%(self.local_ip, self.local_port))
            if not self.transport.start():
                self.console("start transport fail")
                self.critical("start transport fail")
##                self.domain_service.stop()
##                self.timer.stop()
                return
            self.console("service %s.%s(version %s) started"%(self.domain, self.node, self.version))
            self.info("service %s.%s(version %s) started"%(self.domain, self.node, self.version))
            self.transport_established = True
            self.onTransportEstablished(self.local_ip, self.local_port)
            ##connect ds
            self.connectRemoteNode(service_name, NodeTypeDefine.data_server,service_ip, serivce_port)
            return
        
        else:
            ##transport established
            self.console("<NodeService>domain service available, '%s'(%s:%d)"%(
                service_name, service_ip, serivce_port))
            self.info("<NodeService>domain service available, '%s'(%s:%d)"%(
                service_name, service_ip, serivce_port))
            
            event = getEvent(EventDefine.service_available)
            setString(event, ParamKeyDefine.name, service_name)
            setString(event, ParamKeyDefine.ip, service_ip)
            setUInt(event, ParamKeyDefine.port, serivce_port)
            self.sendMessageToSelf(event)

    def __handleServiceAvailable(self, service_name, remote_ip, remote_port, sender):
        if (self.type != NodeTypeDefine.data_server) and (not self.domain_connected):
            self.connectRemoteNode(service_name, NodeTypeDefine.data_server,remote_ip, remote_port)            
        
    def __onDataServerDisconnected(self, server_name):
        if self.type != NodeTypeDefine.data_server:
            self.domain_connected = False
            self.domain_server = ""
            self.info("<NodeService>data server disconnected, try resume in %d seconds..."%(self.service_check_interval))
            self.__enableServiceCheck() 
        
    def __onCheckService(self):
        self.info("<NodeService>check service...")
        self.domain_service.query()

    def __disableServiceCheck(self):        
        if 0 != self.service_check_timer:
            self.clearTimer(self.service_check_timer)

    def __enableServiceCheck(self):
        event = getEvent(EventDefine.service_check)
        self.service_check_timer = self.setLoopTimedEvent(event, self.service_check_interval) 

    def __onConnectResponse(self, reponse, sender):
        if not reponse.success:
            self.warn("<NodeService>connect node fail")
            return
        entry = self.node_map[sender]
        if not entry.connected:
            entry.connected = True
##            self.info("<NodeService>connect remote node success, '%s' at '%s:%d'"%(
##                entry.name, entry.ip, entry.port))
            
            ##update service group
            if not self.service_group.has_key(entry.type):
                self.service_group[entry.type] = [entry.name]
            elif entry.name not in self.service_group[entry.type]:
                ##new service
                self.service_group[entry.type].append(entry.name)
                
            ##notify connected
            event = getEvent(EventDefine.channel_connected)
            setString(event, ParamKeyDefine.node_name, entry.name)
            setUInt(event, ParamKeyDefine.node_type, entry.type)
            setString(event, ParamKeyDefine.ip, entry.ip)
            setUInt(event, ParamKeyDefine.port, entry.port)
            self.sendMessageToSelf(event)        
    
    def __onConnectRequest(self, message, sender):
        entry = self.node_map[sender]
        if not entry.connected:
            entry.domain = getString(message, ParamKeyDefine.domain)
            entry.name = getString(message, ParamKeyDefine.name)
            entry.type = getUInt(message, ParamKeyDefine.type)
            entry.ip = getString(message, ParamKeyDefine.ip)
            entry.port = getUInt(message, ParamKeyDefine.port)
            entry.connected = True
            ##update service group
            if not self.service_group.has_key(entry.type):
                self.service_group[entry.type] = [entry.name]
            elif entry.name not in self.service_group[entry.type]:
                ##new service
                self.service_group[entry.type].append(entry.name)
            
##            self.info("<NodeService>connect by remote node success, '%s.%s' at '%s:%d'"%(
##                entry.domain, entry.name, entry.ip, entry.port))
            ##notify connected only once
            event = getEvent(EventDefine.channel_connected)
            setString(event, ParamKeyDefine.node_name, entry.name)
            setUInt(event, ParamKeyDefine.node_type, entry.type)
            setString(event, ParamKeyDefine.ip, entry.ip)
            setUInt(event, ParamKeyDefine.port, entry.port)
            self.sendMessageToSelf(event)

        ##send response
        response = getResponse(RequestDefine.connect_node)
        response.success = True
        self.sendMessage(response, entry.name) 

    def __onDisconnectResponse(self, reponse, sender):
        if not reponse.success:
            self.warn("<NodeService>disconnect node fail, remote node '%s'"%(sender))
            return
##        self.info("<NodeService>disconnect node success, remote node '%s'"%(sender))
        self.deallocateNode(sender)
        
    def __onDisconnectRequest(self, message, sender):
        if not self.node_map.has_key(sender):
            self.warn("<NodeService>disconnect by remote node fail, invalid node '%s'"%(sender))
            return
##        self.info("<NodeService>disconnect by remote node success, node name'%s'"%(sender))
        response = getResponse(RequestDefine.disconnect_node)
        response.success = True
        self.sendMessage(response, sender)
        
        entry = self.node_map[sender]
               
                
        ##notify disconnected
        event = getEvent(EventDefine.channel_disconnected)
        setString(event, ParamKeyDefine.node_name, entry.name)
        setUInt(event, ParamKeyDefine.node_type, entry.type)
        self.sendMessageToSelf(event)
        
        self.deallocateNode(sender)

    def modifyService(self, service_name, domain):
        if self.config_proxy is not None:
            self.config_proxy.modifyService(service_name, domain)

    def modifyServer(self, name, rack):  
        if self.config_proxy is not None:
            self.config_proxy.modifyServer(name, rack)
        
if __name__ == '__main__':
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)
    
    server_ip = "192.168.66.204"
##    server_ip = "192.168.66.103"
    server_port = 5600
##    client_ip = "192.168.66.102"
    client_ip = "192.168.66.203"

    
    if len(sys.argv) > 1:
        ##server
        server = NodeService(NodeTypeDefine.data_server, "dataserver", "example", server_ip, 5600, 1)
        server.start()
        time.sleep(10)
        server.stop()
        
    else:
        ##client
        client = NodeService(NodeTypeDefine.node_client, "client", "example", client_ip)
        client.start()
        client.connectRemoteNode("dataserver", NodeTypeDefine.data_server, server_ip, server_port)
        time.sleep(10)
        client.stop()      
