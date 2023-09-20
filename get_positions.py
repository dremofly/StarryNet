from starrynet.sn_observer import *
from starrynet.sn_orchestrater import *
from starrynet.sn_synchronizer import *
import pandas as pd
import sys
import json
import os


def main():
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
    # export STARRY_CONFIG=config.json.nuc
    # configuration_file_path = os.environ.get('STARRY_CONFIG')

    configuration_file_path = "./current2.json"

    hello_interval = 1  # hello_interval(s) in OSPF. 1-200 are supported.
    AS = [[1, 25+len(GS_lat_long)]]  # Node #1 to Node #27 are within the same AS.
    sn = StarryNet(configuration_file_path, GS_lat_long, hello_interval, AS)

    for i in range(25):
       pp = sn.get_position(i, 1)
       print(f"position of {i+1} is {pp}")
       


if __name__ == "__main__":
  main()
    
