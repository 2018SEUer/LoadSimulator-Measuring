# cs_module

############################################################
#														   #
# 组织加压与采集程序的进行									   #
# 向加压模块发送负载参数，并从采集模块获取当前数据				   #
#														   #
############################################################

import time, socket, sqlite3, serial, binascii, threading

# 全局变量设置
coresNum=32					# CPU核心数
IP='192.168.10.101'			# IP
portx='/dev/ttyUSB0'			# USB端口号

server=None					# 负责监听的socket
g_conn_pool=[]				# 连接池
thrd_pool=[]

# 网络初始化
def csInitial():
	print('初始化服务器主机信息')
	ADDRESS=(IP,8888)
	# 创建TCP服务socket对象
	print('初始化服务器主机套接字对象……')
	server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# 绑定主机信息
	print('绑定的主机信息……')
	server.bind(ADDRESS)
	# 启动服务器
	print('开始启动服务器……')
	server.listen(5)
	return server

def accept_client():
	"""
	接收新连接
	"""
	for i in range(2):
		# 阻塞，等待客户端连接
		print('等待模块%d连接'%i)
		conn, info=server.accept()
		# 加入连接池
		g_conn_pool.append(conn)
		# 给每个客户端创建一个独立的线程进行管理
		thrd=threading.Thread(target=message_handle, args=(conn,info))
		thrd_pool.append(thrd)
		# 设置成守护线程
		thrd.setDaemon(True)
		thrd.start()
		print('模块%d连接成功'%i)

def message_handle(client, info):
	client.sendall("连接服务器成功".encode(encoding='utf8'))

# 接收数据测试函数
def rcv_test(conn1):
	data1=conn1.recv(1024)
	msg1=data1.decode(encoding='utf-8')
	print(msg1)

# 向LR发送负载参数
def sendLoadLevel(paraList):
	g_conn_pool[0].sendall(paraList.encode('utf-8'))

# 向SAR发送测试请求
def sendCollectInstrc():
	g_conn_pool[1].sendall('COLLECT'.encode('utf-8'))

# 与功耗仪相连
def connToPower():
	# 波特率
	bps=9600
	# 超时设置
	timex=None
	# 打开串口
	ser=serial.Serial(portx, bps, timeout=timex)
	print('已连接到功耗仪')
	return ser

# 从功耗仪读取数据
# V02 获取瓦特
def readFromPower(ser):
	ser.write(bytes.fromhex('40 30 31 56 30 32 0D')) # @01V02
	time.sleep(0.1)
	len=ser.inWaiting()
	while len==0:
		len=ser.inWaiting()
	data=ser.read(len)
	#print(data)
	powerData=str(eval(str(data)[3:11]))
	return powerData

# 关闭串口
def serialEnd(ser):
	ser.close()
	print('关闭串口')

# 数据处理并存入数据库
# 参数sarData是接收到来自sar模块的原始字符串组成的列表，含3个长字符串
def dataProcs(sarData, powerData, sqConn):
	# 这两个列表用于存储分隔开后的数据
	sdlist=[]
	pdlist=[]
	# 将2*3组数据分别存入二维的列表中
	for i in range(3):
		tmpsar=sarData[i]
		tmppower=powerData[i]
		tmpsarlist=tmpsar.split() # tmpsarlist是含73个元素的列表
		sdlist.append(tmpsarlist) # 循环后得到3*73的表
		pdlist.append(tmppower) # 循环后得到3*1的表
	#print(sdlist)	
	# 计算平均值，存入数据库
	l1=72
	sar_res=[]
	power_res=0
	# sar数据的平均值
	for i in range(l1):
		sum=0
		for j in range(3):
			sum+=float(sdlist[j][i])
		avg=sum/3
		sar_res.append(avg)
	# power数据的平局值
	sum=0
	for j in range(3):
		sum+=float(pdlist[j])
	avg=sum/3
	# 本此测试的最终功耗值
	power_res=avg
	# res列表依次存储timestamp、SARdata、POWERdata
	sar_res.append(power_res)
	res=sar_res
	print("Average:")
	print(res)
	print('\n')
	# 将sar的数据插入数据库中
	# --------------------------sqlite3----------------------------
	curs=sqConn.cursor()
	curs.execute('''INSERT INTO METRICS VALUES
	(?,?,?,?,?,?,?,?,?,?,
	?,?,?,?,?,?,?,?,?,?,
	?,?,?,?,?,?,?,?,?,?,
	?,?,?,?,?,?,?,?,?,?,
	?,?,?,?,?,?,?,?,?,?,
	?,?,?,?,?,?,?,?,?,?,
	?,?,?,?,?,?,?,?,?,?,
	?,?,?)''',
	(res[0],res[1],res[2],res[3],res[4],res[5],res[6],res[7],res[8],res[9],
	res[10],res[11],res[12],res[13],res[14],res[15],res[16],res[17],res[18],res[19],
	res[20],res[21],res[22],res[23],res[24],res[25],res[26],res[27],res[28],res[29],
	res[30],res[31],res[32],res[33],res[34],res[35],res[36],res[37],res[38],res[39],
	res[40],res[41],res[42],res[43],res[44],res[45],res[46],res[47],res[48],res[49],
	res[50],res[51],res[52],res[53],res[54],res[55],res[56],res[57],res[58],res[59],
	res[60],res[61],res[62],res[63],res[64],res[65],res[66],res[67],res[68],res[69],
	res[70],res[71],power_res))

