#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading
from message_define import *
from logger_helper import * 
from loop_thread import *


class TimerService(LoopThread):
    """
    usage:
    isRunning():
    start():
    stop():
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

    bindEventHandler(handler):
        handler must has callable by self.handler(event)
        
    override methods
    onStart():return False to cancel start process
    onStop():
    onLoop():customize loop process here

    created akumas 2013.8.8
    """
    class TimeCounter(object):
        timer_id = 0
        receive_session = 0
        timeout = 0
        count_down = 0
        is_loop = False
        specify_event = None

    event_handler = None
    def __init__(self, logger_name, interval = LoopThread.default_timeout):
        LoopThread.__init__(self, interval)
        LoggerHelper.__init__(self, logger_name)
        self.timer_map = {}
        self.timer_lock = threading.RLock()
        self.id_seed = 0
        
    def setTimer(self, timeout, receive_session):
        """
        invoke timeout event to [receive_session] after [timeout] seconds
        @return:timer_id
        """
        with self.timer_lock:
            timer = TimerService.TimeCounter()
            self.id_seed += 1
            timer.timer_id = self.id_seed
            timer.receive_session = receive_session
            timer.timeout = timeout
            timer.count_down = timeout
            self.timer_map[timer.timer_id] = timer
##            self.debug("set timer, timeout %d, session [%08X], id %d"%(
##                timeout, receive_session, timer.timer_id))
            return timer.timer_id
        
    def setLoopTimer(self, timeout, receive_session):
        """
        continues invoke timeout event to [receive_session] after [timeout] seconds
        @return:timer_id
        stop by clearTimer()
        """
        with self.timer_lock:
            timer = TimerService.TimeCounter()
            self.id_seed += 1
            timer.timer_id = self.id_seed
            timer.receive_session = receive_session
            timer.timeout = timeout
            timer.count_down = timeout
            timer.is_loop = True
            self.timer_map[timer.timer_id] = timer
##            self.debug("set loop timer, timeout %d, session [%08X], id %d"%(
##                timeout, receive_session, timer.timer_id))
            return timer.timer_id
        
        
    def setTimedEvent(self, event, timeout):
        """
        invoke specified [event] to handler after [timeout] seconds
        @return:timer_id
        """
        with self.timer_lock:
            timer = TimerService.TimeCounter()
            self.id_seed += 1
            timer.timer_id = self.id_seed
            ##determined by event
            timer.receive_session = 0
            timer.timeout = timeout
            timer.count_down = timeout
            timer.specify_event = event
            self.timer_map[timer.timer_id] = timer
            return timer.timer_id
        
    def setLoopTimedEvent(self, event, timeout):
        """
        continues invoke specified [event] to handler after [timeout] seconds
        @return:timer_id
        stop by clearTimer()
        """
        with self.timer_lock:
            timer = TimerService.TimeCounter()
            self.id_seed += 1
            timer.timer_id = self.id_seed
            ##determined by event
            timer.receive_session = 0
            timer.timeout = timeout
            timer.count_down = timeout
            timer.is_loop = True
            timer.specify_event = event
            self.timer_map[timer.timer_id] = timer
            return timer.timer_id
        
    def clearTimer(self, timer_id):
        """
        cancel timeout count down
        """
        with self.timer_lock:
            if self.timer_map.has_key(timer_id):
                del self.timer_map[timer_id]
##                self.debug("timer %d removed"%timer_id)

    def bindEventHandler(self, handler):
        """
        handler must has callable by self.handler(event)
        """
        self.event_handler = handler
        
    """
    method need override by subclass
    """
    def onStart(self):
        """
        return False to cancel start process
        """
##        self.debug("timer service start")
        return True
    def onStop(self):
##        self.debug("timer service stopped")
        pass

    def onLoop(self):
        """
        customize loop process here
        """
        with self.timer_lock:
            clear_list = []
            for timer in self.timer_map.values():
                timer.count_down -= 1
                if 0 == timer.count_down:
                    ##timeout   
                    if self.event_handler:
                        if not timer.specify_event:
                            event = getEvent(EventDefine.timeout)
                            event.session = timer.receive_session                        
                        else:
                            event = timer.specify_event
                            
##                        self.debug("timer %d timeout"%timer.timer_id)
                        self.event_handler(event)
                        
                    if timer.is_loop:
                        ##loop timer
                        timer.count_down = timer.timeout
##                        self.debug("timer %d reset to %d"%(timer.timer_id,timer.timeout))                        
                    else:
                        ##clear
                        clear_list.append(timer.timer_id)
            ##end for timer in self.timer_map.values():
            if 0 != len(clear_list):
                for timer_id in clear_list:
##                    self.debug("timer %d cleared"%timer_id)                        
                    del self.timer_map[timer_id]

if __name__ == '__main__':
    class Handler(object):
        def onTimeoutEvent(self, event):
            print "on timeout, session =", event.session

    handler = Handler()
    timer = TimerService("timer")
    timer.bindEventHandler(handler.onTimeoutEvent)
    timer.start()
    id1 = timer.setTimer(2, 1)
    id2 = timer.setLoopTimer(5, 2)
    id3 = timer.setTimer(10, 3)
    id4 = timer.setLoopTimer(4, 4)
    print id1,id2,id3,id4
    
    import time
    time.sleep(10)
    timer.clearTimer(id4)
    
    time.sleep(20)
    timer.stop()
    
