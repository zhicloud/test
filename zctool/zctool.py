#!/usr/bin/python

from cmd import *
from common import *
from zcparameter import *

import logging
import logging.handlers
from test_service import *
from threading import *
from service.message_define import *

import os
import ConfigParser

from datetime import *  
import time


"""
****************************************************
this is a mode of zhicloud cloud manage  platform. 
Date: 2014.06.20
****************************************************
"""
#global var define.
global root
root = None
global finished_event
finished_event = None

#call back function of service.
def onTestFinished(passed):
    global root
    if passed:
        root.info("test passed")
    else:
        root.info("test failed")
            
    global finished_event
    finished_event.set()
    
#CmdInterfaceLine Define.    
class ZhiCloudMgtCmd(Cmd):
    """
    define the cmd function.
    """
    do_result = None
    root = None
    global service
    service = None

    def __del__(self):
        global service
        global finished_event
        if service != None:
            service.stop()
            finished_event.clear()
        
    def do_test(self,argc):
        """
        do_test:just test.
        """
        print "test ok." + argc

    def do_quit(self,argc):
        """
        do_quit:quit from command interface while run quit().
        return: 1
        @type: int
        """
        return 1

    def do_exit(self,argc):
        """
        do_exit:exit from command interface while run quit().
        return: 1
        @type: int
        """
        return 1

    def do_EOF(self,argc):
        """
        do_EOF:quit from command interface while run ctrl+d.
        return: 1
        @type: int
        """
        return 1
    
    def emptyline(self):
        """
        emptyline:nothing to do while run null line.
        """
        pass

    def do_help(self,argc):
        """
        help: command help.
        eg:help zctool,help join.
        """
        try:
            if argc == "":
                print "parameter is None,please check it."
            else:
                argc = argc.split()
                config = ConfigParser.ConfigParser()
                helppath = os.path.join(os.getcwd(),"data","help.ini")
                config.readfp(open(helppath))
                help_info = config.get("ZhiCloud_Hlep",argc[0])
                print help_info
        except:
            print "Can't read help informaion from config."

    def do_zctool(self,argc):
        """
        zctool:connect a data service.
        @argc include 7 parameter,ip/-d/data service name/group ip/group port.
                        
        @param ip: ip of localhost,default.
        @type ip: string

        @param domain: domain name.
        @type domain: string
        
        @param group_ip: ip of group.
        @type group_ip: string
        
        @param group_port: port of group.
        @type group_port: int

        eg:zctool 172.16.1.25 -d test -ip 224.5.5.5 -port 5666
        """
        if argc == "":
            print "Err: Pls input parameters."
        else:
            argc = argc.split()
            if len(argc) != 7:
                print "Err: parameter number error,need 7 parameters. Pls check it."
            else:
                if argc[1] != "-d" or argc[3] != "-ip" or argc[5] != "-port":
                    print "Err: parameter format error."
                else:
                    #set logging format
                    global root
                    global finished_event
                    global service
                    
                    handler = logging.StreamHandler()
                    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
                    handler.setFormatter(formatter)
                    logging.getLogger("task")
                    root = logging.getLogger()
                    root.addHandler(handler)
                    logging.info('Set logger success.')
                    
                    finished_event = threading.Event()
                    #connect data service.
                    try:
                        dt = datetime.now()
                        dtemp = '(%Y%m%d-%H%M%S): ' , dt.strftime( '%y%m%d-%I%M%S' )
                        nodename = dtemp[1]
                    except:
                        nodename = "000000"
                        
                    try:
                        
                        service = TestService(nodename,
                                              argc[2],
                                              argc[0],
                                              argc[4],
                                              int(argc[6]),
                                              "","","", None)

                        service.bindCallback(onTestFinished)
                        service.start()
                        
                        finished_event.wait(timeout=7)
                        finished_event.clear()
                        
                        print "Execute command success."
                    #except:
                        #print "Execute fail, goto except now."
                    except ZCException as e:
                        print "zctool exception:%s" % e.argc
                                                         
    
    def do_join(self,argc):
        """
        do_join:connect the data service.
        @argc include 1 parameter: ds ip.
        
        @param ip: ds ip.
        @type ip: string
        eg:join 172.168.6.4
        """
        if argc == "":
            print "Pls input parameter."
        else:
            argc = argc.split()
            if len(argc) != 1:
                print "Err: parameter number error,just need 1 parameters. Pls check it."
            else:
                try:
                    global service
                    global finished_event                   
                    finished_event = threading.Event()
                    if service != None:
                        service.bindCallback(onTestFinished)
                        
                        service.connectRemoteNode("data_server",
                                                  NodeTypeDefine.data_server,
                                                  argc[0],
                                                  5600)
                    finished_event.wait(timeout=10)
                    finished_event.clear()
                    print "Execute command success."
                except:
                    print "Execute fail, goto except now."

    def do_leave(self,argc):
        """
        do_cmdname: leave the domain
        @param: None.
        eg:leave data_server
        """
        try:
            global service
            global finished_event
            if service != None:                                
                service.disconnectRemoteNode("data_server")
                service.case_manager.clearTestCase()
                service.stop()
                finished_event.clear()
            print "Execute command success."
        except:
            print "Execute fail, goto except now."                           

    def do_query_service(self,argc):
        """
        query service,include control service,node client,storage service.
		*************query_service param***************
		 -t(*) : type of query:
		     2 : control service.
		     3 : node client.
		     4 : storage service.
		 -g    : group of sercice,default:default.
		***********************************************
	eg:query_service -t 3
        """
        argc=argc.split()
        if param_image(param_query_service,argc)==CHECK_PASS:
            try:
               global service
               global finished_event
               finished_event.clear()
               finished_event = threading.Event()
               if service != None:               
                   service.case_manager.clearTestCase()
                   service.case_manager.addTestCase(TestCase("query_service", query_service))
                   enviro = service.case_manager.getParam()
                   enviro["control_server"] = service.zc_node_name
                   enviro["type"]=int(param_query_service['-t'])
                   enviro["group"]=param_query_service['-g']
                   service.beginTest()
                   
                   finished_event.wait()
                   finished_event.clear()
                   #test result:
                   if service.case_manager.test_result == CMDRUN_PASS:
                       print "Execute command success."
                   else:
                       print "Execute command fail."
            except:
               print "Execute fail, goto except now."

    def do_query_compute_pool(self,argc):
        """
        query comuter resource pool information.

		********** query_compute_pool param ***********
		 None.
		***********************************************
	eg:query_compute_pool
        """
        try:
            global service
            global finished_event
            
            finished_event.clear()
            finished_event = threading.Event()
            if service != None:               
                service.case_manager.addTestCase(TestCase("query_compute_pool", query_compute_pool))
                enviro = service.case_manager.getParam()
                enviro["control_server"] = service.zc_node_name
                service.beginTest()
                finished_event.wait()
                finished_event.clear()
                   
                #test result:
                if service.case_manager.test_result == CMDRUN_PASS:
                    print "Execute command success."
                else:
                    print "Execute command fail."
        except:
            print "Execute fail, goto except now."

    def do_create_compute_pool(self,argc):
        """
        add node client to comuter resource pool.

		********* create_compute_pool param **********
		 -p(*)    : computer resource pool id.
		 -name(*) : node client name.
		***********************************************
        eg:add_compute_resource -p 060b8aff6fb04ca092534c6540425776 -name node_client_047d7b87143d
        """
        argc = argc.split()
        if param_image(param_create_compute_pool,argc)==CHECK_PASS:
            try:
               global service
               if service != None:               
                   service.case_manager.clearTestCase()
                   enviro = service.case_manager.getParam()
                   service.case_manager.addTestCase(TestCase("create_compute_pool", create_compute_pool))
                   
                   enviro["name"] =param_create_compute_pool['-name']
                   enviro["network_type"] =param_create_compute_pool['-nt']
                   enviro["network"] =param_create_compute_pool['-nw']
                   enviro["disk_type"] =param_create_compute_pool['-dt']
                   enviro["disk_source"] =param_create_compute_pool['-ds']
                                     
                   enviro["control_server"] = service.zc_node_name
                   service.beginTest()

                   #wait threading
                   finished_event.wait()
                   finished_event.clear()
                   
                   if service.case_manager.test_result == CMDRUN_PASS:
                       print "Execute command success."
                   else:
                       print "Execute command fail."
            except:
                print "Execute fail, goto except now."
            #except ZCException as e:
                #print "zctool exception:%s" % e.argc
                
    def do_delete_compute_pool(self,argc):
        """
        delete a computer pool.

	    ****delete_compute_pool param*****
                -id(*) : compute pool uuid.
            ***********************************
        eg:delete_compute_pool -id 060b8aff6fb04ca092534c6540425776
        """
        argc = argc.split()
        if param_image(param_delete_compute_pool,argc)==CHECK_PASS:
            try:
               global service
               if service != None:               
                   service.case_manager.clearTestCase()
                   enviro = service.case_manager.getParam()
                   service.case_manager.addTestCase(TestCase("delete_compute_pool", delete_compute_pool))
                   
                   enviro["uuid"] =param_delete_compute_pool['-id']
                                     
                   enviro["control_server"] = service.zc_node_name
                   service.beginTest()

                   #wait threading
                   finished_event.wait()
                   finished_event.clear()
                   
                   if service.case_manager.test_result == CMDRUN_PASS:
                       print "Execute command success."
                   else:
                       print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_modify_compute_pool(self,argc):
        """
        modify a computer pool informationl.
        ****modify_compute_pool param*****
            '-id' : computer pool uuid
            -name(*) : compute resourece name.
            '-nt' : network type
            '-nw' : network,
            '-dt' : disk type,
            '-ds' : disk_source
        ***********************************
        eg:modify_compute_pool -id 060b8aff6fb04ca092534c6540425776 -name abcdefg
        """
        argc = argc.split()
        if param_image(param_modify_compute_pool,argc)==CHECK_PASS:
            try:
               global service
               if service != None:               
                   service.case_manager.clearTestCase()
                   enviro = service.case_manager.getParam()
                   service.case_manager.addTestCase(TestCase("modify_compute_pool", modify_compute_pool))

                   enviro["uuid"] = param_modify_compute_pool['-id']
                   enviro["name"] = param_modify_compute_pool['-name']
                   enviro["network_type"] = param_modify_compute_pool['-nt']
                   enviro["network"] = param_modify_compute_pool['-nw']
                   enviro["disk_type"] = param_modify_compute_pool['-dt']
                   enviro["disk_source"] = param_modify_compute_pool['-ds']
                                     
                   enviro["control_server"] = service.zc_node_name
                   service.beginTest()

                   #wait threading
                   finished_event.wait()
                   finished_event.clear()
                   
                   if service.case_manager.test_result == CMDRUN_PASS:
                       print "Execute command success."
                   else:
                       print "Execute command fail."
            except:
                print "Execute fail, goto except now."
            #except ZCException as e:
                #print "zctool exception:%s" % e.argc
                

    def do_add_compute_resource(self,argc):
        """
        add node client to comuter resource pool.

		********* add_compute_resource param **********
		 -p(*)    : computer resource pool id.
		 -name(*) : node client name.
		***********************************************
        eg:add_compute_resource -p 060b8aff6fb04ca092534c6540425776 -name node_client_047d7b87143d
        """
        argc = argc.split()
        if param_image(param_add_compute_resource,argc)==CHECK_PASS:
            try:
               global service
               if service != None:               
                   service.case_manager.clearTestCase()
                   enviro = service.case_manager.getParam()
                   enviro["pool"] =param_add_compute_resource['-p']
                   enviro["resource"] =param_add_compute_resource['-name']
                   service.case_manager.addTestCase(TestCase("add_compute_resource", add_compute_resource))
                   enviro["control_server"] = service.zc_node_name
                   service.beginTest()

                   #wait threading
                   finished_event.wait()
                   finished_event.clear()
                   
                   if service.case_manager.test_result == CMDRUN_PASS:
                       print "Execute command success."
                   else:
                       print "Execute command fail."
            except:
                print "Execute fail, goto except now."          

    def do_remove_compute_resource(self,argc):
        """
        remove_compute_resource:remove a compute resource
        @param: None.
        remove node client from comuter resource pool.

		********* remove_compute_resource param *********
		 -p(*)    : computer resource pool id.
		 -name(*) : node client name.
		*************************************************
        eg:remove_compute_resource -p 060b8aff6fb04ca092534c6540425776 -name node_client_047d7b87143d
        """
        argc = argc.split()
        if param_image(param_remove_compute_resource,argc)==CHECK_PASS:
            try:
               global service
               if service != None:               
                   service.case_manager.clearTestCase()
                   enviro = service.case_manager.getParam()
                   enviro["pool"] =param_remove_compute_resource['-p']
                   enviro["resource"] =param_remove_compute_resource['-name']
                   service.case_manager.addTestCase(TestCase("remove_compute_resource", remove_compute_resource))
                   enviro["control_server"] = service.zc_node_name
                   service.beginTest()

                   #wait threading
                   finished_event.wait()
                   finished_event.clear()
                    
                   if service.case_manager.test_result == CMDRUN_PASS:
                       print "Execute command success."
                   else:
                       print "Execute command fail."
            except:
                print "Execute fail, goto except now."


    def do_query_compute_resource(self,argc):
        """
        query_compute_resource:query compute resource  information.	
		*************** query_compute_resource param ****************
		 -p(*)   : target compute pool id.

		**************************************************
        eg:query_compute_resource -p 060b8aff6fb04ca092534c6540425776 
        """
        argc = argc.split()
        if param_image(param_query_compute_resource,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("query_compute_resource", query_compute_resource))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    #essential parameter 
                    enviro["pool"] = param_query_host['-p']

                    #start Test
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."



    def do_query_iso_image(self,argc):
        """
        query iso image information.

		********** query_iso_image param **************
		 None.
		***********************************************
        eg: query_iso_image
        """
        try:
            global service
            global finished_event
            finished_event.clear()
            finished_event = threading.Event()
            if service != None:
                #add TestCase to CaseManager
                service.case_manager.clearTestCase()
                service.case_manager.addTestCase(TestCase("query_iso_image", query_iso_image))
                #parameter initail and begin test.
                enviro = service.case_manager.getParam()
                enviro["control_server"] = service.zc_node_name
                service.beginTest()
                #wait threading
                finished_event.wait()
                finished_event.clear()
                
                #test result:
                if service.case_manager.test_result == CMDRUN_PASS:
                    print "Execute command success."
                else:
                    print "Execute command fail."
        except:
            print "Execute fail, goto except now."

    def do_upload_iso_image(self,argc):
        """
        do_upload_iso_image: upload the iso image to storage service.
        @param: None.
        upload iso image from local to storage service.

		************** upload_iso_image param ***********
		 -p(*)   : path of upload iso image.
		 -name(*): disk image name.
		 -des    : describe of disk image.defalt:''
		************************************************
        eg: upload_iso_image -p E:\\Robot_Project\\ISO\\CentOS-6.4-x86_64-minimal.iso -name Centos6.4_x86_64 -des Centos6.4_x86_64
            upload_iso_image -p //var//iso_images//CentOS-6.5-x86_64-bin-DVD.iso -name Centos6.5_x86_64 -des Centos6.5_x86_64
        """
        argc = argc.split()
        if param_image(param_upload_iso_image,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("upload_iso_image", upload_iso_image))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["iso_file_path"] = param_upload_iso_image['-p']
                    enviro["iso_file_name"] = param_upload_iso_image['-name']
                    enviro["iso_describe"] = param_upload_iso_image['-des']
                    #begin test.
                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                        
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."
                   

    def do_modify_iso_image(self,argc):
        """
        modify_iso_image: Get the iso image information

		************** modify_iso_image param ***********
		 -name(*): new iso image name.
		 -id(*)  : iso image id of modify.
		 -des    : describe of iso image.default:''
		**************************************************
        eg: modify_iso_image -name CentOS6.5 -id 7dc876e854884a5781d1706f13a8448d
            modify_iso_image -name image01 -id e3990406-5f3e-4fe7-8b9c-e408abc2e5b8 -des abc
        """
        argc = argc.split()
        if param_image(param_modify_iso_image,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("modify_iso_image", modify_iso_image))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["iso_image_name"] = param_modify_iso_image['-name']
                    enviro["iso"] = param_modify_iso_image['-id']
                    enviro["iso_image_description"] = param_modify_iso_image['-des']

                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
                        
            except:
                print "Execute fail, goto except now."

    def do_delete_iso_image(self,argc):
        """
        delete_iso_image: Get the iso image information

		************** delete_iso_image param ***********
		 -id(*)   : iso image id of delete.
		*************************************************
        eg: delete_iso_image -id 7dc876e854884a5781d1706f13a8448d
        """
        argc = argc.split()
        if param_image(param_delete_iso_image,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("delete_iso_image", delete_iso_image))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["iso"] = param_delete_iso_image['-id']

                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
                        
            except:
                print "Execute fail, goto except now."

        
    def do_query_disk_image(self,argc):
        """
        query_disk_image: Get the iso image information
		
		********** query_disk_image param **************
		 None.
		************************************************
        eg: query_disk_image
        """
        try:
            global service
            global finished_event
            finished_event.clear()
            finished_event = threading.Event()
            if service != None:
                #add TestCase to CaseManager
                service.case_manager.clearTestCase()
                service.case_manager.addTestCase(TestCase("query_disk_image", query_disk_image))
                #parameter initail and begin test.
                enviro = service.case_manager.getParam()
                enviro["control_server"] = service.zc_node_name
                service.beginTest()
                #wait threading
                finished_event.wait()
                finished_event.clear()
                
                #test result:
                if service.case_manager.test_result == CMDRUN_PASS:
                    print "Execute command success."
                else:
                    print "Execute command fail."
                    
        except:
            print "Execute fail, goto except now."

    def do_create_disk_image(self,argc):
        """
        create_disk_image: Get the iso image information
        create a disk image from a exist host.
		
		************** create_disk_image param ***********
		 -name(*): disk image name.
		 -id(*)  : host id of create disk.
		 -des    : describe of disk image,default:''.
		 -tag    : tag of disk image.
		**************************************************
        eg: create_disk_image -name diskimage01 -id e3990406-5f3e-4fe7-8b9c-e408abc2e5b8
            create_disk_image -name diskimage01 -id e3990406-5f3e-4fe7-8b9c-e408abc2e5b8 -des abc -tag linux,64bit
        """
        argc = argc.split()
        if param_image(param_create_disk_image,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("create_disk_image", create_disk_image))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["disk_image_name"] = param_create_disk_image['-name']
                    enviro["host"] = param_create_disk_image['-id']
                    enviro["disk_image_description"] = param_create_disk_image['-des']
                    enviro["disk_image_tag"] = param_create_disk_image['-tag']
        
                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_modify_disk_image(self,argc):
        """
        modify_disk_image: Get the iso image information
        modify the disk image information.

		************** modify_disk_image param ***********
		 -name(*): disk image name.
		 -id(*)  : disk image id.
		 -des     : describe of disk image,default:''.
		**************************************************
        eg: modify_disk_image -name diskimage01 -id e3990406-5f3e-4fe7-8b9c-e408abc2e5b8
            modify_disk_image -name diskimage01 -id e3990406-5f3e-4fe7-8b9c-e408abc2e5b8 -des abc
        """
        argc = argc.split()
        if param_image(param_modify_disk_image,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("modify_disk_image", modify_disk_image))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["disk_image_name"] = param_modify_disk_image['-name']
                    enviro["host"] = param_modify_disk_image['-id']
                    enviro["disk_image_description"] = param_modify_disk_image['-des']
                    enviro["tag"] = param_modify_disk_image['-tag']

                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            #except:
                #print "Execute fail, goto except now."
            except ZCException as e:
                print "zctool exception:%s" % e.argc

    def do_delete_disk_image(self,argc):
        """
        delete_disk_image: delete the disk image.

		************** delete_disk_image param ***********
		 -id(*) : disk image id.
		**************************************************
        eg: delete_disk_image -id e3990406-5f3e-4fe7-8b9c-e408abc2e5b8
        """
        argc = argc.split()
        if param_image(param_delete_disk_image,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("delete_disk_image", delete_disk_image))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["disk"] = param_delete_disk_image['-id']

                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."


    def do_query_host(self,argc):
        """
        query_host:query host information.	
		*************** query_host param ****************
		 -p(*)   : pool id.
		 -d      : system disk size(GB).
		 -mid    : image id,default:''.
		 -au     : auto start,0:false,1:true,default:'0'.
		 -port      : port,all:tcp&udp,or tcp/udp,default:'tcp:80,tcp:22'.
		 -ib     : inbound width(MB),default:'2'.
		 -ob     : outbound width(MB),default:'2'.
		**************************************************
        eg:query_host -p 060b8aff6fb04ca092534c6540425776 
        """
        argc = argc.split()
        if param_image(param_query_host,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("query_host", query_host))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    #essential parameter 
                    enviro["pool"] = param_query_host['-p']
                    
                    #optional parameters
                    if param_query_host['-au'] == '1':
                        enviro["auto"] = True
                    else:
                        enviro["auto"] = False

                    enviro["disk_image_uuid"] = param_query_host['-mid']
                    enviro["disk_size"] = param_query_host['-d']                   
                    enviro["port"] = port_dealwith(param_query_host['-port'])
                    enviro["inbound"] = param_query_host['-ib']
                    enviro["outbound"] = param_query_host['-ob']
                    #start Test
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_query_host_info(self,argc):
        """
        query_host:query host information.	
		*************** query_host param ****************
		 -p(*)   : pool id.
		 -d      : system disk size(GB).
		 -mid    : image id,default:''.
		 -au     : auto start,0:false,1:true,default:'0'.
		 -port      : port,all:tcp&udp,or tcp/udp,default:'tcp:80,tcp:22'.
		 -ib     : inbound width(MB),default:'2'.
		 -ob     : outbound width(MB),default:'2'.
		**************************************************
        eg:query_host -p 060b8aff6fb04ca092534c6540425776 
        """
        argc = argc.split()
        if param_image(param_query_host_info,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("query_host_info", query_host_info))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    #essential parameter 
                    enviro["host"] = param_query_host_info['-id']
                    
                    #start Test
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."
    
    def do_create_host(self,argc):
        """
        do_create_host: create a new host.
        create a new host on cloud management.
		*************** create_host param ****************
		 -name(*): host name.
		 -p(*)   : pool id.
		 -c(*)   : cpu core.
		 -m(*)   : memory.
		 -d(*)   : system disk size(GB).
		 -w      : monitor password,default:'123456'.
		 -ui     : use disk image,0:false,1:true,default:'0'
		 -mid    : image id,default:''.
		 -ud     : use data disk,0:false,1:true,default:'0'.
		 -au     : auto start,0:false,1:true,default:'0'.
		 -port      : port,all:tcp&udp,or tcp/udp,default:'tcp:3389,tcp:22'.
		 -ds     : data disk size(GB),default:'0'.
		 -ib     : inbound width(MB),default:'2'.
		 -ob     : outbound width(MB),default:'2'.
		 **************************************************
        eg:create_host -name host_new02 -p 080fc149-66f4-4706-a795-e554a5dd306e -c 2 -m 512 -d 10 -w abcdef
        """
        argc = argc.split()
        if param_image(param_create_host,argc) == CHECK_PASS:
            try:
                global service
                global finished_event                   
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("create_host", create_host))
                        
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["host_name"] = param_create_host['-name']
                    enviro["pool"] = param_create_host['-p']
                    enviro["cpu_core"] = param_create_host['-c']
                    enviro["memory_size"] = param_create_host['-m']
                    enviro["system_disk_size"] = param_create_host['-d']
                    enviro["monitor_pwd"] = param_create_host['-w']

                    #optional parameter:
                    if param_create_host['-ui'] == '1':
                        enviro["use_image"] = True
                    else:
                        enviro["use_image"] = False

                    if param_create_host['-ud'] == '1':
                        enviro["user_data_disk"] = True
                    else:
                        enviro["user_data_disk"] = False

                    if param_create_host['-au'] == '1':
                        enviro["auto_start"] = True
                    else:
                        enviro["auto_start"] = False
                    enviro["port"] = port_dealwith(param_create_host['-port'])
                    enviro["image_id"] = param_create_host['-mid']
                    enviro["data_disk_size"] = param_create_host['-ds']
                    enviro["inbound_bandwidth"] = param_create_host['-ib']
                    enviro["outbound_bandwidth"] = param_create_host['-ob']
                    enviro["network"] = param_create_host['-net']
                    
                    service.beginTest()
                        
                    finished_event.wait()
                    finished_event.clear()
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."       

    
    def do_start_host(self,argc):
        """
        start_host:start a host.
        start a host.
		 *************** start_host param ****************
		 -id(*) : host id.
		 -iso   : iso image id.
		 -b     : boot,0:local,1:CDROM,default:'0'.
		**************************************************                        
        eg:start_host -id 306e19d9-ceb2-430d-8b4b-aea765f5ded4 -iso e14a6f50a92941fc96f1e0fa94ae5862
        """
        argc = argc.split()
        if param_image(param_start_host,argc) == CHECK_PASS:
            try:
                global service
                global finished_event                   
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("start_host", start_host))
                        
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["host"] = param_start_host['-id']
                    enviro["iso_id"] = param_start_host['-iso']
                    enviro["boot"] = param_start_host['-b']
                    #start test.
                    service.beginTest()
                        
                    finished_event.wait()
                    finished_event.clear()
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."              

    def do_delete_host(self,argc):
        """
        delete_host:delete a host.
		*************** delete_host param ****************
		 -id(*) : host id.
		**************************************************
        eg:delete_host -id 6f8d9ae7-fe2f-4869-838c-e591254e6f9b
        """        
        argc = argc.split()
        if param_image(param_delete_host,argc) == CHECK_PASS:
            try:
                global service
                global finished_event                   
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("delete_host", delete_host))
                        
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["host"] = param_delete_host['-id']
                    #start test.
                    service.beginTest()
                        
                    finished_event.wait()
                    finished_event.clear()
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."    

    def do_halt_host(self,argc):
        """
        halt_host:halt a host, shutdown the power of host.
		*************** halt_host param ******************
		 -id(*) : host id.
		**************************************************
        eg:halt_host -id 6f8d9ae7-fe2f-4869-838c-e591254e6f9b
        """
        argc = argc.split()
        if param_image(param_halt_host,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("halt_host", halt_host))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    #enviro["host"] = argc[1]
                    enviro["host"] = param_halt_host['-id']
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_stop_host(self,argc):
        """
        stop_host:stop a host.
		*************** stop_host param *****************
		 -id(*) : host id.
		*************************************************
        eg:stop_host -id 6f8d9ae7-fe2f-4869-838c-e591254e6f9b
        """
        argc = argc.split()
        if param_image(param_stop_host,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("stop_host", stop_host))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["host"] = param_stop_host['-id']
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."                       
            except:
                print "Execute fail, goto except now."

    def do_restart_host(self,argc):
        """
        restart_host:restart a host.
		*************** restart_host param *****************
		 -id(*) : host id.
		 -b(*):startup mode:0=hard disk;1=cd
                 -mid(*):uuid of image
		*************************************************
        eg:restart_host -id 6f8d9ae7-fe2f-4869-838c-e591254e6f9b -b 0 -mid 1sd59ae7-fe2f-4869-838c-e591254e6f9b
        """
        argc = argc.split()
        if param_image(param_restart_host,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("restart_host", restart_host))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["host"] = param_restart_host['-id']
                    enviro["mode"] = param_restart_host['-b']
                    enviro["image"] = param_restart_host['-mid']
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."                       
            #except:
                #print "Execute fail, goto except now."
            except ZCException as e:
                print "zctool exception:%s" % e.argc

    def do_modify_host(self,argc):
        """
        modify_host:@modify a host information.
		*************** modify_host param ***************
		 -id(*) :  host id.
		 -c(*)  :  cpu core.
		 -m(*)  :  memory.
		 -ds(*) :  data disk size(GB).
		 -w  :  monitor passwd,default:'123456'
		 -au :  auto start,0:false 1:true,default:'0'.
		 -p  :  port,default:'tcp:22,tcp:3389'.
		 -ib :  inbound width(MB),default:'2'.
		 -ob :  outbound width(MB),default:'2'.
		*************************************************
        eg:modify_host -id 7956c868-49b9-4de5-885f-efc23562cd1f -c 2 -m 1024 -ds 30 -w 123456
        """
        argc = argc.split()
        if param_image(param_modify_host,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("modify_host", modify_host))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    #essential parameter 
                    enviro["host"] = param_modify_host['-id']
                    enviro["cpu_core"] = param_modify_host['-c']
                    enviro["memory_size"] = param_modify_host['-m']
                    enviro["system_disk_size"] = param_modify_host['-ds']
                    enviro["monitor_pwd"] = param_modify_host['-w']
                    enviro["name"] = param_modify_host['-name']
                    
                    #optional parameters
                    if param_modify_host['-au'] == '1':
                        enviro["auto"] = True
                    else:
                        enviro["auto"] = False

                    enviro["port"] = port_dealwith(param_modify_host['-p'])
                    enviro["inbound"] = param_modify_host['-ib']
                    enviro["outbound"] = param_modify_host['-ob']
                    enviro["network"] = param_create_host['-net']
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            #except:
                #print "Execute fail, goto except now."
            except ZCException as e:
                print "zctool exception:%s" % e.argc


    def do_query_port_pool(self,argc):
        """
        query_port_pool:query the port pool information.
		*************** query_port_pool param *****************
		 None.
		*************************************************
        eg:query_port_pool
        """
        try:
            global service
            global finished_event
            finished_event = threading.Event()
            if service != None:
                service.case_manager.clearTestCase()
                service.case_manager.addTestCase(TestCase("query_port_pool", query_port_pool))
                    
                #parameter initail and begin test.
                enviro = service.case_manager.getParam()
                enviro["control_server"] = service.zc_node_name
                service.beginTest()
                    
                finished_event.wait()
                finished_event.clear()
                #test result:
                if service.case_manager.test_result == CMDRUN_PASS:
                    print "Execute command success."
                else:
                    print "Execute command fail."                       
        except:
            print "Execute fail, goto except now."        

    def do_delete_port_pool(self,argc):
        """
        delete_port_pool:create a port pool.
	*************** delete_port_pool param *****************
	    -id(*) : port pool uuid.
	*************************************************
        eg:delete_port_pool -id 31375fba19b64ea3b11effe6fc30e21a 
        """
        argc = argc.split()
        if param_image(param_delete_port_pool,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("delete_port_pool", delete_port_pool))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["id"] = param_delete_port_pool['-id']
                    
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."                       
            except:
                print "Execute fail, goto except now." 

    def do_create_port_pool(self,argc):
        """
        delete a port pool.
        ******create_port_pool param*******
          -name(*) : port pool name.
        ***********************************
        eg:create_port_pool -
        """
        argc = argc.split()
        if param_image(param_create_port_pool,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("create_port_pool", create_port_pool))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["name"] = param_create_port_pool['-name']
                    
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."                       
            except:
                print "Execute fail, goto except now."

    def do_query_port_resource(self,argc):
        """
        delete a port pool.
        ******query_port_resource param*******
             -p(*)  : the port pool id want to add.
             -ip(*) : start ip address.
             -r(*)  : ip number
        ***********************************
        eg:query_port_resource -p xxx 
        """
        argc = argc.split()
        if param_image(param_query_port_resource,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("query_port_resource", query_port_resource))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["pool"] = param_query_port_resource['-p']
                    
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."                       
            except:
                print "Execute fail, goto except now."


    def do_add_port_resource(self,argc):
        """
        delete a port pool.
        ******add_port_resource param*******
             -p(*)  : the port pool id want to add.
             -ip(*) : start ip address.
             -r(*)  : ip number
        ***********************************
        eg:add_port_resource -p xxx -ip 202.105.182.213 -r 10
        """
        argc = argc.split()
        if param_image(param_add_port_resource,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("add_port_resource", add_port_resource))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["pool"] = param_add_port_resource['-p']
                    enviro["ip"] = param_add_port_resource['-ip']
                    enviro["range"] = param_add_port_resource['-r']
                    
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."                       
            except:
                print "Execute fail, goto except now."

    def do_remove_port_resource(self,argc):
        """
        delete a port pool.
        ******remove_port_resource param*******
             -p(*)  : the port pool id want to add.
             -ip(*) : start ip address.
             -r(*)  : ip number
        ***********************************
        eg:remove_port_resource -p xxx -ip 202.105.182.213 -r 10
        """
        argc = argc.split()
        if param_image(param_remove_port_resource,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("remove_port_resource", remove_port_resource))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["pool"] = param_remove_port_resource['-p']
                    enviro["ip"] = param_remove_port_resource['-ip']
                    enviro["range"] = param_remove_port_resource['-r']
                    
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."                       
            except:
                print "Execute fail, goto except now."
    
    def do_query_forwarder_summary(self,argc):
        """
        query_forwarder_summary:query the port pool information.
		*************** query_forwarder_summary param *****************
		 None.
		*************************************************
        eg:query_forwarder_summary
        """
        try:
            global service
            global finished_event
            finished_event = threading.Event()
            if service != None:
                service.case_manager.clearTestCase()
                service.case_manager.addTestCase(TestCase("query_forwarder_summary", query_forwarder_summary))
                    
                #parameter initail and begin test.
                enviro = service.case_manager.getParam()
                enviro["control_server"] = service.zc_node_name
                service.beginTest()
                    
                finished_event.wait()
                finished_event.clear()
                #test result:
                if service.case_manager.test_result == CMDRUN_PASS:
                    print "Execute command success."
                else:
                    print "Execute command fail."                       
        except:
            print "Execute fail, goto except now."

    def do_query_forwarder(self,argc):
        """
       query forwarder information.
        *****query_forwarder param*******
          -t(*)  : forwarder type,0=mono,1=share,2=domain .
        ***********************************
        eg:query_forwarder -t 0
        """
        argc = argc.split()
        if param_image(param_query_forwarder,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("query_forwarder", query_forwarder))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["type"] = param_query_forwarder['-t']                  
                    
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."                       
            except:
                print "Execute fail, goto except now."

    def do_set_forwarder_status(self,argc):
        """
       set forwarder status,0=disable,1=enable.
        *****set_forwarder_status param*******
          -id(*)  : forwarder uuid .
          -s(*)   : forwarder status,0=disable,1=enable
        ***********************************
        eg:set_forwarder_status -id xxxxx -s 0
        """
        argc = argc.split()
        if param_image(param_set_forwarder_status,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("set_forwarder_status", set_forwarder_status))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["id"] = param_set_forwarder_status['-id']
                    enviro["status"] = param_set_forwarder_status['-s'] 
                    
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."                       
            except:
                print "Execute fail, goto except now."

    def do_get_forwarder(self,argc):
        """
        get forwarder information.
        *****get_forwarder param*******
          -id(*)  : forwarder uuid .
        ***********************************
        eg:get_forwarder -id xxxxx 
        """
        argc = argc.split()
        if param_image(param_get_forwarder,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("get_forwarder", get_forwarder))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["id"] = param_get_forwarder['-id']
                    
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."                       
            except:
                print "Execute fail, goto except now."
                
    def do_query_address_pool(self,argc):
        """
       query address pool information.
        *****query_address_pool param*******
          None.
        ***********************************
        eg:query_address_pool
        """
        argc = argc.split()
        try:
            global service
            global finished_event
            
            finished_event.clear()
            finished_event = threading.Event()
            if service != None:               
                service.case_manager.addTestCase(TestCase("query_address_pool", query_address_pool))
                enviro = service.case_manager.getParam()
                enviro["control_server"] = service.zc_node_name
                service.beginTest()
                finished_event.wait()
                finished_event.clear()
                   
                #test result:
                if service.case_manager.test_result == CMDRUN_PASS:
                    print "Execute command success."
                else:
                    print "Execute command fail."
        except:
            print "Execute fail, goto except now."

    def do_create_address_pool(self,argc):
        """
        create_address_pool: creat a new address_pool named by name.
		
		************** create_disk_image param ***********
		 -name(*): address pool name.
		**************************************************
        eg: create_address_pool -name testaddressport
        """
        argc = argc.split()
        if param_image(param_create_address_pool,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("create_address_pool", create_address_pool))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["address_pool_name"] = param_create_address_pool['-name']
        
                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."
    def do_delete_address_pool(self,argc):
        """
        delete_address_pool:delete delete an address pool.
	*************** delete_address_pool param *****************
	    -p(*) : address pool uuid.
	*************************************************
        eg:delete_address_pool -p 31375fba19b64ea3b11effe6fc30e21a 
        """
        argc = argc.split()
        if param_image(param_delete_address_pool,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("delete_address_pool",delete_address_pool))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["pool_uuid"] = param_delete_address_pool['-p']
                    
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."                       
            except:
                print "Execute fail, goto except now."
                
    def do_add_address_resource(self,argc):
        """
        add an address resource to pool.
        ******add_address_resource param*******
             -p(*)  : address pool uuid.
             -ip(*) : starting ip.
             -r(*)  : count of ip.
        ***********************************
        eg:add_address_resource
        """
        argc = argc.split()
        if param_image(param_add_address_resource,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("add_address_resource", add_address_resource))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["pool"] = param_add_address_resource['-p']
                    enviro["ip"] = param_add_address_resource['-ip']
                    enviro["range"] = param_add_address_resource['-r']
                    
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."                       
            #except:
                #print "Execute fail, goto except now."
            except ZCException as e:
                        print "zctool exception:%s" % e.argc
                        
    def do_remove_address_resource(self,argc):
        """
        emove an address resource from pool.
        ******remove_address_resource param*******
             -p(*)  : address pool uuid.
             -ip(*) : starting ip.
        ***********************************
        eg:remove_address_resource
        """
        argc = argc.split()
        if param_image(param_remove_address_resource,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("remove_address_resource", remove_address_resource))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["pool"] = param_remove_address_resource['-p']
                    enviro["ip"] = param_remove_address_resource['-ip']
                    
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."                       
            except:
                print "Execute fail, goto except now."
                
    def do_query_address_resource(self,argc):
        """
        query address resource in pool.
        *****query_address_resource*******
          -p(*): address pool uuid.
        ***********************************
        eg:query_address_resource
        """
        argc = argc.split()
        if param_image(param_query_address_resource,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
            
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:               
                    service.case_manager.addTestCase(TestCase("query_address_resource", query_address_resource))
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["pool"] = param_query_address_resource['-p']
                    service.beginTest()
                    finished_event.wait()
                    finished_event.clear()
                       
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_create_storage_pool(self,argc):
        """
        creat a storage pool with specific use.
		
		************** create_storage_pool ***********
		 -n(*): name of the storage_pool.
		**************************************************
        eg: eg:create_storage_pool -n storagepool-001
        """
        argc = argc.split()
        if param_image(param_create_storage_pool,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("create_storage_pool", create_storage_pool))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["storage_pool_name"] = param_create_storage_pool['-n']
        
                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."
                
    def do_query_storage_pool(self,argc):
        """
        query a storage pool with specific use.	
	************** create_storage_pool ***********
	None
	**************************************************
        eg: eg:query_storage_pool 
        """
        argc = argc.split()
        try:
            global service
            global finished_event
            
            finished_event.clear()
            finished_event = threading.Event()
            if service != None:               
                service.case_manager.addTestCase(TestCase("query_storage_pool", query_storage_pool))
                enviro = service.case_manager.getParam()
                enviro["control_server"] = service.zc_node_name
                service.beginTest()
                finished_event.wait()
                finished_event.clear()                 
                #test result:
                if service.case_manager.test_result == CMDRUN_PASS:
                    print "Execute command success."
                else:
                    print "Execute command fail."
        except:
            print "Execute fail, goto except now."
                
    def do_modify_storage_pool(self,argc):
        """
        modify an existed storage pool.
		
		************** modify_storage_pool ***********
		 -id(*): target storage pool uuid
		 -n(*): name of the storage_pool.
		**************************************************
        eg: 
        """
        argc = argc.split()
        if param_image(param_modify_storage_pool,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("modify_storage_pool", modify_storage_pool))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["storage_pool_id"] = param_modify_storage_pool['-id']
                    enviro["storage_pool_name"] = param_modify_storage_pool['-n']
        
                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."
            #except ZCException as e:
                #print "zctool exception:%s" % e.argc

    def do_delete_storage_pool(self,argc):
        """
        delete an existed storage pool.
        ******:delete_storage_pool param*******
         -id(*) target storage pool uuid
        ***********************************
        eg::delete_storage_pool -id xxx
        """
        argc = argc.split()
        if param_image(param_delete_storage_pool,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("delete_storage_pool", delete_storage_pool))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["storage_pool_id"] = param_delete_storage_pool['-id']
        
                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."
            #except ZCException as e:
                #print "zctool exception:%s" % e.argc

    def do_add_storage_resource(self,argc):
        """
        add the resource storage pool to pool.
        ******:add_storage_resource param*******
         -p(*) storage pool uuid.
         -n(*) storage pool name.
        ***********************************
        eg::add_storage_resource -p xx -n xx
        """
        argc = argc.split()
        if param_image(param_add_storage_resource,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("add_storage_resource", add_storage_resource))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["storage_pool_id"] = param_add_storage_resource['-p']
                    enviro["name"] = param_add_storage_resource['-n']
        
                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_remove_storage_resource(self,argc):
        """
        remove the resource storage pool to pool.
        ******:remove_storage_resource param*******
         -p(*) storage pool uuid.
         -n(*) storage pool name.
        ***********************************
        eg::remove_storage_resource -p xx -n xx
        """
        argc = argc.split()
        if param_image(param_remove_storage_resource,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("remove_storage_resource", remove_storage_resource))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["storage_pool_id"] = param_remove_storage_resource['-p']
                    enviro["name"] = param_remove_storage_resource['-n']
        
                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."
                
    def do_query_storage_resource(self,argc):
        """
        query the resource storage pool .
        ******:query_storage_resource param*******
         -p(*) storage pool uuid.
        ***********************************
        eg::query_storage_resource -p xx
        """
        argc = argc.split()
        if param_image(param_query_storage_resource,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("query_storage_resource", query_storage_resource))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["storage_pool_id"] = param_query_storage_resource['-p']
        
                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."
                
    def do_start_monitor(self,argc):
        """
        start monitor .
        ******:start_monitor param*******
         -n(*) storage resource name.
         -l    level.
        ***********************************
        eg::start_monitor -n xx -l 5
        """
        argc = argc.split()
        if param_image(param_start_monitor,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("start_monitor", start_monitor))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["storage_pool_name"] = param_start_monitor['-n']
                    enviro["monitor_level"] = param_start_monitor['-l']
        
                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_stop_monitor(self,argc):
        """
        stop monitor .
        ******:stop_monitor param*******
         -n(*) storage resource name.
         -l    level.
        ***********************************
        eg::stop_monitor -n xx -l 5
        """
        argc = argc.split()
        if param_image(param_stop_monitor,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("stop_monitor", stop_monitor))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["task_id"] = param_stop_monitor['-id']
        
                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            #except:
                #print "Execute fail, goto except now."
            except ZCException as e:
                print "zctool exception:%s" % e.argc

    def do_monitor_heart_beat(self,argc):
        """
        monitor_heart_beat .
        ******:monitor_heart_beat param*******
         -id(*) monitor task id.
        ***********************************
        eg::monitor_heart_beat -id xx
        """
        argc = argc.split()
        if param_image(param_monitor_heart_beat,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("monitor_heart_beat", monitor_heart_beat))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["task_id"] = param_monitor_heart_beat['-id']
        
                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_monitor_data(self,argc):
        """
        monitor_data .
        ******:monitor_data param*******
         -id(*) monitor task id.
        ***********************************
        eg::monitor_data -id xx
        """
        argc = argc.split()
        if param_image(param_monitor_data,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("monitor_data", monitor_data))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["task_id"] = param_monitor_data['-id']
                    enviro["level"] = param_monitor_data['-l']
        
                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."
                
    def do_add_forwarder(self,argc):
        """
        query address resource in pool.
        ********add_forwarder param********
            '-id' : target host uuid  
            '-t'  : target type,0=host, 1=disk   
            '-nt'  : network type,1:alone,2:share,  
            '-ns' : network source,address pool id 
        *********************************
        """
        argc = argc.split()
        if param_image(param_add_forwarder,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
            
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:               
                    service.case_manager.addTestCase(TestCase("add_forwarder", add_forwarder))
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["uuid"] = param_add_forwarder['-id']
                    enviro["type"] = param_add_forwarder['-t']
                    enviro["nettype"] = param_add_forwarder['-nt']
                    enviro["networksource"] = param_add_forwarder['-ns']
                    
                    service.beginTest()
                    finished_event.wait()
                    finished_event.clear()
                       
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_remove_forwarder(self,argc):
        """
        query address resource in pool.
        ********add_forwarder param********
            '-id' : target host uuid  
            '-t'  : target type,0=host, 1=disk   
            '-fid'  : forwarder id.  
        *********************************
        """
        argc = argc.split()
        if param_image(param_remove_forwarder,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
            
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:               
                    service.case_manager.addTestCase(TestCase("remove_forwarder", remove_forwarder))
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["uuid"] = param_remove_forwarder['-id']
                    enviro["type"] = param_remove_forwarder['-t']
                    enviro["fid"] = param_remove_forwarder['-fid']
                    
                    service.beginTest()
                    finished_event.wait()
                    finished_event.clear()
                       
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."
            #except ZCException as e:
                #print "zctool exception:%s" % e.argc

    def do_bind_domain(self,argc):
        """
        bind domain.
        ******bind_domain param*******
         -n(*): name of the domain.
         -t: type,0=host,1=balancer,default 0
         -id(*): host/balancer id
        ***********************************
        eg:bind_domain -n mydomain -t 0 -id xxx
        """
        argc = argc.split()
        if param_image(param_bind_domain,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
            
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:               
                    service.case_manager.addTestCase(TestCase("bind_domain", bind_domain))
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["name"] = param_bind_domain['-n']
                    enviro["type"] = param_bind_domain['-t']
                    enviro["uuid"] = param_bind_domain['-id']
                    
                    service.beginTest()
                    finished_event.wait()
                    finished_event.clear()
                       
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_unbind_domain(self,argc):
        """
        unbind domain.
        ******unbind_domain param*******
         -n(*): name of the domain.
        ***********************************
        eg:unbind_domain -n mydomain
        """
        argc = argc.split()
        if param_image(param_unbind_domain,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
            
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:               
                    service.case_manager.addTestCase(TestCase("unbind_domain", unbind_domain))
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["name"] = param_unbind_domain['-n']
                    
                    service.beginTest()
                    finished_event.wait()
                    finished_event.clear()
                       
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_query_domain_summary(self,argc):
        """
       query domain summary information.
        *****query_domain_summary param*******
          None.
        ***********************************
        eg:query_domain_summary
        """
        try:
            global service
            global finished_event
            
            finished_event.clear()
            finished_event = threading.Event()
            if service != None:               
                service.case_manager.addTestCase(TestCase("query_domain_summary", query_domain_summary))
                enviro = service.case_manager.getParam()
                enviro["control_server"] = service.zc_node_name
                service.beginTest()
                finished_event.wait()
                finished_event.clear()
                   
                #test result:
                if service.case_manager.test_result == CMDRUN_PASS:
                    print "Execute command success."
                else:
                    print "Execute command fail."
        except:
            print "Execute fail, goto except now."

    def do_query_domain_name(self,argc):
        """
        query domain name.
        ******query_domain_name param*******
         -ip(*): nallocated public ip.
        ***********************************
        eg:query_domain_name -ip 19 10.11.11.11
        """
        argc = argc.split()
        if param_image(param_query_domain_name,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
            
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:               
                    service.case_manager.addTestCase(TestCase("query_domain_name", query_domain_name))
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["ip"] = param_query_domain_name['-ip']
                    
                    service.beginTest()
                    finished_event.wait()
                    finished_event.clear()
                       
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_get_bound_domain(self,argc):
        """
        get domain name.
        ******get_bound_domain param*******
         -n(*): url name.
        ***********************************
        eg:get_bound_domain -n domain.zhicloue.com
        """
        argc = argc.split()
        if param_image(param_get_bound_domain,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
            
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:               
                    service.case_manager.addTestCase(TestCase("get_bound_domain", get_bound_domain))
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["name"] = param_get_bound_domain['-n']
                    
                    service.beginTest()
                    finished_event.wait()
                    finished_event.clear()
                       
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."               

    def do_disable_load_balancer(self,argc):
        """
        disable aload_balancer.
        ******disable_load_balancer param*******
         -id(*): url name.
        ***********************************
        eg:disable_load_balancer -id xxx
        """
        argc = argc.split()
        if param_image(param_disable_load_balancer,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
            
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:               
                    service.case_manager.addTestCase(TestCase("disable_load_balancer", disable_load_balancer))
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["uuid"] = param_disable_load_balancer['-id']
                    
                    service.beginTest()
                    finished_event.wait()
                    finished_event.clear()
                       
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."
            #except ZCException as e:
                #print "zctool exception:%s" % e.argc

    def do_delete_load_balancer(self,argc):
        """
        delete a load_balancer.
        ******delete_load_balancer param*******
         -id(*): url name.
        ***********************************
        eg:delete_load_balancer -id xxx
        """
        argc = argc.split()
        if param_image(param_delete_load_balancer,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
            
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:               
                    service.case_manager.addTestCase(TestCase("delete_load_balancer", delete_load_balancer))
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["uuid"] = param_delete_load_balancer['-id']
                    
                    service.beginTest()
                    finished_event.wait()
                    finished_event.clear()
                       
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."
            #except ZCException as e:
                #print "zctool exception:%s" % e.argc

    def do_query_balancer_summary(self,argc):
        """
       query balancer summary information.
        *****query_balancer_summary param*******
          None.
        ***********************************
        eg:query_balancer_summary
        """
        try:
            global service
            global finished_event
            
            finished_event.clear()
            finished_event = threading.Event()
            if service != None:               
                service.case_manager.addTestCase(TestCase("query_balancer_summary", query_balancer_summary))
                enviro = service.case_manager.getParam()
                enviro["control_server"] = service.zc_node_name
                service.beginTest()
                finished_event.wait()
                finished_event.clear()
                   
                #test result:
                if service.case_manager.test_result == CMDRUN_PASS:
                    print "Execute command success."
                else:
                    print "Execute command fail."
        except:
            print "Execute fail, goto except now."
        #except ZCException as e:
                #print "zctool exception:%s" % e.argc
            
    def do_attach_address(self,argc):
        """
        attach a IP to load_balancer.
        ******attach_address param*******
            '-id': balancer id,
            '-p': address pool id,
            '-t': type,0=forwarder, 1=balancer
            '-c': count of need.
        ***********************************
        eg:attach_address -id xxx -p xx -t 0 -c 5
        """
        argc = argc.split()
        if param_image(param_attach_address,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:               
                    service.case_manager.addTestCase(TestCase("attach_address", attach_address))
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name

                    enviro["uuid"] = param_attach_address['-id']
                    enviro["pool"] = param_attach_address['-p']
                    enviro["type"] = param_attach_address['-t']
                    enviro["count"] = param_attach_address['-c']
                    
                    service.beginTest()
                    finished_event.wait()
                    finished_event.clear()
                       
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_detach_address(self,argc):
        """
        detach a IP from load_balancer.
        ******detach_address param*******
            '-t': type,0=forwarder, 1=balancer
            '-id': balancer id,
            '-ip': list of public ip,
        ***********************************
        eg:detach_address -t 0 -ip 12.12.12.12 -id xxx
        """
        argc = argc.split()
        if param_image(param_detach_address,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:               
                    service.case_manager.addTestCase(TestCase("detach_address", detach_address))
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name

                    enviro["uuid"] = param_detach_address['-id']
                    enviro["ip"] = param_detach_address['-ip']
                    enviro["type"] = param_detach_address['-t']
                    
                    service.beginTest()
                    finished_event.wait()
                    finished_event.clear()
                       
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."
                
    def do_get_load_balancer(self,argc):
        """
        get load balancer information.
        ******get_load_balancer param*******
            '-id': balancer id,
        ***********************************
        eg:get_load_balancer -t 0 -ip 12.12.12.12 -id xxx
        """
        argc = argc.split()
        if param_image(param_get_load_balancer,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:               
                    service.case_manager.addTestCase(TestCase("get_load_balancer", get_load_balancer))
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name

                    enviro["uuid"] = param_get_load_balancer['-id']
                    
                    service.beginTest()
                    finished_event.wait()
                    finished_event.clear()
                       
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_query_load_balancer(self,argc):
        """
        query load balancer information.
        ******query_load_balancer param*******
            '-t': query type,0=mono, 1=share,2=domain
        ***********************************
        eg:query_load_balancer -t 0 
        """
        argc = argc.split()
        if param_image(param_query_load_balancer,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:               
                    service.case_manager.addTestCase(TestCase("query_load_balancer", query_load_balancer))
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name

                    enviro["type"] = param_query_load_balancer['-t']
                    
                    service.beginTest()
                    finished_event.wait()
                    finished_event.clear()
                       
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."
            #except ZCException as e:
                #print "zctool exception:%s" % e.argc

    def do_query_balancer_detail(self,argc):
        """
        query load balancer information.
        ******query_balancer_detail param*******
            '-id': balancer id
        ***********************************
        eg:query_balancer_detail -id xxx
        """
        argc = argc.split()
        if param_image(param_query_balancer_detail,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:               
                    service.case_manager.addTestCase(TestCase("query_balancer_detail", query_balancer_detail))
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name

                    enviro["uuid"] = param_query_balancer_detail['-id']
                    
                    service.beginTest()
                    finished_event.wait()
                    finished_event.clear()
                       
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_create_load_balancer(self,argc):
        """
        create a load balancer.
            ******create_load_balancer param*******
             -n(*): name of the load balancer
             -t(*): type of the load balancer 0:mono,1:share
             -port: list of the  ordered host port.
            ***********************************
        eg:
        """
        argc = argc.split()
        if param_image(param_create_load_balancer,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("create_load_balancer", create_load_balancer))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["balancer_name"] = param_create_load_balancer['-n']
                    enviro["type"] = param_create_load_balancer['-t']
                    enviro["port"] = param_create_load_balancer['-port']
      
        
                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."
                
    def do_add_balancer_node(self,argc):

        """
        add a  balancer node.
            ******add_balancer_node param*******
             -id(*): uuid of the load balancer
             -h(*): uuid of the host 
             -n(*): name of the host
             -ip(*): ip of the server
             -port(*): list of the ordered server port
            ***********************************
        eg:
        """
        argc = argc.split()
        if param_image(param_add_balancer_node,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("add_balancer_node", add_balancer_node))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["balancer_id"] = param_add_balancer_node['-id']
                    enviro["host_id"] = param_add_balancer_node['-h']
                    enviro["host_name"] = param_add_balancer_node['-n']
                    enviro["server_ip"] = param_add_balancer_node['-ip']
                    enviro["server_port"] = param_add_balancer_node['-port']
                   
      
        
                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_remove_balancer_node(self,argc):
        """
        remove a  balancer node.
            ******remove_balancer_node param*******
             -id(*): uuid of the load balancer
             -h(*): uuid of the host 
            ***********************************
        eg:
        """
        argc = argc.split()
        if param_image(param_remove_balancer_node,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("remove_balancer_node", remove_balancer_node))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["balancer_id"] = param_remove_balancer_node['-id']
                    enviro["host_id"] = param_remove_balancer_node['-h']

             
                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_modify_balancer_node(self,argc):
        """
        modify a  balancer node.
            ******modify_balancer_node param*******
             -id(*): uuid of the load balancer
             -h(*): uuid of the host 
             -ip(*): ip of the server
             -port(*): list of the ordered server port
            ***********************************
        eg:
        """
        argc = argc.split()
        if param_image(param_modify_balancer_node,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("modify_balancer_node", modify_balancer_node))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["balancer_id"] = param_modify_balancer_node['-id']
                    enviro["host_id"] = param_modify_balancer_node['-h']
                    enviro["server_ip"] = param_modify_balancer_node['-ip']
                    enviro["server_port"] = param_modify_balancer_node['-port']
                            
                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_enable_load_balancer(self,argc):
        """
        enable a load balancer..
            ******enable_load_balancer param*******
             -id(*): uuid of the load balancer

            ***********************************
        eg:
        """
        argc = argc.split()
        if param_image(param_enable_load_balancer,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event.clear()
                finished_event = threading.Event()
                if service != None:
                    #add TestCase to CaseManager
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("enable_load_balancer", enable_load_balancer))
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["balancer_id"] = param_modify_balancer_node['-id']
                            
                    service.beginTest()
                    #wait threading
                    finished_event.wait()
                    finished_event.clear()
                    
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."


    def do_query_server_room(self,argc):
        """
        query_server_room: Get the server room information
		
		********** query_server_room param **************
		 None.
		************************************************
        eg: query_server_room
        """
        try:
            global service
            global finished_event
            finished_event.clear()
            finished_event = threading.Event()
            if service != None:
                #add TestCase to CaseManager
                service.case_manager.clearTestCase()
                service.case_manager.addTestCase(TestCase("query_server_room", query_server_room))
                #parameter initail and begin test.
                enviro = service.case_manager.getParam()
                enviro["control_server"] = service.zc_node_name
                service.beginTest()
                #wait threading
                finished_event.wait()
                finished_event.clear()
                
                #test result:
                if service.case_manager.test_result == CMDRUN_PASS:
                    print "Execute command success."
                else:
                    print "Execute command fail."
                    
        except:
            print "Execute fail, goto except now."

    def do_query_server_rack(self,argc):
        """
        query_server_rack:query server rack information.	
		*************** query_server_rack param ****************
		 -id(*)   : target room  uuid.
		**************************************************
        eg:query_server_rack -id 060b8aff6fb04ca092534c6540425776 
        """
        argc = argc.split()
        if param_image(param_query_server_rack,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("query_server_rack", query_server_rack))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    #essential parameter 
                    enviro["room"] = param_query_server_rack['-id']

                    #start Test
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_query_server(self,argc):
        """
        query_server:query server information.	
		*************** query_server param ****************
		 -id(*)   : target rack uuid.
		**************************************************
        eg:query_server -id 060b8aff6fb04ca092534c6540425776 
        """
        argc = argc.split()
        if param_image(param_query_server,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("query_server", query_server))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    #essential parameter 
                    enviro["rack"] = param_query_server['-id']

                    #start Test
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."


    def do_attach_disk(self,argc):
        """
        attach_disk:attach disk to host	
		*************** attach_disk param ****************
		 -id(*)   : target rack uuid.
                 -dv(*)   :disk volume(Byte)
                 -dt(*)   :disk type(0=local 1=cloud)
                 -ds(*)   :disk resource,storage resouce uuid when disk type =cloud
                 -m(*)    :disk mode(0=raw)
		**************************************************
        eg:
        """
        argc = argc.split()
        if param_image(param_attach_disk,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("attach_disk", attach_disk))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    #essential parameter 
                    enviro["host"] = param_attach_disk['-id']
                    enviro["disk_volume"] = param_attach_disk['-dv']
                    enviro["disk_type"] = param_attach_disk['-dt']
                    enviro["disk_source"] = param_attach_disk['-ds']
                    enviro["mode"] = param_attach_disk['-m']

                    #start Test
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            #except:
                #print "Execute fail, goto except now."
            except ZCException as e:
                print "zctool exception:%s" % e.argc

    def do_detach_disk(self,argc):
        """
        detach_disk:detach disk from host	
		*************** detach_disk param ****************
		 -id(*)   : target rack uuid.
                 -index(*)   :disk index
		**************************************************
        eg:
        """
        argc = argc.split()
        if param_image(param_detach_disk,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("detach_disk", detach_disk))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    #essential parameter 
                    enviro["host"] = param_detach_disk['-id']
                    enviro["index"] = param_detach_disk['-index']

                    #start Test
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_query_device(self,argc):
        """
        query_device:query device information.	
		*************** query_device param ****************
		 -p(*)   : pool id.
		 -t      : query type (0=by pool).
		**************************************************
        eg:query_device -p 060b8aff6fb04ca092534c6540425776 
        """
        argc = argc.split()
        if param_image(param_query_device,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("query_device", query_device))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    #essential parameter 
                    enviro["pool"] = param_query_device['-p']
                    
                    #optional parameters
                    enviro["type"] = param_query_device['-t']
                    #start Test
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_create_device(self,argc):
        """
        do_create_device: create a new device.
        create a new device on cloud management.
		*************** create_device param ****************
                 -name(*)   : device name
                 -p(*)   :storage pool uuid
                 -dv(*): disk volume(GB)
                 -ps(*): page size(KB)
                 -rp(*): replication count
                 -a():need authentication,0:false,1:true,default:0
                 -et():encrypted transmit,0:false,1:true,default:0
                 -ct():compressed transmit,0:false,1:true,default:0
                 -es():encrypted storage,0:false,1:true,default:0
                 -cs():compressed storage,0:false,1:true,default:0
                 -pre():pre-allocate,0:false,1:true,default:0
                 -dt(*): disk type 0=standard(100IOPS),1=speed(4000IOPS)
                 -user():authentication account
                 -pwd(): authentication password
                 -crypt():encrypted key
                 -ssid():snapshot pool uuid
        eg: 
        """
        argc = argc.split()
        if param_image(param_create_device,argc) == CHECK_PASS:
            try:
                global service
                global finished_event                   
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("create_device", create_device))
                        
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["device_name"] = param_create_device['-name']
                    enviro["pool"] = param_create_device['-p']
                    enviro["disk_volume"] = param_create_device['-dv']
                    enviro["page_size"] = param_create_device['-ps']
                    enviro["replic"] = param_create_device['-rp']
                    enviro["disk_type"] = param_create_device['-dt']

                    #optional parameter:
                    if param_create_device['-a'] == '1':
                        enviro["authen"] = True
                    else:
                        enviro["authen"] = False

                    if param_create_device['-et'] == '1':
                        enviro["crypt_trans"] = True
                    else:
                        enviro["crypt_trans"] = False

                    if param_create_device['-ct'] == '1':
                        enviro["cmp_trans"] = True
                    else:
                        enviro["cmp_trans"] = False
                    if param_create_device['-es'] == '1':
                        enviro["crypt_stor"] = True
                    else:
                        enviro["crypt_stor"] = False
                    if param_create_device['-cs'] == '1':
                        enviro["cmp_stor"] = True
                    else:
                        enviro["cmp_stor"] = False
                    if param_create_device['-pre'] == '1':
                        enviro["pre_alloc"] = True
                    else:
                        enviro["pre_alloc"] = False
                    enviro["authen_user"] = param_create_device['-user']
                    enviro["authen_pwd"] = param_create_device['-pwd']
                    enviro["crypt"] = param_create_device['-crypt']                        
                    enviro["ss_uuid"] = param_create_device['-ssid'] 
                    
                    service.beginTest()
                        
                    finished_event.wait()
                    finished_event.clear()
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_delete_device(self,argc):
        """
        delete_device:delete target device .	
		*************** delete_device param ****************
		 -id(*)   : device  id.
		**************************************************
        eg:delete_device -p 060b8aff6fb04ca092534c6540425776 
        """
        argc = argc.split()
        if param_image(param_delete_device,argc) == CHECK_PASS:
            try:
                global service
                global finished_event
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("delete_device", delete_device))
                    
                    #parameter initail and begin test.
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    #essential parameter 
                    enviro["device"] = param_delete_device['-id']

                    #start Test
                    service.beginTest()
                    
                    finished_event.wait()
                    finished_event.clear()
                    #test result:
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."

    def do_modify_device(self,argc):
        """
        do_modify_device: modify a target device.
        
		*************** modify_device param ****************
                 -id(*)   :device uuid
                 -name(): device name 
                 -a():need authentication,0:false,1:true,default:0
                 -et():encrypted transmit,0:false,1:true,default:0
                 -ct():compressed transmit,0:false,1:true,default:0
                 -dt(): disk type 0=standard(100IOPS),1=speed(4000IOPS)
                 -user():authentication account
                 -pwd(): authentication password
                 -ssid():snapshot pool uuid
        eg: 
        """
        argc = argc.split()
        if param_image(param_modify_device,argc) == CHECK_PASS:
            try:
                global service
                global finished_event                   
                finished_event = threading.Event()
                if service != None:
                    service.case_manager.clearTestCase()
                    service.case_manager.addTestCase(TestCase("modify_device", modify_device))
                        
                    enviro = service.case_manager.getParam()
                    enviro["control_server"] = service.zc_node_name
                    enviro["device_name"] = param_modify_device['-name']
                    enviro["device"] = param_modify_device['-id']
                    enviro["disk_type"] = param_modify_device['-dt']

                    #optional parameter:
                    if param_create_device['-a'] == '1':
                        enviro["authen"] = True
                    else:
                        enviro["authen"] = False

                    if param_create_device['-et'] == '1':
                        enviro["crypt_trans"] = True
                    else:
                        enviro["crypt_trans"] = False

                    if param_create_device['-ct'] == '1':
                        enviro["cmp_trans"] = True
                    else:
                        enviro["cmp_trans"] = False
                    
                    enviro["authen_user"] = param_modify_device['-user']
                    enviro["authen_pwd"] = param_modify_device['-pwd']                    
                    enviro["ss_uuid"] = param_modify_device['-ssid'] 
                    
                    service.beginTest()
                        
                    finished_event.wait()
                    finished_event.clear()
                    if service.case_manager.test_result == CMDRUN_PASS:
                        print "Execute command success."
                    else:
                        print "Execute command fail."
            except:
                print "Execute fail, goto except now."
               

if __name__ == "__main__":
    #Just a tip while login the mode
    welcome = "Welcome to zhicloud manage platform."

    #create cmd interface.
    cli = ZhiCloudMgtCmd()
    cli.prompt = "ZhiCloudCmd: #"
    cli.cmdloop(welcome)
