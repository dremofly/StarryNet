import os
import threading
import json
import copy
import argparse
import os
from time import sleep
import time
import numpy
import random
import re
import subprocess
"""
Starrynet utils that are used in sn_synchronizer
author: Yangtao Deng (dengyt21@mails.tsinghua.edu.cn) and Zeqi Lai (zeqilai@tsinghua.edu.cn)
"""
PYTHON_PATH="/home/hong/anaconda3/bin/python"
try:
    import threading
except ImportError:
    os.system("pip3 install threading")
    import threading

try:
    import paramiko
except ImportError:
    os.system("pip3 install paramiko")
    import paramiko

try:
    import requests
except ImportError:
    os.system("pip3 install requests")
    import requests


def get_right_satellite(current_sat_id, current_orbit_id, orbit_num):
    if current_orbit_id == orbit_num - 1:
        return [current_sat_id, 0]
    else:
        return [current_sat_id, current_orbit_id + 1]


def get_down_satellite(current_sat_id, current_orbit_id, sat_num):
    if current_sat_id == sat_num - 1:
        return [0, current_orbit_id]
    else:
        return [current_sat_id + 1, current_orbit_id]

def run_orchestrater():
    """
    desc: run orchestrater module
    """

def sn_load_file(path, GS_lat_long):
    f = open(path, "r", encoding='utf8')
    table = json.load(f)
    data = {}
    data['cons_name'] = table["Name"]
    data['altitude'] = table["Altitude (km)"]
    data['cycle'] = table["Cycle (s)"]
    data['inclination'] = table["Inclination"]
    data['phase_shift'] = table["Phase shift"]
    data['orbit'] = table["# of orbit"]
    data['sat'] = table["# of satellites"]
    data['link'] = table["Satellite link"]
    data['duration'] = table["Duration (s)"]
    data['ip'] = table["IP version"]
    data['intra_as_routing'] = table["Intra-AS routing"]
    data['inter_as_routing'] = table["Inter-AS routing"]
    data['link_policy'] = table["Link policy"]
    data['handover_policy'] = table["Handover policy"]
    data['update_time'] = table["update_time (s)"]
    data['sat_bw'] = table["satellite link bandwidth (\"X\" Gbps)"]
    data['sat_ground_bw'] = table["sat-ground bandwidth (\"X\" Gbps)"]
    data['sat_loss'] = table["satellite link loss (\"X\"% )"]
    data['sat_ground_loss'] = table["sat-ground loss (\"X\"% )"]
    data['ground_num'] = table["GS number"]
    data['multi_machine'] = table[
        "multi-machine (\"0\" for no, \"1\" for yes)"]
    data['antenna_number'] = table["antenna number"]
    data['antenna_inclination'] = table["antenna_inclination_angle"]
    data['remote_machine_IP'] = table["remote_machine_IP"]
    data['remote_machine_username'] = table["remote_machine_username"]
    data['remote_machine_password'] = table["remote_machine_password"]
    data['remote_machine_port'] = table["remote_machine_port"]
    print(f"sn load files, path: {path};\n config: {data}")

    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('--cons_name', type=str, default=data['cons_name'])
    parser.add_argument('--satellite_altitude',
                        type=int,
                        default=data['altitude'])
    parser.add_argument('--inclination', type=int, default=data['inclination'])
    parser.add_argument('--orbit_number', type=int, default=data['orbit'])
    parser.add_argument('--sat_number', type=int, default=data['sat'])
    parser.add_argument('--fac_num', type=int, default=len(GS_lat_long))
    parser.add_argument('--link_style', type=str, default=data['link'])
    parser.add_argument('--IP_version', type=str, default=data['ip'])
    parser.add_argument('--link_policy', type=str, default=data['link_policy'])
    # link delay updating granularity
    parser.add_argument('--update_interval',
                        type=int,
                        default=data['update_time'])
    parser.add_argument('--duration', type=int, default=data['duration'])
    parser.add_argument('--inter_routing',
                        type=str,
                        default=data['inter_as_routing'])
    parser.add_argument('--intra_routing',
                        type=str,
                        default=data['intra_as_routing'])
    parser.add_argument('--cycle', type=int, default=data['cycle'])
    parser.add_argument('--time_slot', type=int, default=100)
    parser.add_argument('--sat_bandwidth', type=int, default=data['sat_bw'])
    parser.add_argument('--sat_ground_bandwidth',
                        type=int,
                        default=data['sat_ground_bw'])
    parser.add_argument('--sat_loss', type=int, default=data['sat_loss'])
    parser.add_argument('--sat_ground_loss',
                        type=int,
                        default=data['sat_ground_loss'])
    parser.add_argument('--ground_num', type=int, default=data['ground_num'])
    parser.add_argument('--multi_machine',
                        type=int,
                        default=data['multi_machine'])
    parser.add_argument('--antenna_number',
                        type=int,
                        default=data['antenna_number'])
    parser.add_argument('--antenna_inclination',
                        type=int,
                        default=data['antenna_inclination'])
    parser.add_argument('--user_num', type=int, default=0)
    parser.add_argument('--remote_machine_IP',
                        type=str,
                        default=data['remote_machine_IP'])
    parser.add_argument('--remote_machine_username',
                        type=str,
                        default=data['remote_machine_username'])
    parser.add_argument('--remote_machine_password',
                        type=str,
                        default=data['remote_machine_password'])
    parser.add_argument('--remote_machine_port',
                        type=int,
                        default=data['remote_machine_port'])

    parser.add_argument('--path',
                        '-p',
                        type=str,
                        default="starrynet/config.xls")
    parser.add_argument('--hello_interval', '-i', type=int, default=10)
    parser.add_argument('--node_number', '-n', type=int, default=27)
    parser.add_argument('--GS',
                        '-g',
                        type=str,
                        default="50.110924/8.682127/46.635700/14.311817")

    sn_args = parser.parse_args()
    return sn_args


def sn_get_param(file_):
    f = open(file_)
    ADJ = f.readlines()
    for i in range(len(ADJ)):
        ADJ[i] = ADJ[i].strip('\n')
    ADJ = [x.split(',') for x in ADJ]
    f.close()
    return ADJ


def sn_init_remote_machine(host, username, password, port=22):
    # transport = paramiko.Transport((host, 22))
    # transport.connect(username=username, password=password)
    remote_machine_ssh = paramiko.SSHClient()
    # remote_machine_ssh._transport = transport
    remote_machine_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        remote_machine_ssh.connect(hostname=host,
                                   port=port, # 手动修改了port
                                   username=username,
                                   password=password)
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
    except:
        myprivatekey = paramiko.RSAKey(filename=".prv")
        remote_machine_ssh.connect(hostname=host,
                                   port=port,
                                   username=username,
                                   pkey=myprivatekey)
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, pkey=myprivatekey)
    return remote_machine_ssh, transport
    # transport.close()


def sn_init_remote_ftp(transport):
    ftp_client = paramiko.SFTPClient.from_transport(transport)  ## ftp client
    return ftp_client


def sn_remote_cmd(remote_ssh, cmd):
    stdin, stdout, stderr = remote_ssh.exec_command(cmd, get_pty=True)
    lines = stdout.readlines()
    return lines


# A thread designed for initializing working directory.
class sn_init_directory_thread(threading.Thread):

    def __init__(self, file_path, configuration_file_path, remote_ssh):
        threading.Thread.__init__(self)
        self.file_path = file_path
        self.remote_ssh = remote_ssh
        self.configuration_file_path = configuration_file_path

    def run(self):
        # Reset docker environment.
        os.system("rm " + self.configuration_file_path + "/" + self.file_path +
                  "/*.txt")
        if os.path.exists(self.file_path + "/mid_files") == False:
            os.system("mkdir " + self.configuration_file_path + "/" +
                      self.file_path)
            os.system("mkdir " + self.configuration_file_path + "/" +
                      self.file_path + "/delay")
            os.system("mkdir " + self.configuration_file_path + "/" +
                      self.file_path + "/mid_files")
        sn_remote_cmd(self.remote_ssh, "mkdir ~/" + self.file_path)
        sn_remote_cmd(self.remote_ssh, "mkdir ~/" + self.file_path + "/delay")


