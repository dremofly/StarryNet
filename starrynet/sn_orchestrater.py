import os
import threading
import sys
from time import sleep
import numpy
import subprocess
import select
import re
import random
"""
Used in the remote machine for link updating, initializing links, damaging and recovering links and other functionalities。
author: Yangtao Deng (dengyt21@mails.tsinghua.edu.cn) and Zeqi Lai (zeqilai@tsinghua.edu.cn) 
"""


def sn_get_right_satellite(current_sat_id, current_orbit_id, orbit_num):
    if current_orbit_id == orbit_num - 1:
        return [current_sat_id, 0]
    else:
        return [current_sat_id, current_orbit_id + 1]


def sn_get_down_satellite(current_sat_id, current_orbit_id, sat_num):
    if current_sat_id == sat_num - 1:
        return [0, current_orbit_id]
    else:
        return [current_sat_id + 1, current_orbit_id]


def sn_ISL_establish(current_sat_id, current_orbit_id, container_id_list,
                     orbit_num, sat_num, constellation_size, matrix, bw, loss):
    current_id = current_orbit_id * sat_num + current_sat_id # 当前的容器的序号
    isl_idx = current_id * 2 + 1 #  
    # Establish intra-orbit ISLs
    # (Down):
    [down_sat_id,
     down_orbit_id] = sn_get_down_satellite(current_sat_id, current_orbit_id,
                                            sat_num)
    print()
    print(f"[func begin {isl_idx}/{constellation_size*2}] - sn_ISL_establish") 
    print("[" + str(isl_idx) + "/" + str(constellation_size * 2) +
          "] Establish intra-orbit ISL from: (s " + str(current_sat_id) + ", o " +
          str(current_orbit_id) + ") to (" + str(down_sat_id) + "," +
          str(down_orbit_id) + ")")
    ISL_name = "Le_" + str(current_sat_id) + "-" + str(current_orbit_id) + \
        "_" + str(down_sat_id) + "-" + str(down_orbit_id)
    address_16_23 = isl_idx >> 8 # 
    address_8_15 = isl_idx & 0xff
    # Create internal network in docker.
    os.system('docker network create ' + ISL_name + " --subnet 10." +
              str(address_16_23) + "." + str(address_8_15) + ".0/24")
    print(f'[Create ISL {current_id}:]' + 'docker network create ' + ISL_name +
          " --subnet 10." + str(address_16_23) + "." + str(address_8_15) +
          ".0/24")
    os.system('docker network connect ' + ISL_name + " " +
              str(container_id_list[current_orbit_id * sat_num +
                                    current_sat_id]) + " --ip 10." +
              str(address_16_23) + "." + str(address_8_15) + ".40") # TODO 这里的current_orbit_id * sat_num+current_sat_id不就是current_id吗
    delay = matrix[current_orbit_id * sat_num +
                   current_sat_id][down_orbit_id * sat_num + down_sat_id]
    
    # ==== Target interface 1 ====
    print()
    print("[open 1] " + "docker exec -it " +
            str(container_id_list[current_orbit_id * sat_num +
                                  current_sat_id]) +
            " ip addr | grep -B 2 10." + str(address_16_23) + "." +
            str(address_8_15) +
            ".40 | head -n 1 | awk -F: '{ print $2 }' | tr -d '[:blank:]'")
    
    # 下面的current_orbit_id*sat_num+current_sat_id不就是current_id吗
    with os.popen(
            "docker exec -it " +
            str(container_id_list[current_orbit_id * sat_num +
                                  current_sat_id]) +
            " ip addr | grep -B 2 10." + str(address_16_23) + "." +
            str(address_8_15) +
            ".40 | head -n 1 | awk -F: '{ print $2 }' | tr -d '[:blank:]'") as f:
        ifconfig_output = f.readline()
        target_interface = str(ifconfig_output).split("@")[0]
        print(f"ifconfig_output 1: {ifconfig_output}, target_interface 1: {target_interface}")

        print("docker exec -d " +
                  str(container_id_list[current_orbit_id * sat_num +
                                        current_sat_id]) +
                  " ip link set dev " + target_interface + " down")
        os.system("docker exec -d " +
                  str(container_id_list[current_orbit_id * sat_num +
                                        current_sat_id]) +
                  " ip link set dev " + target_interface + " down")

        # interface rename
        print("docker exec -d " +
                  str(container_id_list[current_orbit_id * sat_num +
                                        current_sat_id]) +
                  " ip link set dev " + target_interface + " name " + "B" +
                  str(current_orbit_id * sat_num + current_sat_id + 1) +
                  "-eth" + str(down_orbit_id * sat_num + down_sat_id + 1))
        os.system("docker exec -d " +
                  str(container_id_list[current_orbit_id * sat_num +
                                        current_sat_id]) +
                  " ip link set dev " + target_interface + " name " + "B" +
                  str(current_orbit_id * sat_num + current_sat_id + 1) +
                  "-eth" + str(down_orbit_id * sat_num + down_sat_id + 1))

        print("docker exec -d " +
                  str(container_id_list[current_orbit_id * sat_num +
                                        current_sat_id]) +
                  " ip link set dev B" +
                  str(current_orbit_id * sat_num + current_sat_id + 1) +
                  "-eth" + str(down_orbit_id * sat_num + down_sat_id + 1) +
                  " up")
        os.system("docker exec -d " +
                  str(container_id_list[current_orbit_id * sat_num +
                                        current_sat_id]) +
                  " ip link set dev B" +
                  str(current_orbit_id * sat_num + current_sat_id + 1) +
                  "-eth" + str(down_orbit_id * sat_num + down_sat_id + 1) +
                  " up")

        print("docker exec -d " +
                  str(container_id_list[current_orbit_id * sat_num +
                                        current_sat_id]) +
                  " tc qdisc add dev B" +
                  str(current_orbit_id * sat_num + current_sat_id + 1) +
                  "-eth" + str(down_orbit_id * sat_num + down_sat_id + 1) +
                  " root netem delay " + str(delay) + "ms loss " + str(loss) + "% rate " + str(bw) + "Gbps")
        os.system("docker exec -d " +
                  str(container_id_list[current_orbit_id * sat_num +
                                        current_sat_id]) +
                  " tc qdisc add dev B" +
                  str(current_orbit_id * sat_num + current_sat_id + 1) +
                  "-eth" + str(down_orbit_id * sat_num + down_sat_id + 1) +
                  " root netem delay " + str(delay) + "ms loss " + str(loss) + "% rate " + str(bw) + "Gbps")
        try:
            interface1 = subprocess.run(["docker", "exec", "-it", container_id_list[current_orbit_id * sat_num +
                                            current_sat_id], "tc", "-s", "qdisc", "ls", "dev", "B"+str(current_orbit_id * sat_num + current_sat_id + 1) +
                      "-eth" + str(down_orbit_id * sat_num + down_sat_id + 1)], capture_output=True, text=True)
            print(f"interface 1: {interface1}")
        except Exception as e:
            print("Error: interface 1 ", e)
            
        # TODO 是否需要添加结果的检测
                  
    print('[Add current node:]' + 'docker network connect ' + ISL_name + " " +
          str(container_id_list[current_orbit_id * sat_num + current_sat_id]) +
          " --ip 10." + str(address_16_23) + "." + str(address_8_15) + ".40")
    os.system('docker network connect ' + ISL_name + " " +
              str(container_id_list[down_orbit_id * sat_num + down_sat_id]) +
              " --ip 10." + str(address_16_23) + "." + str(address_8_15) +
              ".10")
            
    # ==== Target interface 2 ====
    print(
            "[open 2] docker exec -it " +
            str(container_id_list[down_orbit_id * sat_num + down_sat_id]) +
            " ip addr | grep -B 2 10." + str(address_16_23) + "." +
            str(address_8_15) +
            ".10 | head -n 1 | awk -F: '{ print $2 }' | tr -d '[:blank:]'")
    with os.popen(
            "docker exec -it " +
            str(container_id_list[down_orbit_id * sat_num + down_sat_id]) +
            " ip addr | grep -B 2 10." + str(address_16_23) + "." +
            str(address_8_15) +
            ".10 | head -n 1 | awk -F: '{ print $2 }' | tr -d '[:blank:]'") as f:
        ifconfig_output = f.readline()
        target_interface = str(ifconfig_output).split("@")[0]
        print(f"target_interface 2: {target_interface}")
        os.system("docker exec -d " +
                  str(container_id_list[down_orbit_id * sat_num +
                                        down_sat_id]) + " ip link set dev " +
                  target_interface + " down")
        os.system("docker exec -d " +
                  str(container_id_list[down_orbit_id * sat_num +
                                        down_sat_id]) + " ip link set dev " +
                  target_interface + " name " + "B" +
                  str(down_orbit_id * sat_num + down_sat_id + 1) + "-eth" +
                  str(current_orbit_id * sat_num + current_sat_id + 1))
        os.system("docker exec -d " +
                  str(container_id_list[down_orbit_id * sat_num +
                                        down_sat_id]) + " ip link set dev B" +
                  str(down_orbit_id * sat_num + down_sat_id + 1) + "-eth" +
                  str(current_orbit_id * sat_num + current_sat_id + 1) + " up")
        os.system("docker exec -d " +
                  str(container_id_list[down_orbit_id * sat_num +
                                        down_sat_id]) + " tc qdisc add dev B" +
                  str(down_orbit_id * sat_num + down_sat_id + 1) + "-eth" +
                  str(current_orbit_id * sat_num + current_sat_id + 1) +
                  " root netem delay " + str(delay) + "ms loss " + str(loss) + "% rate " + str(bw) + "Gbps")
        print("docker " + " exec" + " -it " + container_id_list[current_orbit_id * sat_num +
                                        current_sat_id] + " tc" + " -s" + " qdisc" + " ls" + " dev" + " B "+str(current_orbit_id * sat_num + current_sat_id + 1) +
                  " -eth " + str(down_orbit_id * sat_num + down_sat_id + 1))
        try:
            interface2 = subprocess.run(["docker", "exec", "-it", container_id_list[current_orbit_id * sat_num +
                                            current_sat_id], "tc", "-s", "qdisc", "ls", "dev", "B"+str(current_orbit_id * sat_num + current_sat_id + 1) +
                      "-eth" + str(down_orbit_id * sat_num + down_sat_id + 1)], capture_output=True, text=True)
            print(f"interface 2: {interface2}")
        except Exception as e:
            print("Error: interface 2 ", e)

    print('[Add down node:]' + 'docker network connect ' + ISL_name + " " +
          str(container_id_list[down_orbit_id * sat_num + down_sat_id]) +
          " --ip 10." + str(address_16_23) + "." + str(address_8_15) + ".10")

    print("Add 10." + str(address_16_23) + "." + str(address_8_15) +
          ".40/24 and 10." + str(address_16_23) + "." + str(address_8_15) +
          ".10/24 to (" + str(current_sat_id) + "," + str(current_orbit_id) +
          ") to (" + str(down_sat_id) + "," + str(down_orbit_id) + ")")
    isl_idx = isl_idx + 1

    # Establish inter-orbit ISLs
    # (Right):
    [right_sat_id,
     right_orbit_id] = sn_get_right_satellite(current_sat_id, current_orbit_id,
                                              orbit_num)
    print("[" + str(isl_idx) + "/" + str(constellation_size * 2) +
          "] Establish inter-orbit ISL from: (" + str(current_sat_id) + "," +
          str(current_orbit_id) + ") to (" + str(right_sat_id) + "," +
          str(right_orbit_id) + ")")
    ISL_name = "La_" + str(current_sat_id) + "-" + str(current_orbit_id) + \
        "_" + str(right_sat_id) + "-" + str(right_orbit_id)
    address_16_23 = isl_idx >> 8
    address_8_15 = isl_idx & 0xff
    # Create internal network in docker.
    os.system('docker network create ' + ISL_name + " --subnet 10." +
              str(address_16_23) + "." + str(address_8_15) + ".0/24")
    print(f'[Create ISL {current_id}:]' + 'docker network create ' + ISL_name +
          " --subnet 10." + str(address_16_23) + "." + str(address_8_15) +
          ".0/24")
    os.system('docker network connect ' + ISL_name + " " +
              str(container_id_list[current_orbit_id * sat_num +
                                    current_sat_id]) + " --ip 10." +
              str(address_16_23) + "." + str(address_8_15) + ".30")
    delay = matrix[current_orbit_id * sat_num +
                   current_sat_id][right_orbit_id * sat_num + right_sat_id]

    # ==== Target interface 3 ====
    print(
            "[open 3] docker exec -it " +
            str(container_id_list[current_orbit_id * sat_num +
                                  current_sat_id]) +
            " ip addr | grep -B 2 10." + str(address_16_23) + "." +
            str(address_8_15) +
            ".30 | head -n 1 | awk -F: '{ print $2 }' | tr -d '[:blank:]'")
    with os.popen(
            "docker exec -it " +
            str(container_id_list[current_orbit_id * sat_num +
                                  current_sat_id]) +
            " ip addr | grep -B 2 10." + str(address_16_23) + "." +
            str(address_8_15) +
            ".30 | head -n 1 | awk -F: '{ print $2 }' | tr -d '[:blank:]'") as f:
        ifconfig_output = f.readline()
        target_interface = str(ifconfig_output).split("@")[0]
        print(f"target_interface 3: {target_interface}")
        os.system("docker exec -d " +
                  str(container_id_list[current_orbit_id * sat_num +
                                        current_sat_id]) +
                  " ip link set dev " + target_interface + " down")
        os.system("docker exec -d " +
                  str(container_id_list[current_orbit_id * sat_num +
                                        current_sat_id]) +
                  " ip link set dev " + target_interface + " name " + "B" +
                  str(current_orbit_id * sat_num + current_sat_id + 1) +
                  "-eth" + str(right_orbit_id * sat_num + right_sat_id + 1))
        os.system("docker exec -d " +
                  str(container_id_list[current_orbit_id * sat_num +
                                        current_sat_id]) +
                  " ip link set dev B" +
                  str(current_orbit_id * sat_num + current_sat_id + 1) +
                  "-eth" + str(right_orbit_id * sat_num + right_sat_id + 1) +
                  " up")
        os.system("docker exec -d " +
                  str(container_id_list[current_orbit_id * sat_num +
                                        current_sat_id]) +
                  " tc qdisc add dev B" +
                  str(current_orbit_id * sat_num + current_sat_id + 1) +
                  "-eth" + str(right_orbit_id * sat_num + right_sat_id + 1) +
                  " root netem delay " + str(delay) + "ms loss " + str(loss) + "% rate " + str(bw) + "Gbps")
        try:
            interface3 = subprocess.run(["docker", "exec", "-it", container_id_list[current_orbit_id * sat_num +
                                            current_sat_id], "tc", "-s", "qdisc", "ls", "dev", "B"+str(current_orbit_id * sat_num + current_sat_id + 1) +
                      "-eth" + str(down_orbit_id * sat_num + down_sat_id + 1)], capture_output=True, text=True)
            print(f"interface 3: {interface3}")
        except Exception as e:
            print("Error: interface 3 ", e)
    print('[Add current node:]' + 'docker network connect ' + ISL_name + " " +
          str(container_id_list[current_orbit_id * sat_num + current_sat_id]) +
          " --ip 10." + str(address_16_23) + "." + str(address_8_15) + ".30")
    os.system('docker network connect ' + ISL_name + " " +
              str(container_id_list[right_orbit_id * sat_num + right_sat_id]) +
              " --ip 10." + str(address_16_23) + "." + str(address_8_15) +
              ".20")

    # ==== Target interface 4 ====
    print(
            "[open 4] - docker exec -it " +
            str(container_id_list[right_orbit_id * sat_num + right_sat_id]) +
            " ip addr | grep -B 2 10." + str(address_16_23) + "." +
            str(address_8_15) +
            ".20 | head -n 1 | awk -F: '{ print $2 }' | tr -d '[:blank:]'")
    with os.popen(
            "docker exec -it " +
            str(container_id_list[right_orbit_id * sat_num + right_sat_id]) +
            " ip addr | grep -B 2 10." + str(address_16_23) + "." +
            str(address_8_15) +
            ".20 | head -n 1 | awk -F: '{ print $2 }' | tr -d '[:blank:]'") as f:
        ifconfig_output = f.readline()
        target_interface = str(ifconfig_output).split("@")[0]
        print(f"target_interface 4: {target_interface}")
        os.system("docker exec -d " +
                  str(container_id_list[right_orbit_id * sat_num +
                                        right_sat_id]) + " ip link set dev " +
                  target_interface + " down")
        os.system("docker exec -d " +
                  str(container_id_list[right_orbit_id * sat_num +
                                        right_sat_id]) + " ip link set dev " +
                  target_interface + " name " + "B" +
                  str(right_orbit_id * sat_num + right_sat_id + 1) + "-eth" +
                  str(current_orbit_id * sat_num + current_sat_id + 1))
        os.system("docker exec -d " +
                  str(container_id_list[right_orbit_id * sat_num +
                                        right_sat_id]) + " ip link set dev B" +
                  str(right_orbit_id * sat_num + right_sat_id + 1) + "-eth" +
                  str(current_orbit_id * sat_num + current_sat_id + 1) + " up")
        os.system("docker exec -d " +
                  str(container_id_list[right_orbit_id * sat_num +
                                        right_sat_id]) +
                  " tc qdisc add dev B" +
                  str(right_orbit_id * sat_num + right_sat_id + 1) + "-eth" +
                  str(current_orbit_id * sat_num + current_sat_id + 1) +
                  " root netem delay " + str(delay) + "ms loss " + str(loss) + "% rate " + str(bw) + "Gbps")
        try:
            interface4 = subprocess.run(["docker", "exec", "-it", container_id_list[current_orbit_id * sat_num +
                                            current_sat_id], "tc", "-s", "qdisc", "ls", "dev", "B"+str(current_orbit_id * sat_num + current_sat_id + 1) +
                      "-eth" + str(down_orbit_id * sat_num + down_sat_id + 1)], capture_output=True, text=True)
            print(f"interface 4: {interface4}")
        except Exception as e:
            print("Error: interface 4 ", e)
    print('[Add right node:]' + 'docker network connect ' + ISL_name + " " +
          str(container_id_list[right_orbit_id * sat_num + right_sat_id]) +
          " --ip 10." + str(address_16_23) + "." + str(address_8_15) + ".20")

    print("Add 10." + str(address_16_23) + "." + str(address_8_15) +
          ".30/24 and 10." + str(address_16_23) + "." + str(address_8_15) +
          ".20/24 to (" + str(current_sat_id) + "," + str(current_orbit_id) +
          ") to (" + str(right_sat_id) + "," + str(right_orbit_id) + ")")
    
    print(f"[func end] - sn_ISL_establish") 
    print()


