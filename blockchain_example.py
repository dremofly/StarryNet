from starrynet.sn_observer import *
from starrynet.sn_orchestrater import *
from starrynet.sn_synchronizer import *
import pandas as pd
import sys
import typer
import json
import os

def modify_config_duration(base_file, new_file, duration):
        # 读取源文件内容
    with open(base_file, 'r') as file:
        data = json.load(file)

    # 修改字典中的对应值
    data['Duration (s)'] = duration  # 请根据需要更改此值

    # 将修改后的字典写回目标文件
    with open(new_file, 'w') as file:
        json.dump(data, file, indent=4)  # indent=4 使输出更易读
    
def create_public_node(sn: StarryNet):
    remote_ssh = sn.remote_ssh

    # cmd = "docker run -d --name public_nodes -p 8545:8545 --net terrestrial --ip 192.168.2.254 mynode"
    # createRes = sn_remote_cmd(remote_ssh, cmd)
    # print(createRes)

    getIdCmd = "docker ps | grep public_nodes"
    idRes = sn_remote_cmd(remote_ssh, getIdCmd)
    print(idRes)
    publicId = idRes[0].split()[0]
    print(publicId)

def copy_malicious_scripts(sn: StarryNet):
    remote_ssh = sn.remote_ssh
    container_id_list = sn_get_container_info(remote_ssh)
    prefix = 'project/project_congestionControl/StarryNet/'

    for id in container_id_list:
        copyCmd = f"docker cp {prefix}submitlog.py {id}:/"
        copyCmd2 = f"docker cp {prefix}verify_contract.py {id}:/"
        # print(copyCmd)
        # print(copyCmd2)
        res = sn_remote_cmd(remote_ssh, copyCmd)
        # print(res)
        res2 = sn_remote_cmd(remote_ssh, copyCmd2)
        # print(res2)

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

    # create network
    try:
        res = sn_remote_cmd(remote_ssh, f"docker network create {network_name} --subnet {network_ip}0/24")
        print(res)
    except Exception as e:
        print(f"{network_name} exists")

    container_id_list = sn_get_container_info(remote_ssh)
    for i in range(sat_num*orbit_num, gs_num+sat_num*orbit_num):
        try:
            container_idx = container_id_list[i]
            connectRes = sn_remote_cmd(remote_ssh, f"docker network connect {network_name} {container_idx} --ip {network_ip}{i}")
            print(f"gs {i}: {connectRes}")
        except Exception as e:
            print(f"error: i {i}, container list {container_id_list}", e)
            exit(1)


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

    clearNode = "rm -rf /home/hong/nodes*"
    os.system(clearNode)
    
    # GS_lat_long = locations[:5]
    GS_lat_long = [[37.950, -138.682127],
                [-38.398690,-135.251976],
                [-22.679610,171.437716],
                [49.283858, 9.28385],
                [5.454320,121.290221],
                [48.1827, 10],
                [47, 4],
                [45, 13],
                [44, 2],
                [51, 6]
                ]
    print(f'GS_lat_long: {GS_lat_long}')
    # configuration_file_path = "./config.json.6020"
    # export STARRY_CONFIG=config.json.nuc
    # configuration_file_path = os.environ.get('STARRY_CONFIG')


    duration = 10
    base_configuration_file_path = "./config.json.nuc"
    configuration_file_path = "./current2.json"
    modify_config_duration(base_configuration_file_path, configuration_file_path, duration)

    hello_interval = 1  # hello_interval(s) in OSPF. 1-200 are supported.
    AS = [[1, 25+len(GS_lat_long)]]  # Node #1 to Node #27 are within the same AS.
    sn = StarryNet(configuration_file_path, GS_lat_long, hello_interval, AS)

    resetOrNot = True # 不需要初始化的话 False (节省时间)
    if resetOrNot:
        sn.create_nodes()
        sn.create_links()
        sn.run_routing_deamon()

        create_terrestrial_network(sn)

        sn.run_blockchain_nodes(sharding_num=2)

    # for i in range(2):
    node_index1 = 1
    node_index2 = 2
    time_index = 2
    # sn.set_deposit(node_index1, node_index2, time_index)

    sn.start_emulation()

if __name__ == "__main__":
  typer.run(main)