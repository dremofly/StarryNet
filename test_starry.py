"""
此脚本用于自动化测试流程。
对于给定的配置列表，脚本会依次执行以下操作：
1. 将配置写入 config.json.503 文件。
2. 运行 example.py 脚本，并将输出保存到 output.txt 文件中。
3. 创建一个以配置名命名的新文件夹，并将 output.txt 文件移动到该文件夹中。
"""

import json
import os
import subprocess
from datetime import datetime
import shutil

para1 = "satellite link loss (\"X\"% )"
configFile = "config.json.503"

basename = "starlink-5-5-550-53-grid-LeastDelay"

execuate = "example.py"

log_dir = "/home/hong/log/starrynet"
log_files = os.path.join(log_dir, datetime.now().strftime('%Y%m%d_%H%M%S'))

os.mkdir(log_files)

print("create log files ", log_files)

# 配置列表
new_configs = ["0", "10"] # sat loss configurations

for new_config in new_configs:
    # 修改 config.json.503 文件
    with open(configFile, 'r') as f:
        data = json.load(f)

    # 修改特定参数
    data[para1] = new_config
    print(f"{para1}: {data[para1]}")

    with open(configFile, 'w') as f:
        json.dump(data, f)
    
    

    # 运行 python 脚本并将输出保存到 output.txt
    with open('output.txt', 'w') as f:
        subprocess.run(['python', execuate], stdout=f)

    # 从修改过的 config.json.503 文件中读取配置名称
    with open(configFile, 'r') as f:
        config_name = json.load(f)[para1]

    new_files = os.path.join(log_files, "loss_"+config_name)
    # 创建一个以配置名称命名的新文件夹，并将 output.txt 移动到新文件夹中
    os.makedirs(new_files, exist_ok=True)
    shutil.move('output.txt', os.path.join(new_files, 'output.txt'))
    shutil.move(basename, os.path.join(new_files, basename))
    shutil.move("/home/hong/"+basename, os.path.join(new_files, basename+"_dir2"))