# A thread designed for initializing constellation nodes.
class sn_Node_Init_Thread(threading.Thread):

    def __init__(self, remote_ssh, docker_service_name, node_size,
                 container_id_list, container_global_idx):
        threading.Thread.__init__(self)
        self.remote_ssh = remote_ssh
        self.docker_service_name = docker_service_name
        self.node_size = node_size
        self.container_global_idx = container_global_idx
        self.container_id_list = copy.deepcopy(container_id_list)

    def run(self):

        # Reset docker environment.
        sn_reset_docker_env(self.remote_ssh, self.docker_service_name,
                            self.node_size)
        # Get container list in each machine.
        self.container_id_list = sn_get_container_info(self.remote_ssh)
        # Rename all containers with the global idx
        sn_rename_all_container(self.remote_ssh, self.container_id_list,
                                self.container_global_idx)


def sn_get_container_info(remote_machine_ssh):
    #  Read all container information in all_container_info
    all_container_info = sn_remote_cmd(remote_machine_ssh, "docker ps")
    n_container = len(all_container_info) - 1
    container_id_list = []
    for container_idx in range(1, n_container + 1):
        container_id_list.append(all_container_info[container_idx].split()[0])

    return container_id_list


def sn_delete_remote_network_bridge(remote_ssh):
    all_br_info = sn_remote_cmd(remote_ssh, "docker network ls")
    for line in all_br_info:
        if "La" in line or "Le" in line or "GS" in line:
            network_name = line.split()[1]
            print('docker network rm ' + network_name)
            sn_remote_cmd(remote_ssh, 'docker network rm ' + network_name)


def sn_reset_docker_env(remote_ssh, docker_service_name, node_size):
    print("Reset docker environment for constellation emulation ...")
    print("Remove legacy containers.")
    print(sn_remote_cmd(remote_ssh,
                        "docker service rm " + docker_service_name))
    print(sn_remote_cmd(remote_ssh, "docker rm -f $(docker ps -a -q)"))
    print("Remove legacy emulated ISLs.")
    sn_delete_remote_network_bridge(remote_ssh)
    print("Creating new containers...")
    sn_remote_cmd(
        remote_ssh, "docker service create --replicas " + str(node_size) +
        " --name " + str(docker_service_name) +
        # " --cap-add ALL lwsen/starlab_node:1.0 ping www.baidu.com")
        " --cap-add ALL mynode ping www.baidu.com")
        # " --cap-add ALL mynode --args \"bird -c /home/bird/bird.conf\"") # 默认运行动态路由协议



def sn_rename_all_container(remote_ssh, container_id_list, new_idx):
    print("Rename all containers ...")
    new_idx = 1
    for container_id in container_id_list:
        sn_remote_cmd(
            remote_ssh, "docker rename " + str(container_id) +
            " ovs_container_" + str(new_idx))
        new_idx = new_idx + 1


# A thread designed for initializing constellation links.
class sn_Link_Init_Thread(threading.Thread):

    def __init__(self, remote_ssh, remote_ftp, orbit_num, sat_num,
                 constellation_size, fac_num, file_path,
                 configuration_file_path, sat_bandwidth, sat_ground_bandwidth,
                 sat_loss, sat_ground_loss):
        threading.Thread.__init__(self)
        self.remote_ssh = remote_ssh
        self.constellation_size = constellation_size
        self.fac_num = fac_num
        self.orbit_num = orbit_num
        self.sat_num = sat_num
        self.file_path = file_path
        self.configuration_file_path = configuration_file_path
        self.sat_bandwidth = sat_bandwidth
        self.sat_ground_bandwidth = sat_ground_bandwidth
        self.sat_loss = sat_loss
        self.sat_ground_loss = sat_ground_loss
        self.remote_ftp = remote_ftp

    def run(self):
        print('Run in link init thread.')
        self.remote_ftp.put(
            os.path.join(os.getcwd(), "starrynet/sn_orchestrater.py"),
            self.file_path + "/sn_orchestrater.py")
        
        self.remote_ftp.put(
            self.configuration_file_path + "/" + self.file_path +
            '/delay/1.txt', self.file_path + "/1.txt")
        print('Initializing links ...')
        sn_remote_cmd(
            self.remote_ssh, PYTHON_PATH + " " + self.file_path +
            "/sn_orchestrater.py" + " " + str(self.orbit_num) + " " +
            str(self.sat_num) + " " + str(self.constellation_size) + " " +
            str(self.fac_num) + " " + str(self.sat_bandwidth) + " " +
            str(self.sat_loss) + " " + str(self.sat_ground_bandwidth) + " " +
            str(self.sat_ground_loss) + " " + self.file_path + "/1.txt" + " > " + self.file_path + "/init_routing.log")


# A thread designed for initializing bird routing.
class sn_Routing_Init_Thread(threading.Thread):

    def __init__(self, remote_ssh, remote_ftp, orbit_num, sat_num,
                 constellation_size, fac_num, file_path, sat_bandwidth,
                 sat_ground_bandwidth, sat_loss, sat_ground_loss):
        threading.Thread.__init__(self)
        self.remote_ssh = remote_ssh
        self.constellation_size = constellation_size
        self.fac_num = fac_num
        self.orbit_num = orbit_num
        self.sat_num = sat_num
        self.file_path = file_path
        self.sat_bandwidth = sat_bandwidth
        self.sat_ground_bandwidth = sat_ground_bandwidth
        self.sat_loss = sat_loss
        self.sat_ground_loss = sat_ground_loss
        self.remote_ftp = remote_ftp

    def run(self):
        print(
            f"[sn_utils] - Copy bird configuration file to each container and run routing process. pwd: {os.getcwd()}, file_path: {self.file_path}"
        )
        self.remote_ftp.put(
            os.path.join(os.getcwd(), "starrynet/sn_orchestrater.py"),
            self.file_path + "/sn_orchestrater.py")
        print('Initializing routing ...')
        pwd = sn_remote_cmd(self.remote_ssh, "pwd")
        print(f"remote pwd: {pwd}")
        print(f"[sn_Routing_Init_Thread] {PYTHON_PATH} {self.file_path}/sn_orchestrater.py {str(self.constellation_size)} {str(self.fac_num)} {self.file_path} > observe_routing.log")
        try:
            sn_remote_cmd(
                self.remote_ssh, PYTHON_PATH + " " + self.file_path +
                "/sn_orchestrater.py" + " " + str(self.constellation_size) + " " +
                str(self.fac_num) + " " + self.file_path + " > " + self.file_path + "/observe_routing.log")
            print("Routing initialized!")
        except Exception as e:
            print("[ERROR] - ", e)
            sn_remote_cmd(
                self.remote_ssh, PYTHON_PATH + " " + self.file_path +
                "/sn_orchestrater.py" + " " + str(self.constellation_size) + " " +
                str(self.fac_num) + " " + self.file_path + " > " + self.file_path + "/observe_routing.log")

# A thread used to init blockchain network
class sn_Blockchain_Init_Thread(threading.Thread):
    def __init__(self, remote_ssh, remote_ftp, orbit_num, sat_num,
                 constellation_size, fac_num, file_path, sat_bandwidth,
                 sat_ground_bandwidth, sat_loss, sat_ground_loss):
        threading.Thread.__init__(self)
        self.remote_ssh = remote_ssh
        self.constellation_size = constellation_size
        self.fac_num = fac_num
        self.orbit_num = orbit_num
        self.sat_num = sat_num
        self.file_path = file_path
        self.sat_bandwidth = sat_bandwidth
        self.sat_ground_bandwidth = sat_ground_bandwidth
        self.sat_loss = sat_loss
        self.sat_ground_loss = sat_ground_loss
        self.remote_ftp = remote_ftp
    def run(self):
        print(f"Thread sn_Blockchain_Init")
        self.remote_ftp.put(
            os.path.join(os.getcwd(), "starrynet/sn_orchestrater.py"),
            self.file_path + "/sn_orchestrater.py")

        self.remote_ftp.put(
            os.path.join(os.getcwd(), "build_chain.sh"),
            self.file_path + "/build_chain.sh")

        print(
            PYTHON_PATH + " " + self.file_path +
            "/sn_orchestrater.py" + " " + str(self.constellation_size) + " " +
            str(self.fac_num) + " " + self.file_path + " " + "blockchain" " > " + self.file_path + "/observe_blockchain.log")
        print('Initialize Blockchain network')
        try:
            sn_remote_cmd(
                self.remote_ssh, PYTHON_PATH + " " + self.file_path +
                "/sn_orchestrater.py" + " " + str(self.constellation_size) + " " +
                str(self.fac_num) + " " + self.file_path + " " + "blockchain" " > " + self.file_path + "/observe_blockchain.log")
            print("Blockchain initialized!")
        except Exception as e:
            print("[ERROR] - ", e)
            sn_remote_cmd(
                self.remote_ssh, PYTHON_PATH + " " + self.file_path +
                "/sn_orchestrater.py" + " " +
                str(self.fac_num) + " " + self.file_path + " " + "blockchain" " > " + self.file_path + "/observe_blockchain.log")
        