def sn_establish_ISLs(container_id_list, matrix, orbit_num, sat_num,
                      constellation_size, bw, loss):
    """
    Desc: 创建ISL连接
    """
    ISL_threads = []
    for current_orbit_id in range(0, orbit_num):
        for current_sat_id in range(0, sat_num):
            ISL_thread = threading.Thread(
                target=sn_ISL_establish,
                args=(current_sat_id, current_orbit_id, container_id_list,
                      orbit_num, sat_num, constellation_size, matrix, bw,
                      loss))
            ISL_threads.append(ISL_thread)
    for ISL_thread in ISL_threads:
        ISL_thread.start()
    for ISL_thread in ISL_threads:
        ISL_thread.join()


def sn_get_param(file_):
    f = open(file_)
    ADJ = f.readlines()
    for i in range(len(ADJ)):
        ADJ[i] = ADJ[i].strip('\n')
    ADJ = [x.split(',') for x in ADJ]
    f.close()
    return ADJ


def sn_get_container_info():
    #  Read all container information in all_container_info
    with os.popen("docker ps") as f:
        all_container_info = f.readlines()
        n_container = len(all_container_info) - 1

    container_id_list = []
    for container_idx in range(1, n_container + 1):
        container_id_list.append(all_container_info[container_idx].split()[0])

    return container_id_list


