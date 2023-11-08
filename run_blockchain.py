from starrynet.sn_observer import *
from starrynet.sn_orchestrater import *
from starrynet.sn_synchronizer import *
import pandas as pd
import sys
import os

    

if __name__ == "__main__":
    AS = [[1, 29]]  # Node #1 to Node #27 are within the same AS.
    # TODO 使用更准确的经纬度
    GS_lat_long = [[50.110924, 8.682127], [46.635700, 14.311817], [52.810924, 10.682127], [43.185857, 20.9384857]
                   ]  # latitude and longitude of frankfurt and  Austria
    configuration_file_path = "./config.json.nuc"
    hello_interval = 1  # hello_interval(s) in OSPF. 1-200 are supported.
    sn = StarryNet(configuration_file_path, GS_lat_long, hello_interval, AS)

    # # sn.create_nodes()
    # # sn.create_links()
    # # sn.run_routing_deamon()
    # # sn.run_blockchain_nodes()

    # container_id_list = sn_get_container_info(sn.remote_ssh) 
    # current_topo_path = "/home/hong/log/starrynet/log_dir_20230806-00_28_11/starlink-5-5-550-53-grid-LeastDelay-dir1/delay/1249.txt"
    # matrix = sn_get_param(current_topo_path)

    sn.set_deposit(1, 2, 2)
    sn.start_emulation()
    
    
