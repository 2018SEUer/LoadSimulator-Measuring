# sar_module

############################################################
#                                                          #
#   与cs模块进行通信，用于采集各项动态指标，并将数据返回给cs模块    #
#                                                          #
############################################################

import socket, time, subprocess, sys, os, math, time, sqlite3

# 获取当前时间戳
def sar_collect():
    datetime=year+'-'+month+'-'+day+' '+hour+':'+minute+':'+second
    timestamp=int(time.mktime(time.strptime(datetime, '%Y-%m-%d %H:%M:%S')))
    return timestamp

'''
    date&time
'''
# 获取当前日期
def getDate():                
    year=time.strftime('%Y')
    month=time.strftime('%m')
    day=time.strftime('%d')
    hour=time.strftime('%H')
    minute=time.strftime('%M')
    second=time.strftime('%S')
    print('打印当前日期:',year,month,day,hour,minute,second)
    return year,month,day,hour,minute,second

# 将一定格式的日期时间字符串转换为Unix timestamp
def dt_stamp(year, month, day, hour, minute, second):
	datetime=year+'-'+month+'-'+day+' '+hour+':'+minute+':'+second
	timestamp=int(time.mktime(time.strptime(datetime, '%Y-%m-%d %H:%M:%S')))
	return timestamp

'''
    CPU
'''
# 采集CPU的相关数据
def gather_cpu():
    sar_gather=''
    sar_cpu_info=subprocess.Popen('sar -u ALL -P ALL 0', shell=True, stdout=subprocess.PIPE)
    out0, err0=sar_cpu_info.communicate()
    sar_cpu_str=out0.decode(encoding='utf-8', errors='ignore')
    lines=len(sar_cpu_str.split('\n'))
    sar_cpu_str=sar_cpu_str.split('\n')
    for i in range(0,lines):
        count_r=len(sar_cpu_str[i].split())
        sar_cpu_str[i]=sar_cpu_str[i].split()
        if count_r==12:
            for j in range(0,count_r):
                try:
                    sar_cpu_str[i][j]=float(sar_cpu_str[i][j])
                except ValueError:
                    sar_cpu_str[i][j]=sar_cpu_str[i][j] 
                if sar_cpu_str[i][1]=="all":
                    if j>=2:
                        sar_gather+=str(sar_cpu_str[i][j])
                        sar_gather+=' '
    return sar_gather

# 采集CPU的频率
def gather_cpuMHz():
    sar_gather=''
    sar_cpu_info=subprocess.Popen('sar -m CPU -P ALL 0', shell=True, stdout=subprocess.PIPE)
    out0, err0=sar_cpu_info.communicate()
    sar_cpu_str=out0.decode(encoding='utf-8', errors='ignore')
    lines=len(sar_cpu_str.split('\n'))
    sar_cpu_str=sar_cpu_str.split('\n')
    for i in range(0,lines):
        count_r=len(sar_cpu_str[i].split())
        sar_cpu_str[i]=sar_cpu_str[i].split()
        if count_r==3:
            for j in range(0,count_r):
                try:
                    sar_cpu_str[i][j]=float(sar_cpu_str[i][j])
                except ValueError:
                    sar_cpu_str[i][j]=sar_cpu_str[i][j] 
                if sar_cpu_str[i][1]=="all":
                    if j>=2:
                        sar_gather+=str(sar_cpu_str[i][j])
                        sar_gather+=' '
    return sar_gather

