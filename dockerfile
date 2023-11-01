FROM lwsen/starlab_node:1.0
ARG GUIC_DIR=../aioquic
RUN apt update

WORKDIR /tmp
RUN apt install -y wget unzip
RUN wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz
RUN tar xzf Python-3.10.0.tgz

WORKDIR /tmp/Python-3.10.0
RUN apt-get update && apt-get install -y \ 
    libc6 \
    libc6-dev \
    gcc \
    libffi-dev gcc musl-dev

RUN ./configure --enable-optimizations --with-ctypes
RUN make altinstall
RUN apt install -y libssl-dev

# GRADLE
WORKDIR /tmp
COPY gradle-7.6.1-bin.zip /tmp/gradle-7.6.1-bin.zip
RUN unzip -d /opt/gradle /tmp/gradle-7.6.1-bin.zip
# RUN echo "export GRADLE_HOME=/opt/gradle/gradle-7.6.1" | tee -a /etc/profile.d/gradle.sh
RUN echo "export PATH=/opt/gradle/gradle-7.6.1/bin:${PATH}" | tee -a /etc/profile.d/gradle.sh

WORKDIR /home/
COPY ./aioquic /home/aioquic
# RUN alias python='/usr/local/bin/python3.10' # python版本绑定
RUN ln -s /usr/local/bin/python3.10 /usr/bin/python 

RUN python -m pip install aioquic wsproto httpbin werkzeug==2.0.3 flask==2.1.3 asgiref starlette typer requests
COPY ./pyledbat /home/pyledbat

WORKDIR /
RUN mkdir /fisco-client

# 安装jdk-11
COPY openlogic-openjdk-jre-11.0.20+8-linux-x64.tar.gz /tmp/openlogic-openjdk-jre-11.0.20+8-linux-x64.tar.gz
WORKDIR /tmp
RUN tar xvf openlogic-openjdk-jre-11.0.20+8-linux-x64.tar.gz
# RUN echo "export PATH=$PATH:/tmp/openlogic-openjdk-jre-11.0.20+8-linux-x64/bin" >> /etc/profile
# RUN . /etc/profile
ENV PATH="${PATH}:$PATH:/tmp/openlogic-openjdk-jre-11.0.20+8-linux-x64/bin"

WORKDIR /fisco-client
COPY console.tar.gz /fisco-client
# RUN apt install -y default-jdk
# COPY openlogic-openjdk-jre-11.0.20+8-linux-x64-deb.deb /tmp/openlogic-openjdk-jre-11.0.20+8-linux-x64-deb.deb
# RUN dpkg -i /tmp/openlogic-openjdk-jre-11.0.20+8-linux-x64-deb.deb
RUN tar -xzvf console.tar.gz
COPY change_toml.py /fisco-client/console/conf/change_toml.py
# temp add change_toml2.py
COPY change_toml2.py /fisco-client/console/conf/change_toml2.py 
COPY SimpleBank.sol /fisco-client/console/contracts/solidity/SimpleBank.sol
COPY logging.sol /fisco-client/console/contracts/solidity/logging.sol
COPY call_contract.sh /call_contract.sh
RUN python -m pip install toml

WORKDIR /
RUN python -m pip install grpcio grpcio-tools "Flask[async]" aiohttp aiofiles

RUN mkdir /relsharding-client
RUN mkdir /relsharding-py
WORKDIR /relsharding-client
COPY relsharding-clientv0.1.tar.gz /relsharding-client
RUN tar -xzvf relsharding-clientv0.1.tar.gz

WORKDIR /relsharding-py
COPY relsharding-pyv0.1.tar.gz /relsharding-py
RUN tar -xzvf relsharding-pyv0.1.tar.gz
# RUN apt install -y nodejs npm
# 安装Node.js和npm
RUN apt-get update && apt-get install -y curl gnupg apt-transport-https ca-certificates
RUN apt-get install -y ca-certificates curl gnupg
RUN mkdir -p /etc/apt/keyrings
# RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
# RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_16.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
# RUN apt-get update
# RUN apt-get install nodejs -y
# WORKDIR /relsharding-py/relsharding-py/js
# RUN npm install --save axios

WORKDIR /

EXPOSE 4433 4433

# CMD bird -c /home/bird/brid.conf
