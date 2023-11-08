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

    cmd = "docker run -d --name public_nodes --cap-add ALL -p 8545:8545 --net terrestrial --ip 192.168.2.254 mynode"
    createRes = sn_remote_cmd(remote_ssh, cmd)
    print(createRes)

    getIdCmd = "docker ps | grep public_nodes"
    idRes = sn_remote_cmd(remote_ssh, getIdCmd)
    print(idRes)
    publicId = idRes[0].split()[0]
    print(publicId)

    copyFisco = f"docker cp /home/hong/nodes/192.168.2.254 {publicId}:/fisco"
    copyRes = sn_remote_cmd(remote_ssh, copyFisco)
    # print(copyRes)
    modifyConfigIni = f"docker exec -d {publicId} sed -i 's/jsonrpc_listen_ip=127.0.0.1/jsonrpc_listen_ip=0.0.0.0/' /fisco/node0/config.ini"
    modifyRes = sn_remote_cmd(remote_ssh, modifyConfigIni)

    startFisco = f"docker exec -d {publicId} bash /fisco/start_all.sh"
    fiscoRes = sn_remote_cmd(remote_ssh, startFisco)
    print(fiscoRes)

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
    # print(sat_num, orbit_num, gs_num)

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
            # print(f"gs {i}: {connectRes}")
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

def rename_interface(container_idx, target_interface, g_index):
    """
    修改interface的名字
    """
    print("docker exec -d " +
              container_idx +
              " ip link set dev " + target_interface + " down")
    # 将原来的interface关闭
    os.system("docker exec -d " +
              container_idx +
              " ip link set dev " + target_interface + " down")
    
    print("docker exec -d " +
              container_idx +
              " ip link set dev " + target_interface + " name " + "G" +
              str(g_index))
    # interface rename 为 G{num} 的格式。
    os.system("docker exec -d " +
              container_idx +
              " ip link set dev " + target_interface + " name " + "G" +
              str(g_index))

    # 开启rename后的interface
    os.system("docker exec -d " +
              container_idx +
              " ip link set dev G" +
              str(g_index) +
              " up")

    os.system("docker exec -d " + container_idx +
              " ip link set dev G" + str(g_index) + " up")

def get_ground_interface(container_idx, remote_ssh):
    """
    获取节点的Ground interface对应的interface name
    """
    getInterfaceName = f'docker exec -it {container_idx} ip addr | grep 192.168.2'
    getRes = sn_remote_cmd(remote_ssh, getInterfaceName)
    targetInterface = getRes[0].split()[-1]
    return targetInterface

def generate_ospf_for_public_node(sn: StarryNet, remote_ftp):
    """
    为public node生成OSPF配置文件
    """
    remote_ssh = sn.remote_ssh
    container_id_list = sn_get_container_info(remote_ssh)
    container_idx = container_id_list[0]

    targetInterface = get_ground_interface(container_idx, remote_ssh)

    Q = []
    Q.append(
        "log \"/var/log/bird.log\" { debug, trace, info, remote, warning, error, auth, fatal, bug };"
    )
    Q.append("debug protocols all;")
    Q.append("protocol device {")
    Q.append("}")
    Q.append(" protocol direct {")
    Q.append("    disabled;		# Disable by default")
    Q.append("    ipv4;			# Connect to default IPv4 table")
    Q.append("    ipv6;			# ... and to default IPv6 table")
    Q.append("}")
    Q.append("protocol kernel {")
    Q.append(
        "    ipv4 {			# Connect protocol to IPv4 table by channel")
    Q.append(
        "        export all;	# Export to protocol. default is export none"
    )
    Q.append("    };")
    Q.append("}")
    Q.append("protocol static {")
    Q.append(
        "    ipv4;			# Again, IPv6 channel with default options")
    Q.append("}")
    Q.append("protocol ospf {")
    Q.append("    ipv4 {")
    Q.append("        import all;")
    Q.append("    };")
    Q.append("    area 0 {")
    Q.append('    interface "' + targetInterface + '" {')
    Q.append("        type broadcast;		# Detected by default")
    Q.append("        cost 256;")
    Q.append("        hello 1" +
             ";			# Default hello perid 10 is too long")
    Q.append("    };")
    Q.append("    };")
    Q.append(" }")

    f = open("bird.conf", 'w')
    for item in Q:
        f.write(str(item) + '\n')
    f.close()
    remote_ftp.put('bird.conf', 'bird.conf')
    
    copyConf = f"docker cp bird.conf {container_idx}:/"
    sn_remote_cmd(remote_ssh, copyConf)

    runBird = f"docker exec -d {container_idx} bird -c /bird.conf"
    res = sn_remote_cmd(remote_ssh, runBird)
    print('runBird res')
    print(res)
    
