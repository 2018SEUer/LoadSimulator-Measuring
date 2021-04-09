# loadrunner_module

############################################################
#                                                          #
#   与cs模块进行通信，获得负载参数后对SUT进行加压                 #
#                                                          #
############################################################

from concurrent.futures import ThreadPoolExecutor
import subprocess, re, time
import os,sys,math,threading
import socket

# 全局变量的设定与初始化（！核心数和最大频率需要自行设定）
global cores_num
global freq_max
cores_num   =   12                        # CPU核心数量
freq_max    =   2100                      # CPU最大频率
level       =   [0,0,0,0,0,0,0,0,0,0,0]   # 各项负载等级
tslp        =   10000                     # sleep time
t           =   100000                    # time
network     =   '192.168.0.1'             # 用于网络加压
TCPwindow   =   10                        # 用于网络加压

'''
  CPU
'''
# 根据百分比设置相应的频率
def freq_calculator():
  freq_av=int(freq_max/10)
  level[1]=freq_av
  for n in range (2,11):
    level[n]=level[n-1]+freq_av

# 获取当前开启的CPU核心数量
def cores_on_num():
  grep_info=subprocess.Popen('''grep "processor" /proc/cpuinfo''', shell=True, stdout=subprocess.PIPE)
  out0, err0=grep_info.communicate()
  grep_str=out0.decode(encoding='utf-8', errors='ignore')
  cores_on_num=len(re.findall('processor', grep_str))
  return cores_on_num

# FUNC 1: 开启n个核心，参数为需要开启的核心数
def cores_on(n):
  global cores_num	
  if int(n)>cores_num or int(n)==0:
  	raise Exception("wrong")
  num=cores_on_num()
  if int(n)>num:
  	for i in range(int(n)-num):
  		subprocess.call("echo '1' > /sys/devices/system/cpu/cpu%s/online"%str(num+i), shell=True)
  if int(n)<num:
  	for i in range(num-int(n)):
  		subprocess.call("echo '0' > /sys/devices/system/cpu/cpu%s/online"%str(num-i-1), shell=True)

# FUNC 2: 将所有开启的核心数的频率限制在目标频率
def freq_set(f):
	subprocess.call('cpupower frequency-set -f %s'%str(f), shell=True)

# FUNC 3: 给当前开启的核心进行加压，参数为加压百分比
def stress(s,t,tslp):
  lookbusy_p=subprocess.Popen('lookbusy -c %s --quiet'%(str(s)), shell=True)
  time.sleep(t)
  # 杀死lookubusy加压进程
  subprocess.call('pkill -9 lookbusy', shell=True)
  time.sleep(tslp)

'''
  disk
'''
def diskstress(e,t,tslp):
  # 定义无限循环量,十个不同层级来定义硬盘io负载
  var=0
  T0=time.time()
  if e==0:
      while(time.time()-T0<=t):
          os.system('iozone -i  0 -r 4K -s 4K -I')
  if e==1:
      while(time.time()-T0<=t):
          os.system('iozone -i 0 -r 4K -s  128K -I')
  if  e==2:
      while(time.time()-T0<=t):
          os.system('iozone -i 0 -r 4K -s  640K -I')
  if e==3:
      while(time.time()-T0<=t):
          os.system('iozone -i 0 -r 4K -s  2048K -I')
  if e==4:
      while(time.time()-T0<=t):
          os.system('iozone -i 0 -r 4K -s  4608K -I')
  if e==5:
      while(time.time()-T0<=t):
          os.system('iozone -i 0 -r 4K -s 8M -I')
  if e==6:
      while(time.time()-T0<=t):
          os.system('iozone -i 0 -r 4K -s  10M -I')
  if e==7:
      while(time.time()-T0<=t):
          os.system('iozone -i 0 -r 4K -s  32M -I')
  if e==8:
      while(time.time()-T0<=t):
          os.system('iozone -i 0 -r 4K -s  128M -I')
  if e==9:
      while(time.time()-T0<=t):
          os.system('iozone -i 0 -r 4K -s  512M -I')
  if e==10:
      while(time.time()-T0<=t):
          os.system('iozone -i 0 -r 4K -s  1024M -I')
  print('disk success!')
  time.sleep(tslp)

'''
  memory
'''
def memorystress(z,t,tslp):
  sar_r_info=subprocess.Popen('sar -r ALL 0', shell=True, stdout=subprocess.PIPE)  
  out0, err0=sar_r_info.communicate()
  sar_r_str=out0.decode(encoding='utf-8', errors='ignore')
  lines_r=len(sar_r_str.split('\n'))
  sar_r_str=sar_r_str.split('\n')
  for i in range(0,lines_r-1):
       count_r=len(sar_r_str[i].split())
       sar_r_str[i]=sar_r_str[i].split()
       if count_r==17:      
            for j in range(0,count_r):
              try:
                sar_r_str[i][j]=float(sar_r_str[i][j])
              except ValueError:
                sar_r_str[i][j]=sar_r_str[i][j] 
            if sar_r_str[i][1]!='kbmemfree':
                m=int(z)*10+30-sar_r_str[i][4];   
                m=int(m*(sar_r_str[i][1]+sar_r_str[i][2])/100)
                str_m='stress --vm 1 --vm-bytes '+str(m)+'K  --vm-hang 100 --timeout '+str(t)+'s'
                stress_r_info=subprocess.Popen(str_m, shell=True, stdout=subprocess.PIPE)             
                time.sleep(int(tslp))

'''
  network
'''
def networkstress(network,TCPwindow,j,t,tslp):
  TCPwindow=int(TCPwindow)*float(j)
  TCPwindow=str(TCPwindow)+'M'
  str_sys='iperf3 -c %s -b %s -d m -t '+str(t)
  # TCP模式加压
  os.system(str_sys%(network,TCPwindow))
  time.sleep(tslp)

#---------------------------------#
#            main函数              #
#---------------------------------#

if __name__ == "__main__":

  #-----------更新部分全局变量-----------
  # 将当前cpu核心数赋值给全局变量core_num
  cores_num=cores_on_num()
  # 设置cpu核心的最大频率
  freq_max=800000000
  freq_calculator()
  pool=ThreadPoolExecutor(max_workers=6)

  #-----------socket通信部分-----------

  # 创建一个tcp/ip协议的套接字
  clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  print("-------------")
  print(clientSocket)
  print("-------------")
  # 服务端IP地址  （！需要自行设定）
  IP1           =    "192.168.10.101"
  host          =    IP1
  # 端口号        （！需要自行设定）
  port          =    8008
  buffer_size   =    1024
  address = (host, port)
  print("-------------")
  print(address)
  print("-------------")
  clientSocket.connect(address)
  print("等待服务端发送信息：")
  
  while(True):
    data = clientSocket.recv(1024)
    data = data.decode("utf-8")
    print(data)
    if data=="连接服务器成功":
      print(data)
    elif data=='STOP':
      pool.shutdown(wait=True)
    else :
      x=data.split()
      results = list(map(int, x)) 
      cores_on(results[0])
      freq_set(level[int(results[1]/10)])
      pool.submit(stress,results[2],t,tslp)
      pool.submit(memorystress,results[3],t,tslp)
      pool.submit(diskstress,results[4],t)
      pool.submit(networkstress,network,TCPwindow,results[5],t,tslp)

# __END__OF__LOADRUNNER_PY__