# A thread designed for emulation.
class sn_Emulation_Start_Thread(threading.Thread):

    def __init__(self, remote_ssh, remote_ftp, sat_loss, sat_ground_bw,
                 sat_ground_loss, container_id_list, file_path,
                 configuration_file_path, update_interval, constellation_size,
                 ping_src, ping_des, ping_time, sr_src, sr_des, sr_target,
                 sr_time, damage_ratio, damage_time, damage_list,
                 recovery_time, route_src, route_time, duration,
                 utility_checking_time, perf_src, perf_des, perf_time, perf2_src, perf2_des, perf2_time, 
                 quic_src, quic_des, quic_time, led_src, led_des, led_time, deposit_src, deposit_des, deposit_time):
        threading.Thread.__init__(self)
        self.remote_ssh = remote_ssh
        self.remote_ftp = remote_ftp
        self.sat_loss = sat_loss
        self.sat_ground_bw = sat_ground_bw
        self.sat_ground_loss = sat_ground_loss
        self.container_id_list = copy.deepcopy(container_id_list)
        self.file_path = file_path
        self.configuration_file_path = configuration_file_path
        self.update_interval = update_interval
        self.constellation_size = constellation_size
        self.ping_src = ping_src
        self.ping_des = ping_des
        self.ping_time = ping_time
        self.perf_src = perf_src
        self.perf_des = perf_des
        self.perf_time = perf_time
        self.perf2_src = perf2_src
        self.perf2_des = perf2_des
        self.perf2_time = perf2_time
        self.quic_src = quic_src
        self.quic_des = quic_des
        self.quic_time = quic_time
        self.led_src = led_src
        self.led_des = led_des
        self.led_time = led_time
        self.sr_src = sr_src
        self.sr_des = sr_des
        self.sr_target = sr_target
        self.sr_time = sr_time
        self.deposit_src = deposit_src
        self.deposit_des = deposit_des
        self.deposit_time = deposit_time
        self.damage_ratio = damage_ratio
        self.damage_time = damage_time
        self.damage_list = damage_list
        self.recovery_time = recovery_time
        self.route_src = route_src
        self.route_time = route_time
        self.duration = duration
        self.utility_checking_time = utility_checking_time
        if self.container_id_list == []:
            self.container_id_list = sn_get_container_info(self.remote_ssh)

    def run(self):
        print(f"[func begin] - sn_Emulation_Start_Thread")
        ping_threads = []
        perf_threads = []
        perf2_threads = []
        quic_threads = []
        led_threads = []
        deposit_threads = []
        timeptr = 2  # current emulating time
        topo_change_file_path = self.configuration_file_path + "/" + self.file_path + '/Topo_leo_change.txt'
        fi = open(topo_change_file_path, 'r')
        line = fi.readline()
        while line:  # starting reading change information and emulating
            print(f"line: {line}")
            words = line.split()
            if words[0] == 'time':
                print('Emulation in No.' + str(timeptr) + ' second.')
                # the time when the new change occurrs
                current_time = str(int(words[1][:-1]))
                while int(current_time) > timeptr:
                    start_time = time.time()
                    if timeptr in self.utility_checking_time:
                        sn_check_utility(
                            timeptr, self.remote_ssh,
                            self.configuration_file_path + "/" +
                            self.file_path)
                    if timeptr % self.update_interval == 0:
                        # updating link delays after link changes
                        sn_update_delay(self.file_path,
                                        self.configuration_file_path, timeptr,
                                        self.constellation_size,
                                        self.remote_ssh, self.remote_ftp)
                    if timeptr in self.damage_time:
                        sn_damage(
                            self.damage_ratio[self.damage_time.index(timeptr)],
                            self.damage_list, self.constellation_size,
                            self.remote_ssh, self.remote_ftp, self.file_path,
                            self.configuration_file_path)
                    if timeptr in self.recovery_time:
                        sn_recover(self.damage_list, self.sat_loss,
                                   self.remote_ssh, self.remote_ftp,
                                   self.file_path,
                                   self.configuration_file_path)
                    if timeptr in self.sr_time:
                        index = [
                            i for i, val in enumerate(self.sr_time)
                            if val == timeptr
                        ]
                        for index_num in index:
                            sn_sr(self.sr_src[index_num],
                                  self.sr_des[index_num],
                                  self.sr_target[index_num],
                                  self.container_id_list, self.remote_ssh)
                    if timeptr in self.ping_time:
                        if timeptr in self.ping_time:
                            index = [
                                i for i, val in enumerate(self.ping_time)
                                if val == timeptr
                            ]
                            for index_num in index:
                                ping_thread = threading.Thread(
                                    target=sn_ping,
                                    args=(self.ping_src[index_num],
                                          self.ping_des[index_num],
                                          self.ping_time[index_num],
                                          self.constellation_size,
                                          self.container_id_list,
                                          self.file_path,
                                          self.configuration_file_path,
                                          self.remote_ssh))
                                ping_thread.start()
                                ping_threads.append(ping_thread)
                    if timeptr in self.perf_time:
                        if timeptr in self.perf_time:
                            index = [
                                i for i, val in enumerate(self.perf_time)
                                if val == timeptr
                            ]
                            for index_num in index:
                                perf_thread = threading.Thread(
                                    target=sn_perf,
                                    args=(self.perf_src[index_num],
                                          self.perf_des[index_num],
                                          self.perf_time[index_num],
                                          self.constellation_size,
                                          self.container_id_list,
                                          self.file_path,
                                          self.configuration_file_path,
                                          self.remote_ssh))
                                perf_thread.start()
                                perf_threads.append(perf_thread)
                    if timeptr in self.deposit_time:
                        if timeptr in self.deposit_time:
                            index = [
                                i for i, val in enumerate(self.deposit_time)
                                if val == timeptr
                            ]
                            for index_num in index:
                                deposit_thread = threading.Thread(
                                    target=sn_deposit,
                                    args=(self.deposit_src[index_num],
                                          self.deposit_des[index_num],
                                          self.deposit_time[index_num],
                                          self.container_id_list,
                                          self.file_path,
                                          self.configuration_file_path,
                                          self.remote_ssh
                                          ))
                                deposit_thread.start()
                                deposit_threads.append(deposit_thread)

                    if timeptr in self.perf2_time:
                        if timeptr in self.perf2_time:
                            index = [
                                i for i, val in enumerate(self.perf2_time)
                                if val == timeptr
                            ]
                            for index_num in index:
                                perf2_thread = threading.Thread(
                                    target=sn_perf2,
                                    args=(self.perf2_src[index_num],
                                          self.perf2_des[index_num],
                                          self.perf2_time[index_num],
                                          self.constellation_size,
                                          self.container_id_list,
                                          self.file_path,
                                          self.configuration_file_path,
                                          self.remote_ssh))
                                perf2_thread.start()
                                perf2_threads.append(perf2_thread)
                    # TODO add quic time
                    if timeptr in self.quic_time:
                        if timeptr in self.quic_time:
                            index = [
                                i for i, val in enumerate(self.quic_time)
                                if val == timeptr
                            ]
                            for index_num in index:
                                # TODO quic thread
                                quic_thread = threading.Thread(
                                target=sn_quic,
                                args=(self.quic_src[index_num],
                                      self.quic_des[index_num],
                                      self.quic_time[index_num],
                                      self.constellation_size,
                                      self.container_id_list, self.file_path,
                                      self.configuration_file_path,
                                      self.remote_ssh))
                                quic_thread.start()
                                quic_threads.append(quic_thread)
                    if timeptr in self.led_time:
                        if timeptr in self.led_time:
                            index = [
                                i for i, val in enumerate(self.led_time)
                                if val == timeptr
                            ]
                            for index_num in index:
                                # TODO quic thread
                                led_thread = threading.Thread(
                                target=sn_ledbat,
                                args=(self.led_src[index_num],
                                      self.led_des[index_num],
                                      self.led_time[index_num],
                                      self.constellation_size,
                                      self.container_id_list, self.file_path,
                                      self.configuration_file_path,
                                      self.remote_ssh))
                                led_thread.start()
                                led_threads.append(led_thread)

                    if timeptr in self.route_time:
                        index = [
                            i for i, val in enumerate(self.route_time)
                            if val == timeptr
                        ]
                        for index_num in index:
                            sn_route(self.route_src[index_num],
                                     self.route_time[index_num],
                                     self.file_path,
                                     self.configuration_file_path,
                                     self.container_id_list, self.remote_ssh)
                    timeptr += 1
                    end_time = time.time()
                    passed_time = (
                        end_time -
                        start_time) if (end_time - start_time) < 1 else 1
                    sleep(1 - passed_time)
                    if timeptr >= self.duration:
                        return
                    print('Emulation in No.' + str(timeptr) + ' second.')
                print("A change in time " + current_time + ':')
                line = fi.readline()
                print(f"line: {line}")
                words = line.split()
                line = fi.readline()
                print(f"line: {line}")
                line = fi.readline()
                print(f"line: {line}")
                words = line.split()
                while words[0] != 'del:':  # addlink
                    word = words[0].split('-')
                    s = int(word[0])
                    f = int(word[1])
                    if s > f:
                        tmp = s
                        s = f
                        f = tmp
                    print("add link", s, f)
                    current_topo_path = self.configuration_file_path + "/" + self.file_path + '/delay/' + str(
                        current_time) + '.txt'
                    matrix = sn_get_param(current_topo_path)
                    sn_establish_new_GSL(self.container_id_list, matrix,
                                         self.constellation_size,
                                         self.sat_ground_bw,
                                         self.sat_ground_loss, s, f,
                                         self.remote_ssh)
                    line = fi.readline()
                    print(f"line: {line}")
                    words = line.split()
                line = fi.readline()
                print(f"line: {line}")
                words = line.split()
                if len(words) == 0:
                    return
                while words[0] != 'time':  # delete link
                    word = words[0].split('-')
                    s = int(word[0])
                    f = int(word[1])
                    if s > f:
                        tmp = s
                        s = f
                        f = tmp
                    print("del link " + str(s) + "-" + str(f) + "\n")
                    sn_del_link(s, f, self.container_id_list, self.remote_ssh)
                    line = fi.readline()
                    print(f"line: {line}")
                    words = line.split()
                    if len(words) == 0:
                        return
                if timeptr in self.utility_checking_time:
                    sn_check_utility(
                        timeptr, self.remote_ssh,
                        self.configuration_file_path + "/" + self.file_path)
                if timeptr % self.update_interval == 0:
                    # updating link delays after link changes
                    sn_update_delay(self.file_path,
                                    self.configuration_file_path, timeptr,
                                    self.constellation_size, self.remote_ssh,
                                    self.remote_ftp)
                if timeptr in self.damage_time:
                    sn_damage(
                        self.damage_ratio[self.damage_time.index(timeptr)],
                        self.damage_list, self.constellation_size,
                        self.remote_ssh, self.remote_ftp, self.file_path,
                        self.configuration_file_path)
                if timeptr in self.recovery_time:
                    sn_recover(self.damage_list, self.sat_loss,
                               self.remote_ssh, self.remote_ftp,
                               self.file_path, self.configuration_file_path)
                if timeptr in self.sr_time:
                    index = [
                        i for i, val in enumerate(self.sr_time)
                        if val == timeptr
                    ]
                    for index_num in index:
                        sn_sr(self.sr_src[index_num], self.sr_des[index_num],
                              self.sr_target[index_num],
                              self.container_id_list, self.remote_ssh)
                if timeptr in self.ping_time:
                    if timeptr in self.ping_time:
                        index = [
                            i for i, val in enumerate(self.ping_time)
                            if val == timeptr
                        ]
                        for index_num in index:
                            ping_thread = threading.Thread(
                                target=sn_ping,
                                args=(self.ping_src[index_num],
                                      self.ping_des[index_num],
                                      self.ping_time[index_num],
                                      self.constellation_size,
                                      self.container_id_list, self.file_path,
                                      self.configuration_file_path,
                                      self.remote_ssh))
                            ping_thread.start()
                            ping_threads.append(ping_thread)
                if timeptr in self.perf_time:
                    if timeptr in self.perf_time:
                        index = [
                            i for i, val in enumerate(self.perf_time)
                            if val == timeptr
                        ]
                        for index_num in index:
                            perf_thread = threading.Thread(
                                target=sn_perf,
                                args=(self.perf_src[index_num],
                                      self.perf_des[index_num],
                                      self.perf_time[index_num],
                                      self.constellation_size,
                                      self.container_id_list, self.file_path,
                                      self.configuration_file_path,
                                      self.remote_ssh))
                            perf_thread.start()
                            perf_threads.append(perf_thread)
                if timeptr in self.perf2_time:
                    if timeptr in self.perf2_time:
                        index = [
                            i for i, val in enumerate(self.perf2_time)
                            if val == timeptr
                        ]
                        for index_num in index:
                            perf2_thread = threading.Thread(
                                target=sn_perf2,
                                args=(self.perf2_src[index_num],
                                      self.perf2_des[index_num],
                                      self.perf2_time[index_num],
                                      self.constellation_size,
                                      self.container_id_list,
                                      self.file_path,
                                      self.configuration_file_path,
                                      self.remote_ssh))
                            perf2_thread.start()
                            perf2_threads.append(perf2_thread)
                if timeptr in self.deposit_time:
                    if timeptr in self.deposit_time:
                        index = [
                            i for i, val in enumerate(self.deposit_time)
                            if val == timeptr
                        ]
                        for index_num in index:
                            deposit_thread = threading.Thread(
                                target=sn_deposit,
                                args=(self.deposit_src[index_num],
                                      self.deposit_des[index_num],
                                      self.deposit_time[index_num],
                                      self.container_id_list,
                                      self.file_path,
                                      self.configuration_file_path,
                                      self.remote_ssh
                                      ))
                            deposit_thread.start()
                            deposit_threads.append(deposit_thread)
                # TODO add quic time
                if timeptr in self.quic_time:
                    if timeptr in self.quic_time:
                        index = [
                            i for i, val in enumerate(self.quic_time)
                            if val == timeptr
                        ]
                        for index_num in index:
                            # TODO quic thread
                            quic_thread = threading.Thread(
                            target=sn_quic,
                            args=(self.quic_src[index_num],
                                  self.quic_des[index_num],
                                  self.quic_time[index_num],
                                  self.constellation_size,
                                  self.container_id_list, self.file_path,
                                  self.configuration_file_path,
                                  self.remote_ssh))
                            quic_thread.start()
                            quic_threads.append(quic_thread)
                if timeptr in self.led_time:
                    if timeptr in self.led_time:
                        index = [
                            i for i, val in enumerate(self.led_time)
                            if val == timeptr
                        ]
                        for index_num in index:
                            # TODO quic thread
                            led_thread = threading.Thread(
                            target=sn_ledbat,
                            args=(self.led_src[index_num],
                                  self.led_des[index_num],
                                  self.led_time[index_num],
                                  self.constellation_size,
                                  self.container_id_list, self.file_path,
                                  self.configuration_file_path,
                                  self.remote_ssh))
                            led_thread.start()
                            led_threads.append(led_thread)
                if timeptr in self.route_time:
                    index = [
                        i for i, val in enumerate(self.route_time)
                        if val == timeptr
                    ]
                    for index_num in index:
                        sn_route(self.route_src[index_num],
                                 self.route_time[index_num], self.file_path,
                                 self.configuration_file_path,
                                 self.container_id_list, self.remote_ssh)
                timeptr += 1  # current emulating time
                if timeptr >= self.duration:
                    return
        fi.close()
        for ping_thread in ping_threads:
            ping_thread.join()
        for perf_thread in perf_threads:
            perf_thread.join()
        for quic_thread in quic_threads:
            quic_thread.join()
        for led_thread in led_threads:
            led_thread.join()
        for deposit_thread in deposit_threads:
            deposit_thread.join()


