from Crypto.Hash import keccak
import subprocess
import time
import sys
import random

def get_key(file):
    filename = f'/relsharding-client/relsharding-client/dist/keys/B{file}pub.txt'
    f = open(filename, 'r')
    address = f.readline()
    f.close() 
    return address

counter = 1
# 原始数据
data = bytearray(b"0 This is some data to hash")

contractAddress = sys.argv[1]
keyFile = sys.argv[2] # 
# contractAddress = '0xa6dc067e2ab9e25b61a9f49ea1857f57f5b0e5aa'

maliciouAccount = '0x8aa097dff6ac9306ecedb660348284116c7969a'

proba = 1

while True:
    k = keccak.new(digest_bits=256)
    data[0] = ord(str(counter))
    counter = (counter + 1) % 10
    # 创建Keccak-256哈希对象
    k.update(data)
    # 获取哈希的十六进制表示
    hash_hex = k.hexdigest()
    print("Keccak-256 Hash:", hash_hex)

    random_number = random.randint(1, 10)
    if random_number <= proba:
        account = maliciouAccount
    else:
        account = get_key(keyFile)

    command = f'bash /fisco-client/console/console.sh call logging {contractAddress} SubLog2 {account} {hash_hex}'
    process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = process.stdout
    print(output)
    time.sleep(1)
