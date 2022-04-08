# 服务器压力模拟器及指标测量
# LoadSimulator&Measuring
- - -
## 程序简介| Introduction
作为《数据中心多元非线性硬件能效模型的研究》项目的重要部分，本程序将对服务器进行负载的模拟及各指标的测量。
- - -
## 程序构成 | Component
[Master程序]包含三个模块，分别为[cs.py] [loadRunner.py] [sar.py]
- - -
## 运行操作系统 | OS
* cs.py: Windows10/macOS/Linux
* sar.py/LoadRunner.py: Linux(CentOS is preferred)
- - -
## 环境配置 | Environment Construction
* Python 3.0
* sqlite3
* [lookbusy-1.4]
* cpufrequtils
* pip3 pyserial
* iozone
* iperf3
- - -
## 运行说明 ｜ Execution
1. 在待测试主机或服务器上，以超级用户的身份先后运行LoadRunner.py和sar.py
2. 在另一台主机上运行cs.py
- - -
## 编写人员 | Contributors
* Yang Yongzhen [yangyongzhenyang][1]
* Li Pengcheng [PecholaL][2]
* Zhao Renmin [Fangtang74][3]
* Zhao Zerui [zzr2867][4]

[1]: https://github.com/yangyongzhenyang
[2]: https://github.com/PecholaL
[3]: https://github.com/Fangtang74
[4]: https://github.com/zzr2867
[lookbusy-1.4]:https://github.com/2018SEUer/LoadSimulator-Measuring/blob/main/Environment%20Construction/lookbusy-1.4.tar
[cs.py]:https://github.com/2018SEUer/LoadSimulator-Measuring/blob/main/Master%20Program/cs.py
[loadRunner.py]:https://github.com/2018SEUer/LoadSimulator-Measuring/blob/main/Master%20Program/loadRunner.py
[sar.py]:https://github.com/2018SEUer/LoadSimulator-Measuring/blob/main/Master%20Program/sar.py
[Master程序]:https://github.com/2018SEUer/LoadSimulator-Measuring/tree/main/Master%20Program/
