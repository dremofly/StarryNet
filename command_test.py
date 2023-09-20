import subprocess
from starrynet.sn_utils import sn_init_remote_machine, sn_remote_cmd

host = "202.120.38.138"
username = "hong"
port=6010

remote_ssh, transport = sn_init_remote_machine(host, username, "", port)



res = sn_remote_cmd(remote_ssh, "docker exec -it 6e47c754e655 ps aux")

# print(res)

for item in res:
    if 'python' in item:
        pid = item.split()[1]

# shutdown
res2 = sn_remote_cmd(remote_ssh, "docker exec -it 6e47c754e655 kill -9 " + pid)





