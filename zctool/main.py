import logging
import logging.handlers
from test_service import *
from threading import *
from service.message_define import *


if __name__ == '__main__':
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logging.getLogger("task")
    root = logging.getLogger()
    root.addHandler(handler)

    finished_event = threading.Event()
    """
    param:service_name, domain, ip, group_ip, group_port,
                 server, rack, server_name, proxy
    """
    service = TestService("test",
                          "portal_test",
                          "172.168.2.25",
                          "224.8.8.8",
                          5666,
                          "","","", None)
##    service = TestService("test",
##                          "zhicloud",
##                          "",
##                          "224.6.6.6",
##                          5666,
##                          "","","", None)

    def onTestFinished(passed):
        if passed:
            root.info("test passed")
        else:
            root.info("test failed")
            
        finished_event.set()

    service.bindCallback(onTestFinished)
    
    service.start()
    service.connectRemoteNode("data_server_00505629b9dc",
                              NodeTypeDefine.data_server,
                              "172.168.6.4",
                              5600)                         
    finished_event.wait()
    service.stop()
    
    
    
                          