def sn_establish_GSL(container_id_list, matrix, GS_num, constellation_size, bw,
                     loss):
    # starting links among satellites and ground stations
    for i in range(1, constellation_size + 1):
        for j in range(constellation_size + 1,
                       constellation_size + GS_num + 1):
            # matrix[i-1][j-1])==1 means a link between node i and node j
            if ((float(matrix[i - 1][j - 1])) <= 0.01):
                continue
            # IP address  (there is a link between i and j)
            delay = str(matrix[i - 1][j - 1])
            address_16_23 = (j - constellation_size) & 0xff
            address_8_15 = i & 0xff
            GSL_name = "GSL_" + str(i) + "-" + str(j)
            # Create internal network in docker.
            os.system('docker network create ' + GSL_name + " --subnet 9." +
                      str(address_16_23) + "." + str(address_8_15) + ".0/24")
            print('[Create GSL:]' + 'docker network create ' + GSL_name +
                  " --subnet 9." + str(address_16_23) + "." +
                  str(address_8_15) + ".0/24")
            os.system('docker network connect ' + GSL_name + " " +
                      str(container_id_list[i - 1]) + " --ip 9." +
                      str(address_16_23) + "." + str(address_8_15) + ".50")
            with os.popen(
                    "docker exec -it " + str(container_id_list[i - 1]) +
                    " ip addr | grep -B 2 9." + str(address_16_23) + "." +
                    str(address_8_15) +
                    ".50 | head -n 1 | awk -F: '{ print $2 }' | tr -d '[:blank:]'"
            ) as f:
                ifconfig_output = f.readline()
                target_interface = str(ifconfig_output).split("@")[0]
                os.system("docker exec -d " + str(container_id_list[i - 1]) +
                          " ip link set dev " + target_interface + " down")
                os.system("docker exec -d " + str(container_id_list[i - 1]) +
                          " ip link set dev " + target_interface + " name " +
                          "B" + str(i - 1 + 1) + "-eth" + str(j))
                os.system("docker exec -d " + str(container_id_list[i - 1]) +
                          " ip link set dev B" + str(i - 1 + 1) + "-eth" +
                          str(j) + " up")
                os.system("docker exec -d " + str(container_id_list[i - 1]) +
                          " tc qdisc add dev B" + str(i - 1 + 1) + "-eth" +
                          str(j) + " root netem delay " + str(delay) + "ms loss " + str(loss) + "% rate " + str(bw) + "Gbps")
            print('[Add current node:]' + 'docker network connect ' +
                  GSL_name + " " + str(container_id_list[i - 1]) + " --ip 9." +
                  str(address_16_23) + "." + str(address_8_15) + ".50")

            os.system('docker network connect ' + GSL_name + " " +
                      str(container_id_list[j - 1]) + " --ip 9." +
                      str(address_16_23) + "." + str(address_8_15) + ".60")
            with os.popen(
                    "docker exec -it " + str(container_id_list[j - 1]) +
                    " ip addr | grep -B 2 9." + str(address_16_23) + "." +
                    str(address_8_15) +
                    ".60 | head -n 1 | awk -F: '{ print $2 }' | tr -d '[:blank:]'"
            ) as f:
                ifconfig_output = f.readline()
                target_interface = str(ifconfig_output).split("@")[0]
                os.system("docker exec -d " + str(container_id_list[j - 1]) +
                          " ip link set dev " + target_interface + " down")
                os.system("docker exec -d " + str(container_id_list[j - 1]) +
                          " ip link set dev " + target_interface + " name " +
                          "B" + str(j) + "-eth" + str(i - 1 + 1))
                os.system("docker exec -d " + str(container_id_list[j - 1]) +
                          " ip link set dev B" + str(j) + "-eth" +
                          str(i - 1 + 1) + " up")
                os.system("docker exec -d " + str(container_id_list[j - 1]) +
                          " tc qdisc add dev B" + str(j) + "-eth" +
                          str(i - 1 + 1) + " root netem delay " + str(delay) +
                          "ms loss " + str(loss) + "% rate " + str(bw) +
                          "Gbps")
            print('[Add right node:]' + 'docker network connect ' + GSL_name +
                  " " + str(container_id_list[j - 1]) + " --ip 9." +
                  str(address_16_23) + "." + str(address_8_15) + ".60")
    for j in range(constellation_size + 1, constellation_size + GS_num + 1):
        GS_name = "GS_" + str(j)
        # Create default network and interface for GS.
        os.system('docker network create ' + GS_name + " --subnet 9." +
                  str(j) + "." + str(j) + ".0/24")
        print('[Create GS network:]' + 'docker network create ' + GS_name +
              " --subnet 9." + str(j) + "." + str(j) + ".10/24")
        os.system('docker network connect ' + GS_name + " " +
                  str(container_id_list[j - 1]) + " --ip 9." + str(j) + "." +
                  str(j) + ".10")
        with os.popen(
                "docker exec -it " + str(container_id_list[j - 1]) +
                " ip addr | grep -B 2 9." + str(j) + "." + str(j) +
                ".10 | head -n 1 | awk -F: '{ print $2 }' | tr -d '[:blank:]'"
        ) as f:
            ifconfig_output = f.readline()
            target_interface = str(ifconfig_output).split("@")[0]
            os.system("docker exec -d " + str(container_id_list[j - 1]) +
                      " ip link set dev " + target_interface + " down")
            os.system("docker exec -d " + str(container_id_list[j - 1]) +
                      " ip link set dev " + target_interface + " name " + "B" +
                      str(j - 1 + 1) + "-default")
            os.system("docker exec -d " + str(container_id_list[j - 1]) +
                      " ip link set dev B" + str(j - 1 + 1) + "-default" +
                      " up")
        print('[Add current node:]' + 'docker network connect ' + GS_name +
              " " + str(container_id_list[j - 1]) + " --ip 9." + str(j) + "." +
              str(j) + ".10")