def sn_check_utility(time_index, remote_ssh, file_path):
    result = sn_remote_cmd(remote_ssh, "vmstat")
    f = open(file_path + "/utility-info" + "_" + str(time_index) + ".txt", "w")
    f.writelines(result)
    f.close()


def sn_update_delay(file_path, configuration_file_path, timeptr,
                    constellation_size, remote_ssh,
                    remote_ftp):  # updating delays
    remote_ftp.put(os.path.join(os.getcwd(), "starrynet/sn_orchestrater.py"),
                   file_path + "/sn_orchestrater.py")
    remote_ftp.put(
        configuration_file_path + "/" + file_path + '/delay/' + str(timeptr) +
        '.txt', file_path + '/' + str(timeptr) + '.txt')
    sn_remote_cmd(
        remote_ssh,
        PYTHON_PATH + " " + file_path + "/sn_orchestrater.py " + file_path + '/' +
        str(timeptr) + '.txt ' + str(constellation_size) + " update" + " > " + file_path+'/orche'+str(timeptr)+'.log')
    print("Delay updating done.\n")


def sn_damage(ratio, damage_list, constellation_size, remote_ssh, remote_ftp,
              file_path, configuration_file_path):
    print("Randomly setting damaged links...\n")
    random_list = []
    cumulated_damage_list = damage_list
    while len(random_list) < (int(constellation_size * ratio)):
        target = int(random.uniform(0, constellation_size - 1))
        random_list.append(target)
        cumulated_damage_list.append(target)
    numpy.savetxt(
        configuration_file_path + "/" + file_path +
        '/mid_files/damage_list.txt', random_list)
    remote_ftp.put(os.path.join(os.getcwd(), "starrynet/sn_orchestrater.py"),
                   file_path + "/sn_orchestrater.py")
    remote_ftp.put(
        configuration_file_path + "/" + file_path +
        '/mid_files/damage_list.txt', file_path + "/damage_list.txt")
    sn_remote_cmd(remote_ssh,
                  PYTHON_PATH + " " + file_path + "/sn_orchestrater.py " + file_path + " > " + file_path + "/orche_damage.log")
    print("Damage done.\n")


