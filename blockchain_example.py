from starrynet.sn_observer import *
from starrynet.sn_orchestrater import *
from starrynet.sn_synchronizer import *
import pandas as pd
import sys
import typer
import json
import os

def create_terrestrial_network(sn: StarryNet):
    """
    创建一个地面网络，用于ground stations的连接
    """
    remote_ssh = sn.remote_ssh
    sat_num = sn.sat_number
    orbit_num = sn.orbit_number
    gs_num = sn.fac_num
    print(sat_num, orbit_num, gs_num)

    network_name = "terrestrial"
    network_ip = "192.168.2."

    # res = sn_remote_cmd(remote_ssh, f"docker network create {network_name} --subnet {network_ip}0/24")
    # print(res)

    container_id_list = sn_get_container_info(remote_ssh)
    for i in range(sat_num*orbit_num, gs_num+sat_num*orbit_num):
        container_idx = container_id_list[i]
        connectRes = sn_remote_cmd(remote_ssh, f"docker network connect {network_name} {container_idx} --ip {network_ip}{i}")
        print(f"gs {i}: {connectRes}")


def get_ll(file) -> list:
    # 获取经纬度值
    # 打开和读取JSON文件
    with open('region.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 从数据中提取所有的经纬度
    # TODO 这里的解析需要根据region.json中的数据结构来进行修改
    locations = []
    for region in data['districts']:
        longitude = region['center']['longitude']
        latitude = region['center']['latitude']
        locations.append([longitude, latitude])

    # print(locations)
    return locations


def main():
    typer.echo("typer program")
    # TODO 使用更准确的经纬度

    locations = get_ll("region.json")

    clearNode = "rm -rf /home/hong/nodes"
    os.system(clearNode)
    
    # GS_lat_long = locations[:5]

    GS_lat_long = [[50.110924, 8.682127],
                    [46.635700, 14.311817],
                    [43.185857, 20.9384857],
                    [49.283858, 9.28385],
                    [48.828737, 12.943848],
                    [48.1827, 10],
                    [47, 4],
                    [45, 13],
                    [44, 2],
                    [51, 6]
                   ]  # latitude and longitude of frankfurt and  Austria
    print(f'GS_lat_long: {GS_lat_long}')
    # configuration_file_path = "./config.json.6020"
    configuration_file_path = os.environ.get('STARRY_CONFIG')

    hello_interval = 1  # hello_interval(s) in OSPF. 1-200 are supported.
    AS = [[1, 25+len(GS_lat_long)]]  # Node #1 to Node #27 are within the same AS.
    sn = StarryNet(configuration_file_path, GS_lat_long, hello_interval, AS)

    sn.create_nodes()
    sn.create_links()
    sn.run_routing_deamon()
    create_terrestrial_network(sn)
    sn.run_blockchain_nodes()


    

    # for i in range(2):
    node_index1 = 1
    node_index2 = 2
    time_index = 2
    sn.set_deposit(node_index1, node_index2, time_index)

    sn.start_emulation()


if __name__ == "__main__":
  typer.run(main)
    