def sn_copy_run_conf(container_idx, path, Path, current, total):
    os.system("docker cp " + Path + "/B" + str(current + 1) + ".conf " +
              str(container_idx) + ":/B" + str(current + 1) + ".conf")
    print("[" + str(current + 1) + "/" + str(total) + "]" +
          " docker cp bird.conf " + str(container_idx) + ":/bird.conf")

    print("[sn_copy_run_conf] container_idx ", container_idx)
    try:
        result = subprocess.run(["docker", "exec", str(container_idx), "bird", "-c", "B"+str(current+1)+".conf"], capture_output=True, text=True) # 尝试使用subprocess代替os.system
        print(f"[exec result {current+1}] ", result.stdout)
    except Exception as e:
        print("Error: start bird error ", e)

    try:
        result2 = subprocess.run(["docker", "exec", str(container_idx), "birdc", "show", "protocol"], capture_output=True, text=True) # 尝试使用subprocess代替os.system
        print(f"[exec result2 {current+1}] ", result2.stdout)
        if "OSPF" not in result2.stdout:
            print("[ERROR] - cn_copy_run_conf: there is not configuration file")
            
    except Exception as e:
        print("Error: show protocol error ", e)
              
    print("docker exec -it " + str(container_idx) + " bird -c B" +
              str(current + 1) + ".conf")
    # os.system("docker exec -it " + str(container_idx) + " bird -c /home/bird/bird.conf") # 测试
    print("[" + str(current + 1) + "/" + str(total) +
          "] Bird routing process for container: " + str(container_idx) +
          " has started. ")

