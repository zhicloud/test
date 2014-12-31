#!/usr/bin/python

#status define
Status_Port_Rescource = ['idle','allocated']
Status_Port_Pool = ['Disable','Enable']
Status_Forwarder_summary = ['mono','share','domain']
Status_Forwarder = ['mono','share']
Status_Address_Pool= ['Disable','Enable']
Status_Address_Resource= ['Disable','Enable']

Stutus_host = ['Normal','Warnning','Fault','Stop']
Stutus_disk_image = ['Normal','Disable']
Stutus_iso_image = ['Normal','Disable']
Stutus_compute_pool = ['Normal','Warnning','Fault','Stop']
Stutus_service_type = ['Normal','Warnning','Fault','Stop']

Sturus_bind_domain = ['Host','Balancer']
Sturus_bound_domain = ['Fowwarder','Balancer']

Sturus_balancer_detail = ['Deactive','Active']
Sturus_balancer_summary = ['mono','share','domain']
Status_load_balancer = ['mono','share']

Type_host_network = ['domain','mono','Share']
Type_host_disk = ['local','Cloud']

Status_compute_resource=['Normal','Warnning','Fault','stop']
Status_server_room=['Normal','Warnning','Fault','stop']
Status_server_rack=['Normal','Warnning','Fault','stop']
Status_server=['Normal','Warnning','Fault','stop']
Status_storage_pool=['Normal','Warnning','Fault','stop']

Status_device = ['Normal','Warnning','Fault','stop']
Status_security = ['False','True']
Status_crypt = ['False','True']

#newstatus = ChangeResuleStatus(status,Stutus_host)

#functions define
def show_test_result(title,length,result):
    #judge parameter number
    if len(result[0]) <= 0:
        return 0
    #get title line
    title.insert(0,'index')
    length.insert(0,5)
    
    strtitle = ""
    offset = 0
    for t in title:
        strtitle += ("{0: ^%d}" % length[offset]).format(t)
        strtitle += '|'
        offset += 1
    #result format
    res_list = []
    max_line = len(strtitle)
    for i in range(len(result[0])):
        try:
            lineno = "%d" % (i+1)
            offset = 0
            line = ("{0: ^%d}" % length[offset]).format(lineno) + '|'
            offset += 1
            for j in range(len(title)-1):
                line += ("{0: ^%d}" % length[offset]).format(result[j][i]) + '|'
                offset += 1
            if len(line)>max_line:
                max_line = len(line)
            res_list.append(line)
            offset += 1
        except:
            print "Get value failed,value is:%s" % str(result[0])
    #show at screen
    print '-'*max_line
    print strtitle
    print '-'*max_line
    for linevalue in res_list:
        print linevalue
    print '-'*max_line

    

def print_test_result(title,*result):
    res_result = []
    length = Get_Max_Length_List(title,result)
    index = 0
    for res in result:
        if res == None:
            print "%s value is None,please check it" % title[index+1]
            continue
        res_result.append(res)

    show_test_result(title,length,res_result)

def Get_Max_Length_List(title,listargc):
    length = []
    index = 0
    try:
        for alist in listargc:
            sublen = 0
            if alist == None:
                continue
            for sublist in alist:
                if sublen < len(str(sublist)):
                    sublen = len(str(sublist))
            if sublen < len(title[index]):
                sublen = len(title[index])
            length.append(sublen+2)
            index += 1
        return length
    except:        
        print "Get value exception,may be type is None."
    

def Change_Bit_to_Mb(size):
    newsize = []
    for sz in size:
        newsize.append("%5.2f" % (float(sz)/1024/1024))
    return newsize
def Change_Bit_to_Kb(size):
    newsize = []
    for sz in size:
        newsize.append("%5.2f" % (float(sz)/1024))
    return newsize

def Change_Bit_to_Gb(size):
    newsize = []
    for sz in size:
        newsize.append("%5.2f" % (float(sz)/1024/1024/1024))
    return newsize

def print_one_result(result):
    length_key = 0
    length_value = 0
    for key in result:
        temp = str(key)
        if len(temp) > length_key:
            length_key = len(temp)
        if len(str(result.get(key))) > length_value:
            length_value = len(str(result.get(key)))
                               
    #print value
    column1 = "Items"
    column2 = "Values"
    print '-' * (length_key + length_value + 5)
    print ("{0: <%d}" % length_key).format(column1) + ' | ' + column2
    print '-' * (length_key + length_value + 5)
    for key in result:
        line = ("{0: <%d}" % length_key).format(key) + ' | '
        line += str(result.get(key))
        print line

    print '-' * (length_key + length_value + 5)

def print_one_list(title,value):
    try:
        length_key = 0
        length_value = 0
        for i in range(len(title)):
            if str(value[i]) == "":
                value[i] = "N/A"
            temp = str(value[i])
            title[i] = title[i] + ":"
            if len(title[i]) > length_key:
                length_key = len(title[i])
            if len(temp) > length_value:
                length_value = len(temp)
        column1 = "Items"
        column2 = "Values"
        print '-' * (length_key + length_value + 4)
        print ("{0: <%d}" % length_key).format(column1) + ' | ' + column2
        print '-' * (length_key + length_value + 4)
        for i in range(len(title)):
            line = ("{0: <%d}" % length_key).format(title[i]) + ' | '
            line += str(value[i])
            print line
        print '-' * (length_key + length_value + 4)
    except:
        print "print values exception,please check it."
            
    

def ChangeResuleStatus(status,type_status):
    try:
        if type(status) == list:
            result = []
            for item in status:
                result.append(type_status[int(item)])
            return result
        else:
            return type_status[int(status)]
    except:
        print "Change value status failed,please check it."
        return None


def GetPresentValue(param):
    if param == None:
        print "value is None,cant't get present value."
        return 0
    else:
        rst = []
        for value in param:
            temp = "%3.3f%%" % (value*100)
            rst.append(temp)
        return rst


if __name__ == "__main__":
    #pass
##    title = ['ID','Name','Status','ip']
##    res_id = ['111111111111111111','2222222222222222','3333333333333333']
##    res_name = ['adsaa','bdsdbb','caDDcc']
##    res_status = [2,3,1]
##    ip = ['172.16.1.101','172.16.1.102','172.16.1.103']
##    print_test_result(title,res_id,res_name,res_status,ip)
##    s = {
##        "aa" : None,
##        "bbbbbb" : None,
##        "eeeeeeee" : None,
##        "ccc" : None
##        }
##    s["aa"]= "af"
##    s["bbbbbb"]= "bb"
##    s["eeeeeeee"]= "cc"
##    s["ccc"]= 1237
##
##    print_one_result(s)
##
##    sta=[0,1,1,0]
##    sta2 = "1"
##    res = ChangeResuleStatus(sta,Type_host_network)
##    print res
##    res2 = ChangeResuleStatus(sta2,Type_host_network)
##    print res2
    a1 =[]
    b1 = []
    a1.append("11")
    b1.append("aa")
    a1.append("222")
    b1.append("bbb")
    a1.append("33333")
    b1.append("ccccc")
    print_one_list(a1,b1)
    
