#!/bin/bash

# 执行 `docker ps` 命令，关键字搜索包含 "ovs_container_1" 的行，然后通过 awk 获取容器的hash
TARGET_ID=$(docker ps --format "{{.ID}}: {{.Names}}" | grep -P "ovs_container_1\b" | cut -d: -f1)

echo "ID $TARGET_ID" 

# 用目标容器ID运行你的命令
docker exec -it $TARGET_ID bash -c "cd /relsharding-client/relsharding-client/dist && java -cp 'conf/:lib/*:apps/*' org.fisco.bcos.sdk.demo.rclient.RelayServer"