def sn_copy_blockchain_conf(container_idx, path, Path, current, total):
    print("[" + str(current + 1) + "/" + str(total) + "]" +
        f" docker cp {Path} {container_idx}:/fisco")
    
    # os.system(f"docker cp {path}/B{current}key.txt {container_idx}:/relsharding-client/relsharding-client/")
    # os.system(f"docker cp {path}/B{current}key.txt {container_idx}:/relsharding-client/relsharding-client/dist")
    os.system(f"docker cp {path}/")

    os.system("docker cp " + Path + " " + str(container_idx) + ":/fisco")
    sleep(1)
    print(f"{container_idx} sn_copy_blockchain_conf", ["docker", "exec", str(container_idx), "bash", "/fisco/start_all.sh"])
    try:
        result = subprocess.run(["docker", "exec", str(container_idx), "bash", "/fisco/start_all.sh"])
        print(f"[exec result {current+1}]" , result.stdout)
    except Exception as e:
        print("Error: start blockchain error", e)
        exit(0)

def sn_copy_client_conf(container_idx, path, Path, current, total, caNum):
    print("[" + str(current + 1) + "/" + str(total) + "]" +
        f" docker cp {Path} {container_idx}:/fisco-client/console/conf")

    # 生成role文件
    relshardingPath = "/relsharding-client/relsharding-client/dist"
    roleStr = "client"
    relayer_list = []
    if (current + 1 ) % 5 == 0:
        roleStr = "relayer"
    genRoleCmd = f'docker exec -d {container_idx} bash -c "echo {roleStr} > {relshardingPath}/role.txt"'
    os.system(genRoleCmd)

    # 生成 my_relayers.txt 文件，或者生成 other_relayers.txt
    for i in range(total):
        if (i+1) % 5 == 0:
            relayer_list.append(i+1)
    if roleStr == "relayer":
        relayer_list.remove(current+1)
    if roleStr == "client":
        random.shuffle(relayer_list)
        relayerStr = ""
        for relayerNum in relayer_list:
            relayerStr += str(relayerNum) + " "
        genRelayerListCmd = f'docker exec -d {container_idx} bash -c "echo {relayerStr} > {relshardingPath}/my_relayers.txt"'
        os.system(genRelayerListCmd)
    elif roleStr == "relayer":
        relayerStr = ""
        for relayerNum in relayer_list:
            relayerStr += str(relayerNum) + " "
        genRelayerListCmd = f'docker exec -d {container_idx} bash -c "echo {relayerStr} > {relshardingPath}/other_relayers.txt"'
        os.system(genRelayerListCmd)

    # copy证书
    copySDKcrt = f"docker cp {Path}/sdk.crt {container_idx}:/fisco-client/console/conf/sdk.crt"
    copySDKkey = f"docker cp {Path}/sdk.key {container_idx}:/fisco-client/console/conf/sdk.key"
    copyCa = f"docker cp {Path}/ca.crt {container_idx}:/fisco-client/console/conf/ca.crt"
    os.system(copySDKcrt)
    os.system(copySDKkey)
    os.system(copyCa)

    # copy证书到relsharding-client中
    copySDKcrtRel = f"docker cp {Path}/sdk.crt {container_idx}:{relshardingPath}/conf/sdk.crt"
    copySDKkeyRel = f"docker cp {Path}/sdk.key {container_idx}:{relshardingPath}/conf/sdk.key"
    copyCaRel = f"docker cp {Path}/ca.crt {container_idx}:{relshardingPath}/conf/ca.crt"
    os.system(copySDKcrtRel)
    os.system(copySDKkeyRel)
    os.system(copyCaRel)

    # copy config.toml
    # genConfig = f"docker exec -d {container_idx} cp /fisco-client/console/conf/config-example.toml /fisco-client/console/conf/config.toml"
    genConfig = f"docker exec -d {container_idx} python /fisco-client/console/conf/change_toml.py {caNum} {total}"
    os.system(genConfig)

    # copy config.toml to relsharding-client
    copyConfig = f"docker exec -d {container_idx} cp /fisco-client/console/conf/config.toml /relsharding-client/relsharding-client/dist/conf/config.toml"
    os.system(copyConfig)

    relshardingPyPath = "/relsharding-py/relsharding-py"
    # Run relayClient
    if roleStr == 'client':
        runPyRelayServerCmd = f'''docker exec -d {container_idx} bash -c "cd {relshardingPyPath} && python client.py"''' 
        print(runPyRelayServerCmd)
        os.system(runPyRelayServerCmd)

    # Run relayerServer
    if roleStr == "relayer":
        # TODO: relayServer.py的运行需要加入url
        runPyRelayServerCmd = f'''docker exec -d {container_idx} bash -c "cd {relshardingPyPath} && python relayServer.py"''' 
        print(runPyRelayServerCmd)
        os.system(runPyRelayServerCmd)