def sn_recover(damage_list, sat_loss, remote_ssh, remote_ftp, file_path,
               configuration_file_path):
    print("Recovering damaged links...\n")
    cumulated_damage_list = damage_list
    numpy.savetxt(
        configuration_file_path + "/" + file_path +
        '/mid_files/damage_list.txt', cumulated_damage_list)
    remote_ftp.put(os.path.join(os.getcwd(), "starrynet/sn_orchestrater.py"),
                   file_path + "/sn_orchestrater.py")
    remote_ftp.put(
        configuration_file_path + "/" + file_path +
        '/mid_files/damage_list.txt', file_path + "/damage_list.txt")
    sn_remote_cmd(
        remote_ssh, PYTHON_PATH + " " + file_path + "/sn_orchestrater.py " +
        file_path + " " + str(sat_loss) + " > orche_recover_"+time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())+".log" )
    print(f"{PYTHON_PATH} {file_path}/sn_orchestrater.py {file_path} {sat_loss}")
    cumulated_damage_list.clear()
    print("Link recover done.\n")


def sn_sr(src, des, target, container_id_list, remote_ssh):
    print(f"[thread begin] - sn_sr. src: {src}, des: {des}, target: {target}")
    ifconfig_output = sn_remote_cmd(
        remote_ssh, "docker exec -it " + str(container_id_list[des - 1]) +
        " ifconfig | sed 's/[ \t].*//;/^\(eth0\|\)\(lo\|\)$/d'")
    print(f"ifconfig_output: {ifconfig_output}")

    des_IP = sn_remote_cmd(
        remote_ssh,
        "docker exec -it " + str(container_id_list[des - 1]) + " ifconfig " +
        ifconfig_output[0][:-1] + "|awk -F '[ :]+' 'NR==2{print $4}'")
    print(f"des_IP: {des_IP}")

    target_IP = sn_remote_cmd(
        remote_ssh, "docker exec -it " + str(container_id_list[target - 1]) +
        " ifconfig B" + str(target) + "-eth" + str(src) +
        "|awk -F '[ :]+' 'NR==2{print $4}'")
    print(f"target_IP: {target_IP}")
    
    sn_remote_cmd(
        remote_ssh, "docker exec -d " + str(container_id_list[src - 1]) +
        " ip route del " + str(des_IP[0][:-3]) + "0/24")
    print(
        "docker exec -d " + str(container_id_list[src - 1]) +
        " ip route del " + str(des_IP[0][:-3]) + "0/24")

    sn_remote_cmd(
        remote_ssh, "docker exec -d " + str(container_id_list[src - 1]) +
        " ip route add " + str(des_IP[0][:-3]) + "0/24 dev B%d-eth%d via " %
        (src, target) + target_IP[0])
    print(
        "docker exec -d " + str(container_id_list[src - 1]) +
        " ip route add " + str(des_IP[0][:-3]) + "0/24 dev B%d-eth%d via " %
        (src, target) + target_IP[0])
    print("docker exec -d " + str(container_id_list[src - 1]) +
          " ip route add " + str(des_IP[0][:-3]) + "0/24 dev B%d-eth%d via " %
          (src, target) + target_IP[0])


def sn_ping(src, des, time_index, constellation_size, container_id_list,
            file_path, configuration_file_path, remote_ssh):
    print(f"[sn_ping] from {src} to {des}")
    if des <= constellation_size:
        ifconfig_output = sn_remote_cmd(
            remote_ssh, "docker exec -it " + str(container_id_list[des - 1]) +
            " ifconfig | sed 's/[ \t].*//;/^\(eth0\|\)\(lo\|\)$/d'")
        des_IP = sn_remote_cmd(
            remote_ssh, "docker exec -it " + str(container_id_list[des - 1]) +
            " ifconfig " + ifconfig_output[0][:-1] +
            "|awk -F '[ :]+' 'NR==2{print $4}'")
    else:
        des_IP = sn_remote_cmd(
            remote_ssh, "docker exec -it " + str(container_id_list[des - 1]) +
            " ifconfig B" + str(des) +
            "-default |awk -F '[ :]+' 'NR==2{print $4}'")
    # print(f"[sn_ping] - desIP {des_IP}\n")
    ping_result = sn_remote_cmd(
        remote_ssh, "docker exec -i " + str(container_id_list[src - 1]) +
        " ping " + str(des_IP[0][:-1]) + " -c 1000 -i 0.01 ") # 执行4次
    f = open(
        configuration_file_path + "/" + file_path + "/ping-" + str(src) + "-" +
        str(des) + "_" + str(time_index) + ".txt", "w")
    f.writelines(ping_result)
    f.close()

