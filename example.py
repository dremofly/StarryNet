#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
StarryNet: empowering researchers to evaluate futuristic integrated space and terrestrial networks.
author: Zeqi Lai (zeqilai@tsinghua.edu.cn) and Yangtao Deng (dengyt21@mails.tsinghua.edu.cn)
"""

from starrynet.sn_observer import *
from starrynet.sn_orchestrater import *
from starrynet.sn_synchronizer import *

if __name__ == "__main__":
    # Starlink 5*5: 25 satellite nodes, 2 ground stations.
    # The node index sequence is: 25 sattelites, 2 ground stations.
    # In this example, 25 satellites and 2 ground stations are one AS.

    AS = [[1, 28]]  # Node #1 to Node #27 are within the same AS.
    GS_lat_long = [[50.110924, 8.682127], [46.635700, 14.311817], [43.185857, 20.9384857]
                   ]  # latitude and longitude of frankfurt and  Austria
    configuration_file_path = "./config.json.503"
    hello_interval = 1  # hello_interval(s) in OSPF. 1-200 are supported.

    print('Start StarryNet.')
    sn = StarryNet(configuration_file_path, GS_lat_long, hello_interval, AS)
    sn.create_nodes()
    sn.create_links()
    sn.run_routing_deamon()

    node_index1 = 1
    node_index2 = 2
    time_index = 2

    # distance between nodes at a certain time
    node_distance = sn.get_distance(node_index1, node_index2, time_index)
    print("node_distance (km): " + str(node_distance))

    # neighbor node indexes of node at a certain time
    neighbors_index = sn.get_neighbors(node_index1, time_index)
    print("neighbors_index: " + str(neighbors_index))

    # GS connected to the node at a certain time
    node_index1 = 7
    GSes = sn.get_GSes(node_index1, time_index)
    print("GSes are: " + str(GSes))

    # LLA of a node at a certain time
    LLA = sn.get_position(node_index1, time_index)
    print("LLA: " + str(LLA))

    sn.get_utility(time_index)  # CPU and memory useage

    # IPList of a node
    IP_list = sn.get_IP(node_index1)
    print("IP: " + str(IP_list))

    ratio = 0.4
    time_index = 5
    # random damage of a given ratio at a certain time
    # sn.set_damage(ratio, time_index)

    time_index = 25
    # random damage of a given ratio at a certain time
    # sn.set_damage(ratio, time_index)

    time_index = 10
    # sn.set_recovery(time_index)  # recover the damages at a certain time

    time_index = 50
    # sn.set_recovery(time_index)  # recover the damages at a certain time

    node_index1 = 27
    time_index = 15
    # routing table of a node at a certain time. The output file will be written at the working directory.
    # for i in range(20, 25): # time 
    #     for j in range(0, 26):
    #         sn.check_routing_table(j+1, i)

    sat = 1
    des = 27
    next_hop_sat = 2
    time_index = 10
    # set the next hop at a certain time. Sat, Des and NextHopSat are indexes and Sat and NextHopSat are neighbors.
    # sn.set_next_hop(sat, des, next_hop_sat, time_index)

    # node_index1 = 13
    # node_index2 = 14
    # time_index = 3
    # # ping msg of two nodes at a certain time. The output file will be written at the working directory.
    # sn.set_ping(node_index1, node_index2, time_index)
    count = 6
    for i in range(1, 80, 15):
        for ni in range(1, 3):
            node_index1 = ni
            node_index2 = ni + count
            time_index = i
            sn.set_ping(node_index1, node_index2, time_index)
        count+=1

    # perf example
    # node_index1 = 13
    # node_index2 = 14
    # time_index = 4
    # sn.set_perf(node_index1, node_index2, time_index)
    # for i in range(1, 80, 10):
        # for ni in range(1, 4):
            # node_index1 = ni
            # node_index2 = ni + 6
            # time_index = i
            # sn.set_perf(node_index1, node_index2, time_index)

    # quic example
    # node_index1 = 20
    # node_index2 = 21
    # time_index = 8
    # sn.set_quic(node_index1, node_index2, time_index)


    # ledbat example
    # node_index1 = 5
    # node_index2 = 8
    # time_index = 12
    # sn.set_led(node_index1, node_index2, time_index) # set ledbat

    sn.start_emulation()
    # sn.stop_emulation()
