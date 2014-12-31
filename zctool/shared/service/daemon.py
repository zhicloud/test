#!/usr/bin/python
import sys, os, time
import signal
import io

class Daemon(object):
    """
    A generic daemon class.
    
    Usage: subclass the Daemon class and override the _run() method
    """
    def __init__(self, proxy):
        self.proxy = proxy

    def __daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced 
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        #detach from parent proccess
        try:
            pid = os.fork()
            if pid > 0:
                ##parent process
                sys.exit(0)
                
        except OSError, e:
            self.console("fork #1 failed: %d (%s)" % (e.errno, e.strerror))
            sys.exit(1)

##        runs a program in a new session
        os.setsid()
##        change current dir
        os.chdir("/")
##        Set the current numeric umask and return the previous umask.
##        os.umask(0)

# Fork a second child and exit immediately to prevent zombies.  This
# causes the second child process to be orphaned, making the init
# process responsible for its cleanup.  And, since the first child is
# a session leader without a controlling terminal, it's possible for
# it to acquire one by opening a terminal in the future (System V-
# based systems).  This second fork guarantees that the child is no
# longer a session leader, preventing the daemon from ever acquiring
# a controlling terminal.
        try:
            pid = os.fork()
            if pid > 0:
                ##parent process
                sys.exit(0)
                
        except OSError, e:
            self.console("fork #2 failed: %d (%s)" % (e.errno, e.strerror))
            sys.exit(1)
            
        #exit handler
        signal.signal(signal.SIGTERM, self.onExitSignal)
            
    def start(self):
        """
        Start the daemon
        """
        if self.proxy.isProcessRunning():
            self.console("start deamon fail, service already running")
            sys.exit(1)

        # Start the daemon
        self.__daemonize()                
        if self.proxy.start():
            self.onStart()
            self.mainProcess()
        else:
            self.console("start deamon fail, can't start proxy")
            sys.exit(1)
            
    def stop(self):
        """
        Stop the daemon
        """
        if not self.proxy.isProcessRunning():
            self.console("stop deamon fail, service already stopped")
            return # not an error in a restart
        pid = self.proxy.getPID()
        if -1 == pid:
            self.console("stop deamon fail, can't obtain pid")
            return # not an error in a restart

        self.console("stopping daemon...")
        self.onStop()
        # Try killing the daemon process    
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                self.console("daemon process stopped")
            else:
                self.console(err)
                sys.exit(1)

    def onExitSignal(self, signum, frame):
        self.proxy.stop()
        self.console("daemon exit for exit signal")
        self.onExit()        
        sys.exit(0)

        
    ##stub for override
    """
    onStart
    @return:
    False = initial fail, stop daemon
    True = initial success, start main process
    """
    def onStart(self):
        pass
    
    def onStop(self):
        """
        daemon receving stop signal
        """
        pass
    
    def onExit(self):
        """
        on daemon exit
        """
        pass
    
    def mainProcess(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """
        while True:
            time.sleep(1)
        
    def console(self, content):
        ##output to current console
        print content


