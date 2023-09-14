import toml
import sys
import os

os.chdir("/fisco-client/console/conf")

data = toml.load('config-example.toml')

# TODO 根据不同的shards的数据编写

caNum = int(sys.argv[1])
total = int(sys.argv[2])

peers = []
for i in range(caNum, total+1):
    peers.append(f"9.{i}.{i}.10:20200")
    # peers.append(f"192.168.2.{i-1}:20200")

data['network']['peers'] = peers

with open("config.toml", 'w') as f:
    toml.dump(data, f)