def sn_deposit(src, des, time_index, container_id_list,
                file_path, configuration_file_path, remote_ssh):
    """
    调用SimpleBank合约中的deposit操作
    """
    getAccountCmd = f'docker exec -it {container_id_list[des-1]} bash fisco-client/console/get_account.sh'
    
    
    accountRes = subprocess.run(['docker', 'exec', '-it', str(container_id_list[des-1]), 'bash', 'fisco-client/console/get_account.sh'], capture_output=True, text=True)
    # accountRes = os.system(getAccountCmd)
    print(accountRes.stdout)
    print("\n")
    match = re.search(r"Account Address\s*:\s*(0x[a-fA-F0-9]+)", accountRes.stdout)
    if match:
        account = match.group(1)
        print(f"found account {account}\n")
    else:
        print("Address not found.")
        exit(0)
        # print(account) 

    # '138d8392a9b'
    cmd = f'docker exec {container_id_list[src-1]} bash call_contract.sh {account}'
    print(f"sn_deposit {src} {time_index} {cmd} account\n")
    deposit_res = sn_remote_cmd(remote_ssh, cmd)
    f = open(
        configuration_file_path + "/" + file_path + "/transfer-" + str(src) + "_" + str(time_index) + ".txt", 'w' 
    )
    f.writelines(deposit_res)
    f.close()

def sn_perf(src, des, time_index, constellation_size, container_id_list,
            file_path, configuration_file_path, remote_ssh):
    # congestion control: cubic
    if des <= constellation_size:
        ifconfig_output = sn_remote_cmd(
            remote_ssh, "docker exec -it " + str(container_id_list[des - 1]) +
            " ifconfig | sed 's/[ \t].*//;/^\(eth0\|\)\(lo\|\)$/d'")
        des_IP = sn_remote_cmd(
            remote_ssh, "docker exec -it " + str(container_id_list[des - 1]) +
            " ifconfig " + ifconfig_output[0][:-1] +
            "|awk -F '[ :]+' 'NR==2{print $4}'")
    else:
        des_IP = sn_remote_cmd(
            remote_ssh, "docker exec -it " + str(container_id_list[des - 1]) +
            " ifconfig B" + str(des) +
            "-default |awk -F '[ :]+' 'NR==2{print $4}'")

    sn_remote_cmd(
        remote_ssh,
        "docker exec -id " + str(container_id_list[des - 1]) + " iperf3 -s ")
    print(f"[{src}, {des} ] iperf server success")
    perf_result = sn_remote_cmd(
        remote_ssh, "docker exec -i " + str(container_id_list[src - 1]) +
        " iperf3 -C cubic -c " + str(des_IP[0][:-1]) + " -t 5 ")
    print(f"[{src}, {des} ] iperf client success")
    f = open(
        configuration_file_path + "/" + file_path + "/perfcubic-" + str(src) + "-" +
        str(des) + "_" + str(time_index) + ".txt", "w")
    f.writelines(perf_result)
    f.close()

def sn_perf2(src, des, time_index, constellation_size, container_id_list,
            file_path, configuration_file_path, remote_ssh):
    # congestion control: BBR
    if des <= constellation_size:
        ifconfig_output = sn_remote_cmd(
            remote_ssh, "docker exec -it " + str(container_id_list[des - 1]) +
            " ifconfig | sed 's/[ \t].*//;/^\(eth0\|\)\(lo\|\)$/d'")
        des_IP = sn_remote_cmd(
            remote_ssh, "docker exec -it " + str(container_id_list[des - 1]) +
            " ifconfig " + ifconfig_output[0][:-1] +
            "|awk -F '[ :]+' 'NR==2{print $4}'")
    else:
        des_IP = sn_remote_cmd(
            remote_ssh, "docker exec -it " + str(container_id_list[des - 1]) +
            " ifconfig B" + str(des) +
            "-default |awk -F '[ :]+' 'NR==2{print $4}'")

    sn_remote_cmd(
        remote_ssh,
        "docker exec -id " + str(container_id_list[des - 1]) + " iperf3 -s ")
    print(f"[{src}, {des} ] iperf server success")
    perf_result = sn_remote_cmd(
        remote_ssh, "docker exec -i " + str(container_id_list[src - 1]) +
        " iperf3 -C bbr -c " + str(des_IP[0][:-1]) + " -t 5 ")
    print(f"[{src}, {des} ] iperf client success")
    f = open(
        configuration_file_path + "/" + file_path + "/perfbbr-" + str(src) + "-" +
        str(des) + "_" + str(time_index) + ".txt", "w")
    f.writelines(perf_result)
    f.close()

def sn_quic(src, des, time_index, constellation_size, container_id_list,
            file_path, configuration_file_path, remote_ssh):
    if des <= constellation_size:
        ifconfig_ouput = sn_remote_cmd(
            remote_ssh, "docker exec -it " + str(container_id_list[des - 1]) + 
            " ifconfig | sed 's/[ \t].*//;/^\(eth0\|\)\(lo\|\)$/d'")
        des_IP = sn_remote_cmd(
            remote_ssh, "docker exec -it " + str(container_id_list[des - 1]) + 
                        " ifconfig " + ifconfig_ouput[0][:-1] +
            "|awk -F '[ :]+' 'NR==2{print $4}'")
    else:
        des_IP = sn_remote_cmd(
        remote_ssh, "docker exec -it " + str(container_id_list[des - 1]) +
        " ifconfig B" + str(des) +
        "-default |awk -F '[ :]+' 'NR==2{print $4}'")
    quic_path = "/home/aioquic"
    # sn_remote_cmd(
    #     remote_ssh,
    #     "docker exec -id " + str(container_id_list[des - 1]) + " python3 /aioquic/examples/http3_server.py --certificate /aioquic/tests/ssl_cert.pem --private-key /aioquic/tests/ssl_key.pem ")

    print(f"[sn_quic] src: {src} dec: {des}")

    print(f"stop server")
    res = sn_remote_cmd(remote_ssh, f"docker exec -it {container_id_list[src-1]} ps aux")
    for item in res:
        print(f"container {container_id_list[src-1]} {item}")
        if 'python' in item:
            print(f"[be stopped] {container_id_list[src-1]} {item}")
            pid = item.split()[1]
            sn_remote_cmd(remote_ssh, f"docker exec -it {container_id_list[src-1]} kill -9 {pid}")
    res = sn_remote_cmd(remote_ssh, f"docker exec -it {container_id_list[des-1]} ps aux")
    for item in res:
        print(f"container {container_id_list[des-1]} {item}")
        if 'python' in item:
            print(f"[be stopped] {container_id_list[des-1]} {item}")
            pid = item.split()[1]
            sn_remote_cmd(remote_ssh, f"docker exec -it {container_id_list[des-1]} kill -9 {pid}")

    try:
        sn_remote_cmd(
            remote_ssh,
            f"docker exec -id {container_id_list[des - 1]} python {ledbat_path}/testapp.py")
        print(f"docker exec -id {container_id_list[des - 1]} python {ledbat_path}/testapp.py")
    except Exception as e:
        print(f"{container_id_list[des - 1]} already start server")


    sn_remote_cmd(
        remote_ssh,
        f"docker exec -id {container_id_list[des - 1]} python {quic_path}/examples/http3_server.py --certificate {quic_path}/tests/ssl_cert.pem --private-key {quic_path}/tests/ssl_key.pem ")
    print(f"docker exec -id {container_id_list[des - 1]} python {quic_path}/examples/http3_server.py --certificate {quic_path}/tests/ssl_cert.pem --private-key {quic_path}/tests/ssl_key.pem ")
    # quic_result = sn_remote_cmd(
    #     remote_ssh, "docker exec -id " + str(container_id_list[src - 1]) +
    #     " python /aioquic/examples/http3_client.py --ca-certs /aioquic/tests/pycacert.pem https://" + str(des_IP[0][:-1]) + ":4433/ ")
    quic_result = sn_remote_cmd(
        remote_ssh, 
        f"docker exec -i {container_id_list[src - 1]} python {quic_path}/examples/http3_client.py --ca-certs {quic_path}/tests/pycacert.pem https://{des_IP[0][:-1]}:4433/ ")
    print(f"docker exec -i {container_id_list[src - 1]} python {quic_path}/examples/http3_client.py --ca-certs {quic_path}/tests/pycacert.pem https://{des_IP[0][:-1]}:4433/ ")
    f = open(
        configuration_file_path + "/" + file_path + "/quic-" + str(src) + "-" +
        str(des) + "_" + str(time_index) + ".txt", "w")
    f.writelines(quic_result)
    f.close()