def sn_copy_run_conf_to_each_container(container_id_list, sat_node_number,
                                       fac_node_number, path):
    print(
        "Copy bird configuration file to each container and run routing process."
    )
    total = len(container_id_list)
    print(f"total: {total}")
    copy_threads = []
    for current in range(0, total):
        copy_thread = threading.Thread(
            target=sn_copy_run_conf,
            args=(container_id_list[current], path, path + "/conf/bird-" +
                  str(sat_node_number) + "-" + str(fac_node_number), current,
                  total))
        copy_threads.append(copy_thread)
    for copy_thread in copy_threads:
        copy_thread.start()
    for copy_thread in copy_threads:
        copy_thread.join()
    print("Initializing routing...")
    sleep(120)
    print("Routing initialized!")

def sn_copy_run_blockchain_to_each_gs(container_id_list, fac_node_number, path, sharding_num):
    print(
        "Copy FISCO conf file to each ground station container and run blockchain node process."
    )
    
    total = len(container_id_list)
    # 生成配置文件: 具体步骤参考 https://fisco-bcos-documentation.readthedocs.io/zh_CN/latest/docs/tutorial/multihost.html
    print(f"total: {total} fac_node_number: {fac_node_number}")
    
    
    # 生成配置文件
    network_ip = "192.168.2."
    conf_files = []

    for i in range(sharding_num):
        f = open(os.path.join(path, f'ipconf{i}'), 'w')
        for gs_idx in range(0, fac_node_number):
            if gs_idx % sharding_num == i:
                print(f"generating conf{i}: {total - fac_node_number}, {gs_idx}")
                f.write(f"{network_ip}{gs_idx+total-fac_node_number} agency{i} 1\n")
        conf_files.append(f)
    
    for f in conf_files:
        f.close()

    pattern = r'output_dir=nodes'
    for i in range(sharding_num):
        replacement = f'output_dir=nodes{i}'
        with open(os.path.join(f'{path}', 'build_chain.sh'), 'r') as file:
            content = file.read()
        new_content = re.sub(pattern, replacement, content)
        with open(os.path.join(f'{path}', f'build_chain{i}.sh'), 'w') as file:
            file.write(new_content)
        print(["bash", f"{path}/build_chain{i}.sh", "-f", f"{path}/ipconf{i}", "-p", "30300,20200,8545"])
        conf_fisco = subprocess.run(["bash", f"{path}/build_chain{i}.sh", "-f", f"{path}/ipconf{i}", "-p", "30300,20200,8545"], capture_output=True, text=True)
        # mv_res = subprocess.run(["mv", "nodes", f"nodes{i}"], capture_output=True, text=True)
        print(f"Generate FISCO conf {i} {conf_fisco.stdout}")
        # print(f"{mv_res}")


    copy_threads = []
    # for current in range(total-fac_node_number, total):
    for current in range(0, total):
        print("sn_copy_blockchain_conf")
        if current >= total-fac_node_number:
            # blockchain node
            caNum = total-fac_node_number + 1
            nodei = (current - (total - fac_node_number)) % sharding_num
            copy_thread = threading.Thread(
                target=sn_copy_blockchain_conf,
                # args=(container_id_list[current], path, f"~/nodes/9.{idx}.{idx}.10", current, total) 
                args=(container_id_list[current], path, f"~/nodes{nodei}/{network_ip}{current}", current, total, caNum) 
            )
        else:
            # client (console)
            caNum = total-fac_node_number + 1
            # caPath = f"~/nodes/9.{caNum}.{caNum}.10/sdk"
            # TODO 需要修改成不同分片
            nodei = current % sharding_num
            caPath = f"~/nodes{nodei}/{network_ip}{caNum-1}/sdk"
            print(f"caPath: {caPath}")
            copy_thread = threading.Thread(
                target=sn_copy_client_conf,
                args=(container_id_list[current], path, caPath, current, total, caNum)
            )
        copy_threads.append(copy_thread)
    for copy_thread in copy_threads:
        copy_thread.start()
    for copy_thread in copy_threads:
        copy_thread.join()
    print("Initializing blockchain network")
    sleep(120)
    print("Blockchain initialized!")

    # for current in range(total-fac_node_number, total):
    #     idx = current + 1
        
    #     container_idx = container_id_list[current]
    #     result = subprocess.run(["docker", "exec", str(container_idx), "bash", "/fisco/stop_all.sh"])
    #     result2 = subprocess.run(["docker", "exec", str(container_idx), "bash", "/fisco/start_all.sh"])

    # check if every blockchain node is connected to the network
    # 在每个container中，不断的查询 tail fisco/node0/log/* | grep -i connected 
    # 直到查询到结果 info|2023-08-01 10:06:52.768452|[P2P][Service] heartBeat,connected count=0
    # 同时结果中 count != 0
    # for current in range(total-fac_node_number, total): 
    #     # container_id_list[current]
    #     flag = 0
    #     while True:
    #         with os.popen(f'docker exec {container_id_list[current]} /bin/bash -c "tail fisco/node0/log/* | grep -i connected"') as f:
    #             print(f'docker exec {container_id_list[current]} /bin/bash -c "tail fisco/node0/log/* | grep -i connected"')
    #             for line in f:
    #                 if 'count=' in line:
    #                     count = int(line.split('=')[-1])
    #                     if count <= 2:
    #                         subprocess.run(["docker", "exec", str(container_id_list[current]), "bash", "/fisco/stop_all.sh"])
    #                         subprocess.run(["docker", "exec", str(container_id_list[current]), "bash", "/fisco/start_all.sh"])
    #                         flag = 1
    #                     else:
    #                         flag = 1
    #             if flag == 1:
    #                 break

    # 上面的代码该用subprocess.Popenf'docker exec {container_id_list[current]} /bin/bash -c "tail fisco/node0/log/* | grep -i connected"'
    # for current in range(total-fac_node_number, total): 
    #     cmd = f'docker exec {container_id_list[current]} /bin/bash -c "tail -f fisco/node0/log/* | grep -i connected"'
    #     process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     poll_obj = select.poll()
    #     poll_obj.register(process.stdout, select.POLLIN)

    #     try:
    #         while True:
    #             poll_result = poll_obj.poll(0)
    #             if poll_result:
    #                 line = process.stdout.readline().decode('utf-8')
    #                 print(line.strip())  # 打印输出
    #                 if 'heartBeat,connected' in line.lower():
    #                     print("Target string found!")
    #                     process.terminate()  # 终止进程
    #                     break
    #     except KeyboardInterrupt:
    #         print("keyboard interrupt")
    #         process.terminate()

        
            

                    


