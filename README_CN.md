# 星网模拟器

星网模拟器用于模拟卫星互联网星座。

## 什么是星网模拟器？

星网模拟器可帮助您在指定时间内模拟定制的星座和地面站，并进行实时路由。借助星网模拟器，您可以在节点内测试可用性、带宽、损失，检查节点的路由状态，甚至破坏某些链接。

## 主要组成部分包括？

1. 配置文件（`config.json`）。
2. API库（`starrynet`）。
3. 利用API进行试验的示例（`example.py`）。
4. 路由配置文件（`bird.conf`）。
5. `setup.py`和`./bin/sn`。

## 准备工作

CentOS 7.9.2009或更高版本，Docker 20.10.17或更高版本，Python 3.6或更高版本。

1. 支持CentOS 7.9.2009和Python 3或Python 2，也支持Ubuntu 20.04 LTS（和18.04）。
2. 在模拟机器上安装Docker。

## 安装

然后运行`bash ./install.sh`来安装CLI sn，同时也会安装像`python3 -m pip install setuptools xlrd copy argparse time numpy random requests math skyfield sgp4 datetime paramiko`这样的包。

## 如何使用？

1. 准备数据目录：

在`config.json`中完成*remote_machine_IP, remote_machine_username 和 remote_machine_password*的填写，以指定运行模拟的远程机器。

将`config.json`，`starrynet`，`bird.conf`和`example.py`放在同一个工作目录中。

3. 开始模拟：

要指定您自己的星座，请复制`config.json`并根据您的卫星模拟环境填写其中的字段，包括星座名称、轨道数量、每个轨道的卫星数量、地面站数量、每个地面站连接的地面用户数量等。您只能更改`config.json`中的`Name`、`Altitude (km)`、`Cycle (s)`、`Inclination`、`Phase shift`、`# of orbit`、`# of satellites`、`Duration(s)`、`update_time (s)`、`satellite link bandwidth  ("X" Gbps)`、`sat-ground bandwidth ("X" Gbps)`、`satellite link loss ( 'X'% )`、`sat-ground loss ( 'X'% )`、`GS number`、`multi-machine('0' for no, '1' for yes)`、`antenna number`、`antenna_inclination_angle`、`remote_machine_IP`、`remote_machine_username`、`remote_machine_password`。

然后使用`example.py`中的API来开始您的实验。记得更改您的`config.json`的配置路径。

4. OSPF是唯一的内部路由协议。在`example.py`中，你需要设置hello-int

erval。（示例在example.py中）：

> HelloInterval = 1

5. 在`example.py`中，你需要按顺序指定地面站的纬度和经度。它们的节点索引将在卫星节点之后命名。

> GS_lat_long=[[50.110924,8.682127],[46.635700,14.311817]] # 德国法兰克福和奥地利

6. `ConfigurationFilePath`是你放置config.json文件的地方，`example.py`中有说明。
   > ConfigurationFilePath = "./config.json"

## 有哪些API？

> sn.create_nodes()

此API创建模拟用节点，包括卫星和地面站节点。

> sn.create_links()

此API为模拟创建初始网络链接。

> sn.run_routing_deamon()

此API启动网络的OSPF路由，否则网络将无路由协议运行。

> sn.get_distance(node_index1, node_index2, time_index)

此API返回在某个时间节点之间的距离。

> sn.get_neighbors(node_index1, time_index)

此API在某个时间返回一个节点的相邻节点索引。

> sn.get_GSes(node_index1, time_index)

此API在某个时间返回与节点连接的地面站。

> sn.get_position(node_index1, time_index)

此API在某个时间返回一个节点的LLA。

> sn.get_utility(time_index)

此API返回当前的CPU利用率和内存利用率。

> sn.get_IP(node_index1)

此API在某个时间返回一个节点的IP列表。

> sn.set_damage(ratio, time_index)

此API在某个时间为网络链接设置一个随机损伤，给定的比例。

> sn.set_recovery(time_index)

此API将在某个时间恢复所有损坏的链接。

> sn.check_routing_table(node_index1, time_index)

此API返回在某个时间的节点的路由表文件。输出文件可以在工作目录中找到。

> sn.set_next_hop(sat, des, next_hop_sat, time_index)

此API在某个时间设置下一跳。Sat、Des和NextHopSat是索引，Sat和NextHopSat是邻居。

