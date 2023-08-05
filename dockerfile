FROM lwsen/starlab_node:1.0

ARG GUIC_DIR=../aioquic

RUN apt update

WORKDIR /tmp
RUN apt install -y wget
RUN wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz
RUN tar xzf Python-3.10.0.tgz

WORKDIR /tmp/Python-3.10.0
RUN ./configure --enable-optimizations
RUN make altinstall
RUN apt install -y libssl-dev

WORKDIR /home/
COPY ./aioquic /home/aioquic
# RUN alias python='/usr/local/bin/python3.10' # python版本绑定
RUN ln -s /usr/local/bin/python3.10 /usr/bin/python 

RUN python -m pip install aioquic wsproto httpbin werkzeug==2.0.3 flask==2.1.3 asgiref starlette
COPY ./pyledbat /home/pyledbat

WORKDIR /
RUN mkdir /fisco-client

WORKDIR /fisco-client
COPY console.tar.gz /fisco-client
RUN apt install -y default-jdk
RUN tar -xzvf console.tar.gz
COPY change_toml.py /fisco-client/console/conf/change_toml.py
COPY SimpleBank.sol /fisco-client/console/contracts/solidity/SimpleBank.sol
COPY call_contract.sh /call_contract.sh
RUN python -m pip install toml

WORKDIR /

EXPOSE 4433 4433

# CMD bird -c /home/bird/brid.conf
