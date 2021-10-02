import subprocess
import sys


def build_env_full(identity: str):
    command_update = f'sudo apt update -y'
    subprocess.run(command_update, shell=True, stdout=subprocess.PIPE)
    command_install = f'sudo apt install git docker.io docker-compose -y'
    subprocess.run(command_install, shell=True, stdout=subprocess.PIPE)
    registry_mirrors = 'echo "'
    registry_mirrors += '{\n'
    registry_mirrors += f'""registry-mirrors": ["https://y0qd3iq.mirror.aliyuncs.com"]\n'
    registry_mirrors += '}"'
    registry_mirrors += ' >> /etc/docker/daemon.json'
    subprocess.run(registry_mirrors, shell=True, stdout=subprocess.PIPE)
    re_dock = f'systemctl restart docker.service'
    subprocess.run(re_dock, shell=True, stdout=subprocess.PIPE)
    fabric_tools = f'echo "---pull fabric-tools---"'
    subprocess.run(fabric_tools, shell=True, stdout=subprocess.PIPE)
    pull_tools = f'docker pull hyperledger/fabric-tools:2.2.0'
    subprocess.run(pull_tools, shell=True, stdout=subprocess.PIPE)
    fabric_ccenv = f'echo "---pull fabric-ccenv---"'
    subprocess.run(fabric_ccenv, shell=True, stdout=subprocess.PIPE)
    pull_ccenv = f'docker pull hyperledger/fabric-ccenv:2.2.0'
    subprocess.run(pull_ccenv, shell=True, stdout=subprocess.PIPE)
    fabric_baseos = f'echo "---pull fabric-baseos---"'
    subprocess.run(fabric_baseos, shell=True, stdout=subprocess.PIPE)
    pull_baseos = f'docker pull hyperledger/fabric-baseos:2.2.0'
    subprocess.run(pull_baseos, shell=True, stdout=subprocess.PIPE)
    develop = f'mkdir develop && cd develop;'\
              'wget https://studygolang.com/dl/golang/go1.15.6.linux-amd64.tar.gz;'\
              'echo"\n'\
              'export PATH=$PATH:/root/develop/go/bin\n'\
              'export GOROOT=/root/develop/go\n'\
              'export PATH=$PATH:$GOPATH/bin\n'\
              '" >> ~/.profile;' \
              'source ~/.profile;cd'\
              'echo "---base env build completed---"'
    subprocess.run(develop, shell=True, stdout=subprocess.PIPE)
    if identity == "ca":
        fabric_ca = f'echo "---pull fabric-ca---"'
        subprocess.run(fabric_ca, shell=True, stdout=subprocess.PIPE)
        pull_ca = f'docker pull hyperledger/fabric-ca:1.4.7'
        subprocess.run(pull_ca, shell=True, stdout=subprocess.PIPE)
        ca_env = f'echo "---ca env build completed---"'
        subprocess.run(ca_env, shell=True, stdout=subprocess.PIPE)
    elif identity == "peer":
        fabric_peer = f'echo "---pull fabric-peer---"'
        subprocess.run(fabric_peer, shell=True, stdout=subprocess.PIPE)
        pull_peer = f'docker pull hyperledger/fabric-peer:2.2.0'
        subprocess.run(pull_peer, shell=True, stdout=subprocess.PIPE)
        ledger = f'mkdir -p go/src/github.com/hyperledger && cd go/src/github.com/hyperledger;'\
                 'git clone https://gitee.com/planewalker/fabric-ca.git'\
                 'cd fabric-ca;'\
                 'echo "---make fabric-ca-client---"'\
                 'make fabric-ca-client'\
                 'cp bin/fabric-ca-client /usr/local/bin'\
                 'chmod 775 /usr/local/bin/fabric-ca-client'     
        subprocess.run(ledger, shell=True, stdout=subprocess.PIPE)
        peer_env = f'echo "---peer env build completed---"'
        subprocess.run(peer_env, shell=True, stdout=subprocess.PIPE)
    elif identity == "orderer":
        printf = f'echo "---pull fabric-orderer---"'
        subprocess.run(printf, shell=True, stdout=subprocess.PIPE)
        dock_order = f'docker pull hyperledger/fabric-orderer:2.2.0'
        subprocess.run(dock_order, shell=True, stdout=subprocess.PIPE)
        mkdir_cd = f'mkdir -p go/src/github.com/hyperledger && cd go/src/github.com/hyperledger;'\
                   'git clone https://gitee.com/planewalker/fabric-ca.git;'\
                   'git clone https://gitee.com/planewalker/fabric.git;'\
                   'cd fabric-ca;'\
                   'echo "---make fabric-ca-client---";'\
                   'cp bin/fabric-ca-client /usr/local/bin;'\
                   'chmod 775 /usr/local/bin/fabric-ca-client;cd;'\
                   'cd fabric;'\
                   'echo "---make fabric---";'\
                   'make release;'\
                   'cp release/linux-amd64/bin/configtxgen /usr/local/bin;'\
                   'chmod 775 /usr/local/bin/configtxgen;cd;'\
                   'echo "---orderer env build completed---"'   
        subprocess.run(mkdir_cd, shell=True, stdout=subprocess.PIPE)
if __name__ == '__main__':
    build_env_full(sys.argv[1])