def sn_ledbat(src, des, time_index, constellation_size, container_id_list,
            file_path, configuration_file_path, remote_ssh):
    if des <= constellation_size:
        ifconfig_ouput = sn_remote_cmd(
            remote_ssh, "docker exec -it " + str(container_id_list[des - 1]) + 
            " ifconfig | sed 's/[ \t].*//;/^\(eth0\|\)\(lo\|\)$/d'")
        des_IP = sn_remote_cmd(
            remote_ssh, "docker exec -it " + str(container_id_list[des - 1]) + 
                        " ifconfig " + ifconfig_ouput[0][:-1] +
            "|awk -F '[ :]+' 'NR==2{print $4}'")
    else:
        des_IP = sn_remote_cmd(
        remote_ssh, "docker exec -it " + str(container_id_list[des - 1]) +
        " ifconfig B" + str(des) +
        "-default |awk -F '[ :]+' 'NR==2{print $4}'")
    ledbat_path = "/home/pyledbat/pyledbat"
    # sn_remote_cmd(
    #     remote_ssh,
    #     "docker exec -id " + str(container_id_list[des - 1]) + " python3 /aioquic/examples/http3_server.py --certificate /aioquic/tests/ssl_cert.pem --private-key /aioquic/tests/ssl_key.pem ")


    print(f"[sn_led] src: {src} dec: {des}")

    print(f"stop server")
    # stop pyledbat servers
    res = sn_remote_cmd(remote_ssh, f"docker exec -it {container_id_list[src-1]} ps aux")
    for item in res:
        print(f"container {container_id_list[src-1]} {item}")
        if 'python' in item:
            print(f"[be stopped] {container_id_list[src-1]} {item}")
            pid = item.split()[1]
            sn_remote_cmd(remote_ssh, f"docker exec -it {container_id_list[src-1]} kill -9 {pid}")
    res = sn_remote_cmd(remote_ssh, f"docker exec -it {container_id_list[des-1]} ps aux")
    for item in res:
        print(f"container {container_id_list[des-1]} {item}")
        if 'python' in item:
            print(f"[be stopped] {container_id_list[des-1]} {item}")
            pid = item.split()[1]
            sn_remote_cmd(remote_ssh, f"docker exec -it {container_id_list[des-1]} kill -9 {pid}")

    try:
        sn_remote_cmd(
            remote_ssh,
            f"docker exec -id {container_id_list[des - 1]} python {ledbat_path}/testapp.py")
        print(f"docker exec -id {container_id_list[des - 1]} python {ledbat_path}/testapp.py")
    except Exception as e:
        print(f"{container_id_list[des - 1]} already start server")
    # quic_result = sn_remote_cmd(
    #     remote_ssh, "docker exec -id " + str(container_id_list[src - 1]) +
    #     " python /aioquic/examples/http3_client.py --ca-certs /aioquic/tests/pycacert.pem https://" + str(des_IP[0][:-1]) + ":4433/ ")
    ledbat_result = sn_remote_cmd(
        remote_ssh, 
        f"docker exec -i {container_id_list[src - 1]} python {ledbat_path}/testapp.py --role=client --remote={des_IP[0][:-1]} --time=1 ")
    print(f"docker exec -i {container_id_list[src - 1]} python {ledbat_path}/testapp.py --role=client --remote={des_IP[0][:-1]} --time=1 ")
    
    f = open(
        configuration_file_path + "/" + file_path + "/ledbat-" + str(src) + "-" +
        str(des) + "_" + str(time_index) + ".txt", "w")
    f.writelines(ledbat_result)
    f.close()


def sn_route(src, time_index, file_path, configuration_file_path,
             container_id_list, remote_ssh):
    route_result = sn_remote_cmd(
        remote_ssh,
        "docker exec -it " + str(container_id_list[src - 1]) + " route ")
    f = open(
        configuration_file_path + "/" + file_path + "/route-" + str(src) +
        "_" + str(time_index) + ".txt", "w")
    f.writelines(route_result)
    f.close()


