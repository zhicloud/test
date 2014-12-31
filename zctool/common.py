#!/usr/bin/python


#testcase result
CMDRUN_PASS = 0
CMDRUN_FAULT = 1
CMDRUN_TIMEOUT = 2

#check parameter
CHECK_PASS = 0
CHECK_FAULT = 1


#create host config
memory_config = [
    512*1024*1024,#512MB
    1024*1024*1024,#1GB
    2*1024*1024*1024,#2GB
    4*1024*1024*1024,#4GB
    8*1024*1024*1024,#8GB
    16*1024*1024*1024,#16GB
    ]

system_disk_config = [
    5*1024*1024*1024,#5GB
    10*1024*1024*1024,#10GB
    20*1024*1024*1024,#20GB
    50*1024*1024*1024,#50GB
    100*1024*1024*1024,#100GB
    ]

data_disk_config = [
    20*1024*1024*1024,#20GB
    50*1024*1024*1024,#50GB
    100*1024*1024*1024,#100GB
    200*1024*1024*1024,#200GB
    500*1024*1024*1024,#500GB
    1000*1024*1024*1024,#1TB
    2000*1024*1024*1024,#2TB
    ]


def check_param_input(argc,pnum):
    if argc == "":
        print "Err:The parameter is none,please input all of parmeters."
        return CHECK_FAULT
    if len(argc)!= pnum:
        print "Err: parameter number error,Pls check it."
        return CHECK_FAULT

    return CHECK_PASS

##def param_image(param_type, param_argc):
##    #get parameter key.
##    for i in range(0,len(param_argc),2):
##        if param_argc[i] in param_type:
##            param_type[param_argc[i]] = param_argc[i+1]
##        else:
##            print "Err:parameter key error."
##            return CHECK_FAULT
##    #check essential parameter
##    for key in param_type:
##        if param_type[key] == None:
##            print "Err:Get parameter error,some essential parameter is None."
##            return CHECK_FAULT
##    return CHECK_PASS

def param_image(param_type, param_argc):
    #get parameter key.
    for i in range(0,len(param_argc),2):
        if param_argc[i] in param_type:
#            print 'gaoshijie add:',param_argc[i]
#            print 'gaoshijie add:',param_type[param_argc[i]]
            if i+1 in range(0,len(param_argc)):
                param_type[param_argc[i]] = param_argc[i+1] 
#                print 'gaoshijie add:',param_type[param_argc[i]]
            else: 
                print "%r Missing parameter."%(param_argc[i])
                return CHECK_FAULT
        else:
            print "Err:parameter key error."
            return CHECK_FAULT
    #check essential parameter
    for key in param_type:
        if param_type[key] == None:
            print "Err:%r Get parameter error,some essential parameter is None."%key
            return CHECK_FAULT
    return CHECK_PASS


def port_dealwith(portstr):
    port_list = []
    #temp = portstr.split(',')
    for portlist in portstr.split(','):
        portlist = portlist.split(':')
        if portlist[0] == "all":
            port_list.append(0)
        elif portlist[0] == "tcp":
            port_list.append(1)
        elif portlist[0] == "udp":
            port_list.append(2)
        else:
            #print "Err:deal with port type fail."
            return []
        port_list.append(int(portlist[1]))
    
    return port_list


def show_test_result(title,result):
    #get title line
    strtitle = ""
    for t in title:
        #strtitle += ' '*2
        #strtitle += t
        #strtitle += ' '*2
        strtitle += '{0: ^10}'.format(t)
        strtitle += '|'
        #'{0:*^30}'.format(eachStr); 
    #result format
    res_list = []
    max_line = len(strtitle)
    for i in range(len(result[0])):
        line = "    %d    | " % (i+1)
        for j in range(len(title)-1):            
            #line += ' '*2
            #line += result[j][i]
            #line += ' '*2
            line += '{0: ^10}'.format(result[j][i])
            line += '|'
        if len(line)>max_line:
            max_line = len(line)
        res_list.append(line)
    #show at screen
    print '-'*max_line
    print strtitle
    print '-'*max_line
    for linevalue in res_list:
        print linevalue
    print '-'*max_line

def print_test_result(title,*result):
    res_result = []
    for res in result:
        res_result.append(res)

    show_test_result(title,res_result)

class ZCException(Exception):
    pass

def ZCCMN_GetLocalIP():
    pass

def cmn_test(index):
    #index = input("NO.:")
    print memory_config[index]
    print system_disk_config[index]
    print data_disk_config[index]

if __name__ == "__main__":
    #print port_dealwith("tcp:80,tcp:22")
    title = ['index','ID','Name','Status']
    length = [7,8,5,8]
    res_id = ['1111111111111111','2222222222222222','3333333333333333']
    res_name = ['aaa','bbb','ccc']
    res_status = ['normal','start','stop']
    
##    res_result = []
##    res_result.append(res_id)
##    res_result.append(res_name)
##    res_result.append(res_status)

    print_test_result(title,res_id,res_name,res_status)
    
    #show_test_result(title,res_result)
             
    