> sn.set_ping(node_index1, node_index2, time_index)

此API在某个时间启动两个节点的ping消息。输出文件可以在工作目录中找到。

> sn.set_perf(node_index1, node_index2, time_index)

此API在某个时间启动两个节点的perf消息。输出文件可以在工作目录中找到。

> sn.start_emulation()

此API开始整个模拟的持续时间。

> sn.stop_emulation()

此API停止模拟并清理环境。

## 示例一：在Python中使用API

运行example.py模拟网络。

在这个示例中，模拟了来自Starlink的5*5颗卫星，其在550km的高度上，倾角为53度，还模拟了在德国法兰克福和奥地利的两个地面站。节点索引序列为：25颗卫星，2个地面

站。 25颗卫星和2个地面站在一个自治系统（AS）中，其中运行OSPF。在OSPF中，Hello_interval(s)被设为1秒。在`config.json`中指定AS，每个地面站有一个天线，其倾角为25度，用于连接最近的卫星。丢包和吞吐量也在`config.json`中设置。链接延迟更新的粒度是1秒。

模拟持续时间在`config.json`中设置为100秒。在#5秒处设置了30%的损坏比例，网络将在#10秒恢复。在#15秒时，我们想查看节点27的路由表，这可以在工作目录中找到。在#20秒时，我们将节点1的下一跳设为节点2，以便到达节点27。我们将从#30秒到#80秒从节点26到节点27的ping信息。运行后，当前路径将创建一个新的目录，可以在那里找到输出信息。

其他API帮助显示在#2秒时节点#1和节点#2之间的距离（以公里为单位），该时间的节点#1的邻居索引，#2秒时与节点#7连接的地面站，该节点在同一时间的LLA信息以及节点的所有IP。此外，get_utility会在该时间下载内存和CPU使用率信息。

## 示例二：在Shell中使用CLI

在config.json中完成*remote_machine_IP, remote_machine_username, remote_machine_password*以指定运行模拟的远程机器。其他字段也应如上所述填写。

> sn

在`config.json`的相同路径中，运行`sn`，你将看到starrynet CLI。如果你只在config.json中完成*remote_machine_IP, remote_machine_username, remote_machine_password*而不改变其他字段，`sn`会自动启动上述的5*5(卫星)+2(地面站)规模的网络。看下面的示例。

> sn -h

> sn

*这启动了默认的5*5+2规模的CLI。你也可以在config.json中指定你自定义的规模，并运行`sn -p "./config.json" -i 1 -n 27 -g 50.110924/8.682127/46.635700/14.311817`来启动你自己的模拟。这里的`-p`指的是自定义config.json的路径，`-i`指的是你自定义的hello数据包间隔（默认为10），`-n`指的是总节点数，`-g`指的是GSes的纬度和经度。*

> starrynet> help

> starrynet> create_nodes

> starrynet> create_links

> starrynet> run_routing_deamon

> starrynet> get_distance 1 2 10

*这意味着在#10秒时获取两个节点（#1和#2）的距离。*

> starrynet> get_neighbors 5 16

*这意味着在#16

秒时获取节点#5的邻居。*

> starrynet> get_GSes 8 20

*这意味着在#20秒时获取和节点#8连接的地面站。*

> starrynet> get_position 27 2

*这意味着在#2秒时获取节点#27的LLA。*

> starrynet> get_utility 20

*这意味着在#20秒时获取CPU和内存使用率。*

> starrynet> get_IP 6

*这意味着获取节点#6的所有IP。*

> starrynet> set_damage 0.3 5

*这意味着在#5秒时设置损坏比例为30%。*

> starrynet> set_recovery 10

*这意味着在#10秒恢复所有损坏的链接。*

> starrynet> check_routing_table 27 15

*这意味着在#15秒时查看节点#27的路由表。*

> starrynet> set_next_hop 1 27 2 20

*这意味着在#20秒时设置节点#1到节点#27的下一跳为节点#2。*

> starrynet> set_ping 26 27 30 80

*这意味着在#30秒到#80秒的时间内从节点#26到节点#27发送ping消息。*

> starrynet> set_perf 26 27 30 80

*这意味着在#30秒到#80秒的时间内从节点#26到节点#27发送perf消息。*

> starrynet> start_emulation

*这意味着开始模拟。*

> starrynet> stop_emulation

*这意味着停止模拟并清理环境。*