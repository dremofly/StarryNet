#!/bin/bash

# 获取外部参数
DES=$1

# 定义文件路径
FILE_PATH="/fisco-client/console/conf/contract_address.txt"

echo "DES $DES"

# 检查文件是否存在
if [ -f "$FILE_PATH" ]; then
    # 读取文件内容保存到变量
    CONTRACT_ADDRESS=$(cat $FILE_PATH)
else
    echo "Error: $FILE_PATH does not exist."
    exit 1
fi

# 执行另一个脚本
bash /fisco-client/console/console.sh call SimpleBank $CONTRACT_ADDRESS transfer $DES 10