'''
    memory
'''
# 采集内存的相关数据
def gather_memory():
    sar_gather=''
    sar_mem_info=subprocess.Popen('sar -r ALL 0', shell=True, stdout=subprocess.PIPE)  
    out0, err0=sar_mem_info.communicate()                                           
    sar_mem_str=out0.decode(encoding='utf-8', errors='ignore')             
    lines=len(sar_mem_str.split('\n'))
    sar_mem_str=sar_mem_str.split('\n')
    for i in range(0,lines):
        count_r=len(sar_mem_str[i].split())
        sar_mem_str[i]=sar_mem_str[i].split()
        if count_r==16:    
            for j in range(0,count_r):
                try:
                    sar_mem_str[i][j]=float(sar_mem_str[i][j])
                except ValueError:
                    sar_mem_str[i][j]=sar_mem_str[i][j] 
                if sar_mem_str[i][1]!="kbmemfree":
                    if j>=3 and j!=4 and j!=5 and j!=6 and j!=12 :
                        sar_gather+=str(sar_mem_str[i][j])
                        sar_gather+=' '
    sar_mem_info=subprocess.Popen('sar -B 0', shell=True, stdout=subprocess.PIPE)   
    out0, err0=sar_mem_info.communicate()                                  
    sar_mem_str=out0.decode(encoding='utf-8', errors='ignore')                     
    lines=len(sar_mem_str.split('\n'))
    sar_mem_str=sar_mem_str.split('\n')
    for i in range(0,lines):
        count_r=len(sar_mem_str[i].split())
        sar_mem_str[i]=sar_mem_str[i].split()
        if count_r==10:    
            for j in range(0,count_r):
                try:
                    sar_mem_str[i][j]=float(sar_mem_str[i][j])
                except ValueError:
                    sar_mem_str[i][j]=sar_mem_str[i][j] 
                if sar_mem_str[i][1]!="pgpgin/s":
                    if j>=1 and j!=7:
                        sar_gather+=str(sar_mem_str[i][j])
                        sar_gather+=' '
    return sar_gather

'''
    disk
'''
# 采集磁盘的相关数据
def gather_disk():
    sar_gather=''
    sar_disk_info=subprocess.Popen('sar -d 0', shell=True, stdout=subprocess.PIPE)
    out0, err0=sar_disk_info.communicate()
    sar_disk_str=out0.decode(encoding='utf-8', errors='ignore')
    lines=len(sar_disk_str.split('\n'))
    sar_disk_str=sar_disk_str.split('\n')
    for i in range(0,lines):
        count_r=len(sar_disk_str[i].split())
        sar_disk_str[i]=sar_disk_str[i].split()
        if count_r==10:
            for j in range(0,count_r):
                try:
                    sar_disk_str[i][j]=float(sar_disk_str[i][j])
                except ValueError:
                    sar_disk_str[i][j]=sar_disk_str[i][j] 
                if sar_disk_str[i][1]=="dev8-0":
                    if j>=2:
                        sar_gather+=str(sar_disk_str[i][j])
                        sar_gather+=' '
    return sar_gather

'''
    network
'''
# 采集网络的相关数据
def gather_network():
    sar_gather=''

    sar_net_info=subprocess.Popen('sar -n DEV 0', shell=True, stdout=subprocess.PIPE)
    out0, err0=sar_net_info.communicate()
    sar_net_str=out0.decode(encoding='utf-8', errors='ignore')
    lines=len(sar_net_str.split('\n'))
    sar_net_str=sar_net_str.split('\n')
    for i in range(0,lines):
        count_r=len(sar_net_str[i].split())
        sar_net_str[i]=sar_net_str[i].split()
        if count_r==10:
            for j in range(0,count_r):
                try:
                    sar_net_str[i][j]=float(sar_net_str[i][j])
                except ValueError:
                    sar_net_str[i][j]=sar_net_str[i][j] 
                if sar_net_str[i][1]=="wlp3s0":
                    if j>=2:
                        sar_gather+=str(sar_net_str[i][j])
                        sar_gather+=' '
    sar_net_info=subprocess.Popen('sar -n EDEV 0', shell=True, stdout=subprocess.PIPE)
    out0, err0=sar_net_info.communicate()
    sar_net_str=out0.decode(encoding='utf-8', errors='ignore')
    lines=len(sar_net_str.split('\n'))
    sar_net_str=sar_net_str.split('\n')
    for i in range(0,lines):
        count_r=len(sar_net_str[i].split())
        sar_net_str[i]=sar_net_str[i].split()
        if count_r==11:
            for j in range(0,count_r):
                try:
                    sar_net_str[i][j]=float(sar_net_str[i][j])
                except ValueError:
                    sar_net_str[i][j]=sar_net_str[i][j] 
                if sar_net_str[i][1]=="wlp3s0":
                    if j>=2:
                        sar_gather+=str(sar_net_str[i][j])
                        sar_gather+=' '
    return sar_gather