def sn_damage_link(sat_index, container_id_list):

    with os.popen(
            "docker exec -it " + str(container_id_list[sat_index]) +
            " ifconfig | sed 's/[ \t].*//;/^\(eth0\|\)\(lo\|\)$/d'") as f:
        ifconfig_output = f.readlines()
        for intreface in range(0, len(ifconfig_output), 2):
            os.system("docker exec -d " + str(container_id_list[sat_index]) +
                      " tc qdisc change dev " +
                      ifconfig_output[intreface][:-1] +
                      " root netem loss 100%")
            print("docker exec -d " + str(container_id_list[sat_index]) +
                  " tc qdisc change dev " + ifconfig_output[intreface][:-1] +
                  " root netem loss 100%")


def sn_damage(random_list, container_id_list):
    damage_threads = []
    for random_satellite in random_list:
        damage_thread = threading.Thread(target=sn_damage_link,
                                         args=(int(random_satellite),
                                               container_id_list))
        damage_threads.append(damage_thread)
    for damage_thread in damage_threads:
        damage_thread.start()
    for damage_thread in damage_threads:
        damage_thread.join()


def sn_recover_link(
    damaged_satellite,
    container_id_list,
    sat_loss,
):
# TODO: tc的设置是否修改了delay和rate
    with os.popen(
            "docker exec -it " + str(container_id_list[damaged_satellite]) +
            " ifconfig | sed 's/[ \t].*//;/^\(eth0\|\)\(lo\|\)$/d'") as f:
        ifconfig_output = f.readlines()
        for i in range(0, len(ifconfig_output), 2):
            os.system("docker exec -d " +
                      str(container_id_list[damaged_satellite]) +
                      " tc qdisc change dev " + ifconfig_output[i][:-1] +
                      " root netem loss " + str(sat_loss) + "%")
            print("docker exec -d " +
                  str(container_id_list[damaged_satellite]) +
                  " tc qdisc change dev " + ifconfig_output[i][:-1] +
                  " root netem loss " + str(sat_loss) + "%")


def sn_del_network(network_name):
    os.system('docker network rm ' + network_name)


def sn_stop_emulation():
    os.system("docker service rm constellation-test")
    with os.popen("docker rm -f $(docker ps -a -q)") as f:
        f.readlines()
    with os.popen("docker network ls") as f:
        all_br_info = f.readlines()
        del_threads = []
        for line in all_br_info:
            if "La" in line or "Le" or "GS" in line:
                network_name = line.split()[1]
                del_thread = threading.Thread(target=sn_del_network,
                                              args=(network_name, ))
                del_threads.append(del_thread)
        for del_thread in del_threads:
            del_thread.start()
        for del_thread in del_threads:
            del_thread.join()


def sn_recover(damage_list, container_id_list, sat_loss):
    recover_threads = []
    for damaged_satellite in damage_list:
        recover_thread = threading.Thread(target=sn_recover_link,
                                          args=(int(damaged_satellite),
                                                container_id_list, sat_loss))
        recover_threads.append(recover_thread)
    for recover_thread in recover_threads:
        recover_thread.start()
    for recover_thread in recover_threads:
        recover_thread.join()


def sn_update_delay(matrix, container_id_list,
                    constellation_size):  # updating delays
    delay_threads = []
    print(f'[func begin] - sn_update_delay')
    for row in range(len(matrix)):
        for col in range(row, len(matrix[row])):
            print(f"row: {row}, col: {col}")
            if float(matrix[row][col]) > 0:
                if row < col:
                    delay_thread = threading.Thread(
                        target=sn_delay_change,
                        args=(row, col, matrix[row][col], container_id_list,
                              constellation_size))
                    delay_threads.append(delay_thread)
                else:
                    delay_thread = threading.Thread(
                        target=sn_delay_change,
                        args=(col, row, matrix[col][row], container_id_list,
                              constellation_size))
                    delay_threads.append(delay_thread)
    for delay_thread in delay_threads:
        delay_thread.start()
    for delay_thread in delay_threads:
        delay_thread.join()
    print("Delay updating done.\n")