def modify_ground_ospf(sn: StarryNet):
    """
    修改地面站的ospf文件，向其中添加地面网络的interface G数字
    """
    remote_ssh = sn.remote_ssh
    container_id_list = sn_get_container_info(remote_ssh)
    sat_num = sn.sat_number
    orbit_num = sn.orbit_number
    gs_num = sn.fac_num
    for i in range(sat_num*orbit_num+1, gs_num+sat_num*orbit_num+1):
        container_idx = container_id_list[i]

        targetInterface = get_ground_interface(container_idx, remote_ssh)
        lsConf = f'docker exec -it {container_idx} ls /'
        lsRes = sn_remote_cmd(remote_ssh, lsConf)
        confFile = lsRes[0].split()[0]
    
        cmd = f'docker exec -d {container_idx} python add_ospf.py {targetInterface} /{confFile}'
        sn_remote_cmd(remote_ssh, cmd)

        psCmd = f'docker exec -it {container_idx} ps aux | grep bird'
        psRes = sn_remote_cmd(remote_ssh, psCmd)
        # print(psCmd, psRes)
        if psRes:
            pid = psRes[0].split()[1]
        
        if pid:
            killCmd = f'docker exec -d {container_idx} kill -9 {pid}'
            killRes = sn_remote_cmd(remote_ssh, killCmd)
            print(killRes)

        # print(i)
        restartCmd = f'docker exec -it {container_idx} bird -c B{i}.conf'
        reRes = sn_remote_cmd(remote_ssh, restartCmd)
        print(reRes)


def modify_ground_interface(sn: StarryNet):
    """
    修改ground station的interface名
    """
    remote_ssh = sn.remote_ssh
    container_id_list = sn_get_container_info(remote_ssh)
    sat_num = sn.sat_number
    orbit_num = sn.orbit_number
    gs_num = sn.fac_num

    g_index = 1
    for i in range(sat_num*orbit_num+1, gs_num+sat_num*orbit_num+1):
        container_idx = container_id_list[i]

        targetInterface = get_ground_interface(container_idx, remote_ssh)
        # getInterfaceName = f'docker exec -it {container_idx} ip addr | grep 192.168.2'
        # getRes = sn_remote_cmd(remote_ssh, getInterfaceName)
        # # print(getRes)
        # targetInterface = getRes[0].split()[-1]
        print(targetInterface)
        rename_interface(container_idx, targetInterface, g_index)
        g_index += 1
    data_center_id = container_id_list[0]

    # getInterfaceName = f'docker exec -it {data_center_id} ip addr | grep 192.168.2'
    # getRes = sn_remote_cmd(remote_ssh, getInterfaceName)
    # # print(getRes)
    # targetInterface = getRes[0].split()[-1]

    targetInterface = get_ground_interface(data_center_id, remote_ssh)

    rename_interface(data_center_id, targetInterface, g_index)

def copy_ospf_script(sn: StarryNet):
    remote_ssh = sn.remote_ssh
    container_id_list = sn_get_container_info(remote_ssh)
    sat_num = sn.sat_number
    orbit_num = sn.orbit_number
    gs_num = sn.fac_num
    for i in range(sat_num*orbit_num+1, gs_num+sat_num*orbit_num+1):
        container_idx = container_id_list[i]
        copyCmd = f'docker cp add_ospf.py {container_idx}:/'
        os.system(copyCmd)

def main():
    typer.echo("typer program")
    # TODO 使用更准确的经纬度

    resetOrNot = True # 不需要初始化的话 False (节省时间)
    locations = get_ll("region.json")

    if resetOrNot:
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
    # print(f'GS_lat_long: {GS_lat_long}')
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

    if resetOrNot:
        sn.create_nodes()
        sn.create_links()
        sn.run_routing_deamon()

        create_terrestrial_network(sn)

        sn.run_blockchain_nodes(sharding_num=2)

        create_public_node(sn)
        modify_ground_interface(sn)
    remote_ftp = sn.remote_ftp
    copy_malicious_scripts(sn)
    copy_ospf_script(sn)

    generate_ospf_for_public_node(sn, remote_ftp)

    copy_ospf_script(sn)
    modify_ground_ospf(sn)


    # for i in range(2):
    node_index1 = 1
    node_index2 = 2
    time_index = 2
    # sn.set_deposit(node_index1, node_index2, time_index)

    # sn.start_emulation()

if __name__ == "__main__":
  typer.run(main)