#!/usr/bin/python
# -*- coding: UTF-8 -*-

from starrynet.sn_observer import *
from starrynet.sn_orchestrater import *
from starrynet.sn_synchronizer import *
import subprocess
import os

def run_command(command):
    process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = process.stdout
    print(output)

if __name__ == "__main__":
    target_id = ""
    with os.popen("docker ps") as f:
        for line in f.readlines():
            if "ovs_container_1" in line:
                temp = line.split()
                target_id = temp[0]
                break
    
    if target_id != "":
        cmd = f'''docker exec -it {target_id} bash -c "cd /relsharding-client/relsharding-client/dist/ && java -cp 'conf/:lib/*:apps/*' org.fisco.bcos.sdk.demo.rclient.RelayClient 10.0.7.10 /fisco-client/console/conf/contract_address.txt 10 0xb6c01da64424a3345a25813016587f4264b6b3da keys/B1key.txt"'''

        run_command(cmd)
    