def sn_delay_change(link_x, link_y, delay, container_id_list,
                    constellation_size):  # multi-thread updating delays
    try:
        interface1 = subprocess.run(["docker", "exec", "-it", str(container_id_list[link_x]), 
                                     "tc", "-s", "qdisc", "ls", "dev", 
                                     "B"+str(link_x + 1) +
                  "-eth" + str(link_y + 1)], capture_output=True, text=True)
        print(f"[before] delay interface 1: {interface1}")
    except Exception as e:
        print("Error: interface 1 ", e)
    import re

    # Extract loss and rate using regular expressions
    loss = re.search(r'loss (\d+)%', interface1.stdout)
    rate = re.search(r'rate (\d+)Gbit', interface1.stdout)

    if loss:
        loss = loss.group(1)
    if rate:
        rate = rate.group(1)

    if link_y <= constellation_size:
        os.system("docker exec -d " + str(container_id_list[link_x]) +
                  " tc qdisc change dev B" + str(link_x + 1) + "-eth" +
                  str(link_y + 1) + " root netem delay " + str(delay) + "ms loss" + str(loss) + "% rate " + str(rate) + "Gbps")
        os.system("docker exec -d " + str(container_id_list[link_y]) +
                  " tc qdisc change dev B" + str(link_y + 1) + "-eth" +
                  str(link_x + 1) + " root netem delay " + str(delay) + "ms loss" + str(loss) + "% rate " + str(rate) + "Gbps")
    else:
        os.system("docker exec -d " + str(container_id_list[link_x]) +
                  " tc qdisc change dev B" + str(link_x + 1) + "-eth" +
                  str(link_y + 1) + " root netem delay " + str(delay) + "ms loss" + str(loss) + "% rate " + str(rate) + "Gbps")
        os.system("docker exec -d " + str(container_id_list[link_y]) +
                  " tc qdisc change dev B" + str(link_y + 1) + "-eth" +
                  str(link_x + 1) + " root netem delay " + str(delay) + "ms loss" + str(loss) + "% rate " + str(rate) + "Gbps")
    try:
        interface1 = subprocess.run(["docker", "exec", "-it", str(container_id_list[link_x]), 
                                     "tc", "-s", "qdisc", "ls", "dev", 
                                     "B"+str(link_x + 1) +
                  "-eth" + str(link_y + 1)], capture_output=True, text=True)
        print(f"[after] delay interface 1: {interface1}")
    except Exception as e:
        print("Error: interface 1 ", e)

def sn_copy_contract_address(container_idx, contract_address):
    """
    将contract address发给每个clients
    """
    print(f"register_contract_address {container_idx}, {contract_address}")
    write_cmd = f'docker exec {container_idx} bash -c "echo {contract_address} > /fisco-client/console/conf/contract_address.txt"'
    os.system(write_cmd)
    
def sn_deploy_contract(container_id_list, sat_number) -> str:
    """
    Desc: 部署一个名为SimpleBank的合约，返回值为合约的地址
    """
    print(f"[func begin] - sn_deploy_contract {container_id_list}, {sat_number}")

    container_idx = container_id_list[0]

    # deployContractCmd = f"docker exec {container_idx} bash fisco-client/console/console.sh deploy SimpleBank"
    deployContractCmd = ['docker', 'exec', str(container_idx), 'bash', 'fisco-client/console/console.sh', 'deploy', 'SimpleBank']
    # res = sn_remote_cmd(sn.remote_ssh, deployContractCmd)
    # res = os.system(deployContractCmd)
    res = subprocess.run(deployContractCmd, capture_output=True, text=True)

    print(f"deploy contract: {res.stdout}")

    print(res.stdout.split()[5])
    try:
        # contract_address = res.stdout[1].split(':')[1].strip()
        contract_address = res.stdout.split()[5]
    except Exception as e:
        print(f"ERROR of contract_address {e}")
    
    copy_threads = []
    for current in range(0, sat_number):
        # print(f"start threads {current}")
        # sn_copy_contract_address(container_id_list[current], contract_address)
        copy_thread = threading.Thread(
            target=sn_copy_contract_address,
            args=(container_id_list[current], contract_address)
        )
        copy_threads.append(copy_thread)
    for copy_thread in copy_threads:
        copy_thread.start()
    for copy_thread in copy_threads:
        copy_thread.join()

    
    return contract_address

if __name__ == '__main__':
    print(f"==== Start sn_orchestrater ==== {len(sys.argv)}.")
    print(f"args: {sys.argv}")
    if len(sys.argv) == 10:
        orbit_num = int(sys.argv[1])
        sat_num = int(sys.argv[2])
        constellation_size = int(sys.argv[3])
        GS_num = int(sys.argv[4])
        sat_bandwidth = float(sys.argv[5])
        sat_loss = float(sys.argv[6])
        sat_ground_bandwidth = float(sys.argv[7])
        sat_ground_loss = float(sys.argv[8])
        current_topo_path = sys.argv[9]
        matrix = sn_get_param(current_topo_path)
        container_id_list = sn_get_container_info()
        sn_establish_ISLs(container_id_list, matrix, orbit_num, sat_num,
                          constellation_size, sat_bandwidth, sat_loss)
        sn_establish_GSL(container_id_list, matrix, GS_num, constellation_size,
                         sat_ground_bandwidth, sat_ground_loss)
    elif len(sys.argv) == 4:
        if sys.argv[3] == "update":
            current_delay_path = sys.argv[1]
            constellation_size = int(sys.argv[2])
            matrix = sn_get_param(current_delay_path)
            container_id_list = sn_get_container_info()
            sn_update_delay(matrix, container_id_list, constellation_size)
        else:
            # function: routing_init
            constellation_size = int(sys.argv[1])
            GS_num = int(sys.argv[2])
            path = sys.argv[3]
            container_id_list = sn_get_container_info()
            sn_copy_run_conf_to_each_container(container_id_list,
                                               constellation_size, GS_num,
                                               path)

    elif len(sys.argv) == 6:
        if sys.argv[5] == "blockchain":
            # Init blockchain network (sn_Blockchain_Init_Thread in sn_utils.py)
            constellation_size = int(sys.argv[1])
            GS_num = int(sys.argv[2])
            path = sys.argv[3]
            sharding_num = int(sys.argv[4])
            container_id_list = sn_get_container_info()
            sn_copy_run_blockchain_to_each_gs(container_id_list, GS_num, path, sharding_num)
            sn_deploy_contract(container_id_list, len(container_id_list)-GS_num)

    elif len(sys.argv) == 2:
        path = sys.argv[1]
        random_list = numpy.loadtxt(path + "/damage_list.txt")
        container_id_list = sn_get_container_info()
        sn_damage(random_list, container_id_list)
    elif len(sys.argv) == 3:
        path = sys.argv[1]
        sat_loss = float(sys.argv[2])
        damage_list = numpy.loadtxt(path + "/damage_list.txt")
        container_id_list = sn_get_container_info()
        sn_recover(damage_list, container_id_list, sat_loss)
    elif len(sys.argv) == 1:
        sn_stop_emulation()
