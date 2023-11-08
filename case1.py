#!/usr/bin/python
# -*- coding: UTF-8 -*-

from starrynet.sn_observer import *
from starrynet.sn_orchestrater import *
from starrynet.sn_synchronizer import *
import pandas as pd
import os
from datetime import datetime
import shutil

def backup_res(remote_ssh, ping_or_res, dir):
    if ping_or_res == 'ping':
        backup_des = os.path.join(dir, 'ping')
    elif ping_or_res == 'perf1':
        backup_des = os.path.join(dir, 'perf1')
    elif ping_or_res == 'perf2':
        backup_des = os.path.join(dir, 'perf2')
    os.makedirs(backup_des, exist_ok=True)

    print("backup_des", backup_des)
    # sn_remote_cmd(remote_ssh, 'mv starlink-5-5-550-53-grid-LeastDelay {backup_des}/starlink-5-5-550-53-grid-LeastDelay_dir1')
    # sn_remote_cmd(remote_ssh, 'mv /home/hong/starlink-5-5-550-53-grid-LeastDelay {backup_des}/starlink-5-5-550-53-grid-LeastDelay_dir2')
    # sn_remote_cmd(remote_ssh, 'cp config.json.nuc2 {backup_des}/config.json.nuc2')

    shutil.copytree('starlink-5-5-550-53-grid-LeastDelay', f'{backup_des}/starlink-5-5-550-53-grid-LeastDelay_dir1')
    shutil.copytree('/home/hong/starlink-5-5-550-53-grid-LeastDelay', f'{backup_des}/starlink-5-5-550-53-grid-LeastDelay_dir2')
    shutil.copy('current.json', f'{backup_des}/current.json')


def modify_config(bandwidth, loss, base_file, new_file):
    # 读取源文件内容
    with open(base_file, 'r') as file:
        data = json.load(file)

    # 修改字典中的对应值
    data['satellite link bandwidth ("X" Gbps)'] = bandwidth  # 请根据需要更改此值
    data['satellite link loss ("X"% )'] = loss  # 请根据需要更改此值

    # 将修改后的字典写回目标文件
    with open(new_file, 'w') as file:
        json.dump(data, file, indent=4)  # indent=4 使输出更易读
    

if __name__ == "__main__":
    AS = [[1, 28]]  # Node #1 to Node #27 are within the same AS.
    GS_lat_long = [[50.110924, 8.682127], [46.635700, 14.311817], [43.185857, 20.9384857]
                   ]  # latitude and longitude of frankfurt and  Austria
    # configuration_file_path = "./config.json.503"
    base_configuration_file_path = "./config.json.nuc2"
    configuration_file_path = "./current.json"

    hello_interval = 1  # hello_interval(s) in OSPF. 1-200 are supported.

    final_time = 500
    time_interval = 10


    bandwidth_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    loss_list = [0, 0.05, 0.1, 0.3, 0.5, 1, 3, 5, 10, 20]

    for bw in bandwidth_list:
        for loss in loss_list:
            now = datetime.now()
            time_str = now.strftime("%Y%m%d_%H%M%S")
            # backup_dir = "/home/hong/log/cc_" + time_str
            backup_dir = f"/home/hong/log/cc_{time_str}_{bw}_{loss}"
            os.makedirs(backup_dir, exist_ok=True)
            modify_config(bw, loss, base_configuration_file_path, configuration_file_path)
            for j in range(2, 26):
                sn = StarryNet(configuration_file_path, GS_lat_long, hello_interval, AS)
                sn.create_nodes()
                sn.create_links()
                sn.run_routing_deamon()
                src = 1
                des = j
                backup_log = os.path.join(backup_dir, f"s{src}_d{des}")
                for i in range(1, final_time, time_interval):
                    # sn.set_ping(src, des, i)
                    sn.set_perf(src, des, i)
                sn.start_emulation()
                remote_ssh = sn.remote_ssh
                backup_res(remote_ssh, 'perf1', backup_log)

                sn2 = StarryNet(configuration_file_path, GS_lat_long, hello_interval, AS)
                sn2.create_nodes()
                sn2.create_links()
                sn2.run_routing_deamon()
                for i in range(1, final_time, time_interval):
                    sn2.set_ping(src, des, i)
                sn2.start_emulation()
                remote_ssh2 = sn2.remote_ssh
                backup_res(remote_ssh2, 'ping', backup_log)
    
                sn3 = StarryNet(configuration_file_path, GS_lat_long, hello_interval, AS)
                sn3.create_nodes()
                sn3.create_links()
                sn3.run_routing_deamon()
                for i in range(1, final_time, time_interval):
                    sn3.set_perf2(src, des, i)
                sn3.start_emulation()
                remote_ssh3 = sn3.remote_ssh
                backup_res(remote_ssh3, 'perf2', backup_log)