'''
    task
'''
# 采集任务的相关数据
def gather_q():
    sar_gather=''
    sar_task_info=subprocess.Popen('sar -q 0', shell=True, stdout=subprocess.PIPE)
    out0, err0=sar_task_info.communicate()
    sar_task_str=out0.decode(encoding='utf-8', errors='ignore')
    lines=len(sar_task_str.split('\n'))
    sar_task_str=sar_task_str.split('\n')
    for i in range(0,lines):
        count_r=len(sar_task_str[i].split())
        sar_task_str[i]=sar_task_str[i].split()
        if count_r==7:      
            for j in range(0,count_r):
                try:
                    sar_task_str[i][j]=float(sar_task_str[i][j])
                except ValueError:
                    sar_task_str[i][j]=sar_task_str[i][j] 
                if sar_task_str[i][1]!="runq-sz" and sar_task_str[i][0]!="Linux":
                    if j>=1:
                        sar_gather+=str(sar_task_str[i][j])
                        sar_gather+=' '
    return sar_gather

'''
    interrupt
'''
# 采集中断的相关数据
def gather_I():
    sar_gather=''
    sar_intr_info=subprocess.Popen('sar -I 1 0', shell=True, stdout=subprocess.PIPE)
    out0, err0=sar_intr_info.communicate()
    sar_intr_str=out0.decode(encoding='utf-8', errors='ignore')
    lines=len(sar_intr_str.split('\n'))
    sar_intr_str=sar_intr_str.split('\n')
    for i in range(0,lines):
        count_r=len(sar_intr_str[i].split())
        sar_intr_str[i]=sar_intr_str[i].split()
        if count_r==3:
            for j in range(0,count_r):
                try:
                    sar_intr_str[i][j]=float(sar_intr_str[i][j])
                except ValueError:
                    sar_intr_str[i][j]=sar_intr_str[i][j] 
                if sar_intr_str[i][1]!="INTR":
                    if j==2:
                        sar_gather+=str(sar_intr_str[i][j])
                        sar_gather+=' '
    return sar_gather

'''
    process
'''
# 采集I/O的相关数据
def gather_w():
    sar_gather=''
    sar_prcs_info=subprocess.Popen('sar -w 0', shell=True, stdout=subprocess.PIPE)
    out0, err0=sar_prcs_info.communicate() 
    sar_prcs_str=out0.decode(encoding='utf-8', errors='ignore')
    lines=len(sar_prcs_str.split('\n'))
    sar_prcs_str=sar_prcs_str.split('\n')
    for i in range(0,lines):
        count_r=len(sar_prcs_str[i].split())
        sar_prcs_str[i]=sar_prcs_str[i].split()
        if count_r==3:
            for j in range(0,count_r):
                try:
                    sar_prcs_str[i][j]=float(sar_prcs_str[i][j])
                except ValueError:
                    sar_prcs_str[i][j]=sar_prcs_str[i][j] 
                if sar_prcs_str[i][1]!="proc/s":
                    if j>=1:
                        sar_gather+=str(sar_prcs_str[i][j])
                        sar_gather+=' '
    return sar_gather

'''
    io
'''
# 采集磁盘的相关数据
def gather_b():
    sar_gather=''
    sar_io_info=subprocess.Popen('sar -b 0', shell=True, stdout=subprocess.PIPE)
    out0, err0=sar_io_info.communicate()
    sar_io_str=out0.decode(encoding='utf-8', errors='ignore')
    lines=len(sar_io_str.split('\n'))
    sar_io_str=sar_io_str.split('\n')
    for i in range(0,lines):
        count_r=len(sar_io_str[i].split())
        sar_io_str[i]=sar_io_str[i].split()
        if count_r==6:
            for j in range(0,count_r):
                try:
                    sar_io_str[i][j]=float(sar_io_str[i][j])
                except ValueError:
                    sar_io_str[i][j]=sar_io_str[i][j] 
                if sar_io_str[i][1]!="tps":
                    if j>=1:
                        sar_gather+=str(sar_io_str[i][j])
                        sar_gather+=' '
    return sar_gather

'''
    swap
'''
# 采集交换区的相关数据
def gather_W():
    sar_gather=''
    sar_swap_info=subprocess.Popen('sar -W 0', shell=True, stdout=subprocess.PIPE)
    out0, err0=sar_swap_info.communicate()
    sar_swap_str=out0.decode(encoding='utf-8', errors='ignore')
    lines=len(sar_swap_str.split('\n'))
    sar_swap_str=sar_swap_str.split('\n')
    for i in range(0,lines):
        count_r=len(sar_swap_str[i].split())
        sar_swap_str[i]=sar_swap_str[i].split()
        if count_r==3:
            for j in range(0,count_r):
                try:
                    sar_swap_str[i][j]=float(sar_swap_str[i][j])
                except ValueError:
                    sar_swap_str[i][j]=sar_swap_str[i][j] 
                if sar_swap_str[i][1]!="pswpin/s":
                    if j>=1:
                        sar_gather+=str(sar_swap_str[i][j])
                        sar_gather+=' '
    return sar_gather