# CS模块工作核心
def cs_main(ser,sqConn):
	for a in (16, 32):						# cores	2levels
		for b in (900, 1500):					# freq	2levals
			for c in (10, 50, 80):				# CPU	3levels
				for d in (1, 3, 5):			# MEM	levels(0-7:40%-100%)
					for e in (10, 40, 80):		# DISK	4levels
						#for f in (20):	# NET	4levels
							paraList=''
							paraList+=str(a)+' '+str(b)+' '+str(c)+' '+str(d)+' '+str(e)+' '+str(20)
							print('当前测试: '+paraList)							
							sendLoadLevel(paraList+' 0')
							print('waiting...')
							# wait
							time.sleep(2)
							sarData=[]		# 存储3组数据
							powerData=[]	# 存储3组数据
							# 每间隔2秒进行一次数据的采集，共采集3次
							# 接收来自SAR模块的数据，将解码后的数据放入sarData中
							## 一组约9秒
							print("开始采集数据...")
							for i in range(3):
								sendCollectInstrc()
								pData=readFromPower(ser)
								print("当前功耗值:"+pData)
								powerData.append(pData)
								msgFromSar=g_conn_pool[1].recv(1024)
								dataFromSar=msgFromSar.decode('utf-8')
								print('当前动态数据:'+dataFromSar+'\n')
								sarData.append(dataFromSar)
								if i!=2:
									time.sleep(2)
							g_conn_pool[0].sendall((paraList+' 1').encode('utf-8'))
							# 对两个列表中的5组数据取平均值并存入数据库
							dataProcs(sarData,powerData,sqConn)

# 结束(Socket)
def csEnd(server):
	server.close()
	thrd_pool[0].join()
	thrd_pool[1].join()
	print('已关闭服务端')	

#-------------------------------------SQLite3--------------------------------
def dbInitial():
	conn=sqlite3.connect('test_data.db')
	print('数据库创建成功')
	curs=conn.cursor()

	# 表格共 73 列
	curs.execute('''CREATE TABLE IF NOT EXISTS METRICS
		(time_ID REAL, CPU_usr REAL, CPU_nice REAL, CPU_sys REAL, CPU_iowait REAL, 
	CPU_steal REAL, CPU_irq REAL, CPU_soft REAL, CPU_guest REAL, CPU_gnice REAL,
	CPU_idle REAL, CPU_mhz REAL,
	MEM_memused REAL, MEM_commit REAL, MEM_kbactive REAL, MEM_kbinact REAL, MEM_kbdirty REAL,
	MEM_kbanonpg REAL, MEM_kbstack REAL, MEM_kbpgtbl REAL, MEM_kbvmused REAL, MEM_pgpgin_s REAL,
	MEM_pgpgout_s REAL, MEM_fault_s, MEM_majflt_s REAL, MEM_pgfree_s REAL, MEM_pgscank_s REAL,
	MEM_pgsteal_s REAL, MEM_vmeff REAL, 
	DISK_tps REAL, DISK_rd_sec REAL, DISK_wr_sec REAL, DISK_avgrq_sz REAL, DISK_avgqu_sz REAL,
	DISK_await REAL, DISK_svctm REAL, DISK_util REAL,
	NET_rxpkg_s REAL, NET_txpkg_s REAL, NET_rxkb_s REAL, NET_txkb_s REAL, NET_rxcmp_s REAL,
	NET_txcmp_s REAL, NET_rxmcst_s REAL, NET_ifutil REAL, NET_rxerr_s REAL, NET_txerr_s REAL,
	NET_coll_s REAL, NET_rxdrop_s REAL, NET_txdrop_s REAL, NET_txcarr_s REAL, NET_rxfram_s REAL,
	NET_rxfifo_s REAL, NET_txfifo_s REAL,
	Q_runq_sz REAL, Q_plist_sz REAL, Q_ldavg_1 REAL, Q_ldavg_5 REAL, Q_ldavg_15 REAL,
	Q_blocked REAL,
	INTR_intr_s REAL,
	TASK_proc_s REAL, TASK_cswch_s REAL,
	IO_tps REAL, IO_rtps REAL, IO_wtps REAL, IO_bread_s REAL, IO_bwrtn_s REAL,
	IO_pswpin_s REAL, IO_pswpout_s REAL,
	SWP_swpused REAL, SWP_swpcad REAL,
	POWER_watt REAL);''') 
	return conn

def outputToFile(sqConn):
	curs=sqConn.cursor()
	# 打开文件
	output_file=open('metrics_and_power.txt', 'w')
	print('准备写入文件')
	cursor=curs.execute('SELECT * FROM METRICS')
	for row in cursor:
		for i in range(len(row)):
			output_file.write(str(row[i])+'\t')
		output_file.write('\n')
	output_file.close()
	print('写入完成')
	curs.close()
	print('关闭数据库')


#---------------------------------#
#            main函数        #
#---------------------------------#

if __name__=="__main__":
	
	# 初始化服务端
	server=csInitial()

	accept_client()

	# 发送测试
	#g_conn_pool[0].sendall('1okkkk'.encode('utf-8'))
	#g_conn_pool[1].sendall('2okkkk'.encode('utf-8'))
	
	# 与串口相连
	ser=connToPower()

	# 初始化数据库
	sqConn=dbInitial()
	
	try:
		# 进行主要工作
		cs_main(ser,sqConn)
	except:
		# 发生异常时结束线程，并将数据库中的数据写入到文件
		csEnd(server)
		outputToFile(sqConn)
	else:
		# 结束两个Socket通信相关的线程
		csEnd(server)

		# 关闭串口
		serialEnd(ser)

		# 将数据库中的数据输出到文件
		outputToFile(sqConn)

#__END__OF__CS_PY__	
