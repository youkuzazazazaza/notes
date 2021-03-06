# 容器跨越主机网络VXLAN

VXLAN技术是Linux内核本身就支持的一种网络虚拟化技术，可以直接在内核态完善封装和解封装的工作。

设计思想是在现有的三层网络智商，覆盖一层虚拟的，由内核VXLAN模块负责维护的二层网络，使链接VXLAN的主机或者容器可以像局域网一样进行通信。

为了能够在二层网络上打通隧道，VXLAN会在宿主机上设置一个特殊的网络设备作为隧道的两段，叫做VTEP。

VTEP的作用就是用来进行封装和解封装的对象，是二层的数据帧。

![2019-07-12-00-07-34](http://jikelearn.cn/2019-07-12-00-07-34.png)

流程如下：

1. 宿主1容器1发出请求后，携带目的地IP包，先出现在docker0的网桥上。
2. 在被路由到隧道的入口。
3. VXLAN为了把原始数据包发送到正确的宿主机上，需要找到这条隧道的出口，即是另外一台设备的上的VTEP设备。
4. 还是依靠路由规则来查找到对应的机器上。
5. 封装二层数据包。
6. 首先在路由上找到目的地的MAC地址，进行封装目的地设备的MAC地址+目的地容器IP地址+数据包。
7. 再次封装宿主机的外层数据帧，在内部数据帧前面加上VNI,VNI是VTEP设备识别某个数据帧是不是应该扫描自己处理的重要标识。
8. flannel.1设备扮演一个网器哦啊设备，根据FDB数据库找到对应查询出目的地IP地址与MAC地址。
9. 再次封装数据即可完成数据的封装。在转发到宿主机2上的网卡。
10. 从9倒着走一遍即可