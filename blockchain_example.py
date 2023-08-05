from starrynet.sn_observer import *
from starrynet.sn_orchestrater import *
from starrynet.sn_synchronizer import *
import pandas as pd
import sys

def deploy_contract(container_id_list, sat_number) -> str:
    """
    Desc: 部署一个名为SimpleBank的合约，返回值为合约的地址
    """

    container_idx = container_id_list[sat_number]
    
    deployContractCmd = f"docker exec -i {container_idx} bash fisco-client/console/console.sh deploy SimpleBank"
    res = sn_remote_cmd(sn.remote_ssh, deployContractCmd)

    print(f"deploy contract: {res}")

    return res[1].split(':')[1].strip()
    

if __name__ == "__main__":
    AS = [[1, 29]]  # Node #1 to Node #27 are within the same AS.
    # TODO 使用更准确的经纬度
    GS_lat_long = [[50.110924, 8.682127], [46.635700, 14.311817], [52.810924, 10.682127], [43.185857, 20.9384857]
                   ]  # latitude and longitude of frankfurt and  Austria
    configuration_file_path = "./config.json.nuc"
    hello_interval = 1  # hello_interval(s) in OSPF. 1-200 are supported.
    sn = StarryNet(configuration_file_path, GS_lat_long, hello_interval, AS)

    sn.create_nodes()
    sn.create_links()
    sn.run_routing_deamon()
    sn.run_blockchain_nodes()

    container_id_list = sn_get_container_info(sn.remote_ssh)
    deploy_contract(container_id_list, sn.sat_number)



    # sn.start_emulation()