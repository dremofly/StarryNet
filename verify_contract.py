import sys
import subprocess
import time
import re

contractAddress = sys.argv[1]
groupId = sys.argv[2]

addresses = []
def get_address():
    prefix = '/relsharding-client/relsharding-client/dist/'
    for i in range(25):
        filename = prefix + f'keys/B{i+1}pub.txt'
        f = open(filename, 'r')
        address = f.readline()
        f.close()
        addresses.append(address)

def get_return_value(data):
    # 使用正则表达式查找Return values后的内容
    match = re.search(r"Return values:\(([^,]+), ([^\)]+)\)", data)

    # 如果找到匹配项，则提取和打印值
    if match:
        value1 = match.group(1).strip()
        value2 = match.group(2).strip()
        print(f"account address: {value1}")
        print(f"signed message: {value2}")
        return value1, value2
    else:
        print("No match found")
        print(data)
        return 0,0
    return 0,0

get_address()
print(addresses)
while True:
    command = f'bash /fisco-client/console/console.sh {groupId} call logging {contractAddress} GetOnePengdingTx'
    abandonCmd =f'bash /fisco-client/console/console.sh {groupId} call logging {contractAddress} abandonLog' 
    submitCmd =f'bash /fisco-client/console/console.sh {groupId} call logging {contractAddress} approveLog' 
    process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = process.stdout
    account, message = get_return_value(output)
    if account in addresses:
        print("valid log")  
        process = subprocess.run(submitCmd, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    else:
        print("Found malicious node")
        process = subprocess.run(abandonCmd, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    time.sleep(1)