'''
    swap
'''
# 采集交换区的相关数据
def gather_S():
    sar_gather=''
    sar_swap_info=subprocess.Popen('sar -S 0', shell=True, stdout=subprocess.PIPE)
    out0, err0=sar_swap_info.communicate()
    sar_swap_str=out0.decode(encoding='utf-8', errors='ignore')
    lines=len(sar_swap_str.split('\n'))
    sar_swap_str=sar_swap_str.split('\n')
    for i in range(0,lines):
        count_r=len(sar_swap_str[i].split())
        sar_swap_str[i]=sar_swap_str[i].split()
        if count_r==6:
            for j in range(0,count_r):
                try:
                    sar_swap_str[i][j]=float(sar_swap_str[i][j])
                except ValueError:
                    sar_swap_str[i][j]=sar_swap_str[i][j] 
                if sar_swap_str[i][1]!="kbswpfree":
                    if j>=3 and j!=4:
                        sar_gather+=str(sar_swap_str[i][j])
                        sar_gather+=' '
    return sar_gather

'''
    数据汇总
'''
def gather():
    year,month,day,hour,minute,second=getDate()
    # 制作时间戳
    timestamp=dt_stamp(year, month, day, hour, minute, second)
    sar_gather=''
    # sar_gather[1~10]: %usr %nice %sys %iowait %steal %irq %soft %guest %gnice %idle
    sar_gather+=gather_cpu()
    # sar_gather[11]: MHz
    sar_gather+=gather_cpuMHz()
    # sar_gether[12-20]:%memused %commit kbactive kbinact kbdirty kbanonpg kbstack kbpgtbl kbvmused
    # sar_gather[21-28]:pgpgin/s pgpgout/s fault/s majflt/s pgfree/s pgscank/s  pgsteal/s %vmeff
    sar_gather+=gather_memory()
    # sar_gather[29-36]:tps rd_sec/s wr_sec/s avgrq-sz avgqu-sz await svctm %util
    sar_gather+=gather_disk()
    # sar_gather[37-53]:rxpck/s txpck/s rxkB/s txkB/s rxcmp/s txcmp/s rxmcst/s %ifutil rxerr/s txerr/s coll/s rxdrop/s txdrop/s txcarr/s rxfram/s rxfifo/s txfifo/s
    sar_gather+=gather_network()
    # sar_gather[54-59]: runq-sz plist-sz ldavg-1 ldavg-5 ldavg-15 blocked
    sar_gather+=gather_q()
    # sar_gather[60]:intr/s
    sar_gather+=gather_I()
    # sar_gather[61-62]:proc/s cswch/s
    sar_gather+=gather_w()
    # sar_gather[63-67]: tps rtps wtps bread/s bwrtn/s
    sar_gather+=gather_b()
    # sar_gather[68-69]:pswpin/s pswpout/s
    sar_gather+=gather_W()
    # sar_gather[70-71]: %swpused %swpcad
    sar_gather+=gather_S()
    # 在sar_gather输出的第一个符号前添加时间戳
    sar_gather=str(timestamp)+' '+sar_gather
    return sar_gather

#---------------------------------#
#            main函数              #
#---------------------------------#

if __name__ =="__main__":

    #----------socket通信部分----------
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(clientSocket)
    # 服务端的IP和端口号等（！需要自己进行设定）
    host = socket.gethostname()
    IP      =   "192.168.10.101"     
    host    =   IP
    port    =   8080
    buffer_size = 1024
    address = (host, port)
    print(address)
    clientSocket.connect(address)
    print("连接服务器成功")
    print("等待服务端发送信息...")
    
    # 与服务端进行通信
    while(1):
      infor = clientSocket.recv(1024)
      command=infor.decode("utf-8")
      print("从服务器接受到消息",command)
      print("开始输出sar 的cpu、memory、disk、network等信息")
      if command=="COLLECT":
        data=gather()
        # 将收集到的信息作为有一定顺序的字符串
        information=data
        clientSocket.send(information.encode("utf-8"))
    
    # 关闭socket连接
    clientSocket.close()

# __END__OF__SAR_PY__