def sn_establish_new_GSL(container_id_list, matrix, constellation_size, bw,
                         loss, sat_index, GS_index, remote_ssh):
    i = sat_index
    j = GS_index
    print(f"[func begin] - sn_establish_new_GSL: sat_index {i}, GS_index {j}")
    # IP address  (there is a link between i and j)
    delay = str(matrix[i - 1][j - 1])
    address_16_23 = (j - constellation_size) & 0xff
    address_8_15 = i & 0xff
    GSL_name = "GSL_" + str(i) + "-" + str(j)
    # Create internal network in docker.
    sn_remote_cmd(
        remote_ssh, 'docker network create ' + GSL_name + " --subnet 9." +
        str(address_16_23) + "." + str(address_8_15) + ".0/24")
    print('docker network create ' + GSL_name + " --subnet 9." +
        str(address_16_23) + "." + str(address_8_15) + ".0/24")
    print('[Create GSL:]' + 'docker network create ' + GSL_name +
          " --subnet 9." + str(address_16_23) + "." + str(address_8_15) +
          ".0/24")
    sn_remote_cmd(
        remote_ssh, 'docker network connect ' + GSL_name + " " +
        str(container_id_list[i - 1]) + " --ip 9." + str(address_16_23) + "." +
        str(address_8_15) + ".50")
    print(
        'docker network connect ' + GSL_name + " " +
        str(container_id_list[i - 1]) + " --ip 9." + str(address_16_23) + "." +
        str(address_8_15) + ".50")
    ifconfig_output = sn_remote_cmd(
        remote_ssh, "docker exec -it " + str(container_id_list[i - 1]) +
        " ip addr | grep -B 2 9." + str(address_16_23) + "." +
        str(address_8_15) +
        ".50 | head -n 1 | awk -F: '{ print $2 }' | tr -d '[:blank:]'")
    print(
        "docker exec -it " + str(container_id_list[i - 1]) +
        " ip addr | grep -B 2 9." + str(address_16_23) + "." +
        str(address_8_15) +
        ".50 | head -n 1 | awk -F: '{ print $2 }' | tr -d '[:blank:]'")
    print(f"ifconfig_output {ifconfig_output}")

    target_interface = str(ifconfig_output[0]).split("@")[0]
    sn_remote_cmd(
        remote_ssh, "docker exec -d " + str(container_id_list[i - 1]) +
        " ip link set dev " + target_interface + " down")
    print("docker exec -d " + str(container_id_list[i - 1]) +
        " ip link set dev " + target_interface + " down")
    sn_remote_cmd(
        remote_ssh, "docker exec -d " + str(container_id_list[i - 1]) +
        " ip link set dev " + target_interface + " name " + "B" +
        str(i - 1 + 1) + "-eth" + str(j))
    print("docker exec -d " + str(container_id_list[i - 1]) +
        " ip link set dev " + target_interface + " name " + "B" +
        str(i - 1 + 1) + "-eth" + str(j))
    sn_remote_cmd(
        remote_ssh, "docker exec -d " + str(container_id_list[i - 1]) +
        " ip link set dev B" + str(i - 1 + 1) + "-eth" + str(j) + " up")
    print("docker exec -d " + str(container_id_list[i - 1]) +
        " ip link set dev B" + str(i - 1 + 1) + "-eth" + str(j) + " up")
    sn_remote_cmd(
        remote_ssh, "docker exec -d " + str(container_id_list[i - 1]) +
        " tc qdisc add dev B" + str(i - 1 + 1) + "-eth" + str(j) +
        " root netem delay " + str(delay) + "ms")
    print("docker exec -d " + str(container_id_list[i - 1]) +
        " tc qdisc add dev B" + str(i - 1 + 1) + "-eth" + str(j) +
        " root netem delay " + str(delay) + "ms")
    sn_remote_cmd(
        remote_ssh, "docker exec -d " + str(container_id_list[i - 1]) +
        " tc qdisc add dev B" + str(i - 1 + 1) + "-eth" + str(j) +
        " root netem loss " + str(loss) + "%")
    print(
        "docker exec -d " + str(container_id_list[i - 1]) +
        " tc qdisc add dev B" + str(i - 1 + 1) + "-eth" + str(j) +
        " root netem loss " + str(loss) + "%")
    sn_remote_cmd(
        remote_ssh, "docker exec -d " + str(container_id_list[i - 1]) +
        " tc qdisc add dev B" + str(i - 1 + 1) + "-eth" + str(j) +
        " root netem rate " + str(bw) + "Gbps")
    print(
        "docker exec -d " + str(container_id_list[i - 1]) +
        " tc qdisc add dev B" + str(i - 1 + 1) + "-eth" + str(j) +
        " root netem rate " + str(bw) + "Gbps")
    print('[Add current node:]' + 'docker network connect ' + GSL_name + " " +
          str(container_id_list[i - 1]) + " --ip 10." + str(address_16_23) +
          "." + str(address_8_15) + ".50")
    # TODO 这句话可能执行失败
    connect_gs = sn_remote_cmd(
        remote_ssh, 'docker network connect ' + GSL_name + " " +
        str(container_id_list[j - 1]) + " --ip 9." + str(address_16_23) + "." +
        str(address_8_15) + ".60")
    print(
        'docker network connect ' + GSL_name + " " +
        str(container_id_list[j - 1]) + " --ip 9." + str(address_16_23) + "." +
        str(address_8_15) + ".60")
    try:
        connect_gs = connect_gs[0]
        print(f"connect_gs: {connect_gs}")
        if 'Error' in connect_gs:
            match = re.search(r'Gw: (\b(?:\d{1,3}\.){3}\d{1,3}\b)', connect_gs)
            if match:
                gw_value = match.group(1)
                print(f'The value of Gw is: {gw_value}')

                del_res = sn_remote_cmd(remote_ssh, f'docker exec -it {container_id_list[j-1]} ip route del 9.{address_16_23}.{address_8_15}.0/24 via {gw_value}')
                print(f"del_res: {del_res}")
                connect_gs = sn_remote_cmd(
                    remote_ssh, 'docker network connect ' + GSL_name + " " +
                    str(container_id_list[j - 1]) + " --ip 9." + str(address_16_23) + "." +
                    str(address_8_15) + ".60")
                print(f"connect_gs: {connect_gs}")
            else:
                print('Gw value not found') 
                exit(1)
    except Exception as e:
        print(connect_gs)

    ifconfig_output = sn_remote_cmd(
        remote_ssh, "docker exec -it " + str(container_id_list[j - 1]) +
        " ip addr | grep -B 2 9." + str(address_16_23) + "." +
        str(address_8_15) +
        ".60 | head -n 1 | awk -F: '{ print $2 }' | tr -d '[:blank:]'")
    print(
        "docker exec -it " + str(container_id_list[j - 1]) +
        " ip addr | grep -B 2 9." + str(address_16_23) + "." +
        str(address_8_15) +
        ".60 | head -n 1 | awk -F: '{ print $2 }' | tr -d '[:blank:]'")

    print(f"ifconfig_output: {ifconfig_output}")
    try:
        target_interface = str(ifconfig_output[0]).split("@")[0]
    except Exception as e:
        print(f'ESTABLISH_NEW_GSL ERROR: {ifconfig_output} {e}')
        exit(1)
    sn_remote_cmd(
        remote_ssh, "docker exec -d " + str(container_id_list[j - 1]) +
        " ip link set dev " + target_interface + " down")
    print(
        "docker exec -d " + str(container_id_list[j - 1]) +
        " ip link set dev " + target_interface + " down")
    sn_remote_cmd(
        remote_ssh, "docker exec -d " + str(container_id_list[j - 1]) +
        " ip link set dev " + target_interface + " name " + "B" + str(j) +
        "-eth" + str(i - 1 + 1))
    print(
        "docker exec -d " + str(container_id_list[j - 1]) +
        " ip link set dev " + target_interface + " name " + "B" + str(j) +
        "-eth" + str(i - 1 + 1))
    sn_remote_cmd(
        remote_ssh, "docker exec -d " + str(container_id_list[j - 1]) +
        " ip link set dev B" + str(j) + "-eth" + str(i - 1 + 1) + " up")
    print(
        "docker exec -d " + str(container_id_list[j - 1]) +
        " ip link set dev B" + str(j) + "-eth" + str(i - 1 + 1) + " up")
    sn_remote_cmd(
        remote_ssh, "docker exec -d " + str(container_id_list[j - 1]) +
        " tc qdisc add dev B" + str(j) + "-eth" + str(i - 1 + 1) +
        " root netem delay " + str(delay) + "ms")
    print(
        "docker exec -d " + str(container_id_list[j - 1]) +
        " tc qdisc add dev B" + str(j) + "-eth" + str(i - 1 + 1) +
        " root netem delay " + str(delay) + "ms")
    sn_remote_cmd(
        remote_ssh, "docker exec -d " + str(container_id_list[j - 1]) +
        " tc qdisc add dev B" + str(j) + "-eth" + str(i - 1 + 1) +
        " root netem loss " + str(loss) + "%")
    print(
        "docker exec -d " + str(container_id_list[j - 1]) +
        " tc qdisc add dev B" + str(j) + "-eth" + str(i - 1 + 1) +
        " root netem loss " + str(loss) + "%")
    sn_remote_cmd(
        remote_ssh, "docker exec -d " + str(container_id_list[j - 1]) +
        " tc qdisc add dev B" + str(j) + "-eth" + str(i - 1 + 1) +
        " root netem rate " + str(bw) + "Gbps")
    print(
        "docker exec -d " + str(container_id_list[j - 1]) +
        " tc qdisc add dev B" + str(j) + "-eth" + str(i - 1 + 1) +
        " root netem rate " + str(bw) + "Gbps")
    print('[Add right node:]' + 'docker network connect ' + GSL_name + " " +
          str(container_id_list[j - 1]) + " --ip 10." + str(address_16_23) +
          "." + str(address_8_15) + ".60")
    print("[func end] - sn_establish_new_GSL")


def sn_del_link(first_index, second_index, container_id_list, remote_ssh):
    print("[func begin] - sn_del_link")
    sn_remote_cmd(
        remote_ssh, "docker exec -d " +
        str(container_id_list[second_index - 1]) + " ip link set dev B" +
        str(second_index) + "-eth" + str(first_index) + " down")
    print(
        "docker exec -d " +
        str(container_id_list[second_index - 1]) + " ip link set dev B" +
        str(second_index) + "-eth" + str(first_index) + " down")

    sn_remote_cmd(
        remote_ssh, "docker exec -d " +
        str(container_id_list[first_index - 1]) + " ip link set dev B" +
        str(first_index) + "-eth" + str(second_index) + " down")
    print(
        "docker exec -d " +
        str(container_id_list[first_index - 1]) + " ip link set dev B" +
        str(first_index) + "-eth" + str(second_index) + " down")

    GSL_name = "GSL_" + str(first_index) + "-" + str(second_index)
    sn_remote_cmd(
        remote_ssh, 'docker network disconnect ' + GSL_name + " " +
        str(container_id_list[first_index - 1]))
    print(
        'docker network disconnect ' + GSL_name + " " +
        str(container_id_list[first_index - 1]))

    sn_remote_cmd(
        remote_ssh, 'docker network disconnect ' + GSL_name + " " +
        str(container_id_list[second_index - 1]))
    print(
        'docker network disconnect ' + GSL_name + " " +
        str(container_id_list[second_index - 1]))

    sn_remote_cmd(remote_ssh, 'docker network rm ' + GSL_name)
    print('docker network rm ' + GSL_name)

    print("[func end] - sn_del_link")


# A thread designed for stopping the emulation.
class sn_Emulation_Stop_Thread(threading.Thread):

    def __init__(self, remote_ssh, remote_ftp, file_path):
        threading.Thread.__init__(self)
        self.remote_ssh = remote_ssh
        self.remote_ftp = remote_ftp
        self.file_path = file_path

    def run(self):
        print("Deleting all native bridges and containers...")
        self.remote_ftp.put(
            os.path.join(os.getcwd(), "starrynet/sn_orchestrater.py"),
            self.file_path + "/sn_orchestrater.py")
        sn_remote_cmd(self.remote_ssh,
                      PYTHON_PATH + " " + self.file_path + "/sn_orchestrater.py")
