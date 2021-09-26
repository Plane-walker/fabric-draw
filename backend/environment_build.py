import subprocess


def build_env_full(identity: str):
    command_update = f'sudo apt update -y &> /dev/null'
    subprocess.run(command_update, shell=True, stdout=subprocess.PIPE)
    command_install = f'sudo apt install git docker docker-compose -y &> /dev/null'
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
    pull_tools = f'docker pull hyperledger/fabric-tools:2.2.0 &> /dev/null'
    subprocess.run(pull_tools, shell=True, stdout=subprocess.PIPE)
    fabric_ccenv = f'echo "---pull fabric-ccenv---"'
    subprocess.run(fabric_ccenv, shell=True, stdout=subprocess.PIPE)
    pull_ccenv = f'docker pull hyperledger/fabric-ccenv:2.2.0 &> /dev/null'
    subprocess.run(pull_ccenv, shell=True, stdout=subprocess.PIPE)
    fabric_baseos = f'echo "---pull fabric-baseos---"'
    subprocess.run(fabric_baseos, shell=True, stdout=subprocess.PIPE)
    pull_baseos = f'docker pull hyperledger/fabric-baseos:2.2.0 &> /dev/null'
    subprocess.run(pull_baseos, shell=True, stdout=subprocess.PIPE)
    develop = f'mkdir develop && cd develop'
    subprocess.run(develop, shell=True, stdout=subprocess.PIPE)
    wegt = f'wget https://studygolang.com/dl/golang/go1.15.6.linux-amd64.tar.gz &> /dev/null'
    subprocess.run(wegt, shell=True, stdout=subprocess.PIPE)
    path = f'echo"'
    path += f'export PATH=$PATH:/root/develop/go/bin\n'
    path += f'export GOROOT=/root/develop/go\n'
    path += f'export GOPATH=$HOME/go\n'
    path += f'export PATH=$PATH:$GOPATH/bin\n'
    path += f'" >> ~/.profile'
    subprocess.run(path, shell=True, stdout=subprocess.PIPE)
    profile = f'source ~/.profile'
    subprocess.run(profile, shell=True, stdout=subprocess.PIPE)
    cd = f'cd'
    subprocess.run(cd, shell=True, stdout=subprocess.PIPE)
    env_complete = f'echo "---base env build completed---"'
    subprocess.run(env_complete, shell=True, stdout=subprocess.PIPE)

    if identity == "ca":
        fabric_ca = f'echo "---pull fabric-ca---"'
        subprocess.run(fabric_ca, shell=True, stdout=subprocess.PIPE)
        pull_ca = f'docker pull hyperledger/fabric-ca:1.4.7 &> /dev/null'
        subprocess.run(pull_ca, shell=True, stdout=subprocess.PIPE)
        ca_env = f'echo "---ca env build completed---"'
        subprocess.run(ca_env, shell=True, stdout=subprocess.PIPE)
    elif identity == "peer":
        fabric_peer = f'echo "---pull fabric-peer---"'
        subprocess.run(fabric_peer, shell=True, stdout=subprocess.PIPE)
        pull_peer = f'docker pull hyperledger/fabric-peer:2.2.0 &> /dev/null'
        subprocess.run(pull_peer, shell=True, stdout=subprocess.PIPE)
        ledger = f'mkdir -p go/src/github.com/hyperledger && cd go/src/github.com/hyperledger'
        subprocess.run(ledger, shell=True, stdout=subprocess.PIPE)
        clone_ca = f'git clone https://gitee.com/planewalker/fabric-ca.git &> /dev/null'
        subprocess.run(clone_ca, shell=True , stdout=subprocess.PIPE)
        cd_ca = f'cd fabric-ca'
        subprocess.run(cd_ca, shell=True, stdout=subprocess.PIPE)
        print_ca = f'echo "---make fabric-ca-client---"'
        subprocess.run(print_ca, shell=True, stdout=subprocess.PIPE)
        make_ca = f'make fabric-ca-client &> /dev/null'
        subprocess.run(make_ca, shell=True, stdout=subprocess.PIPE)
        cp_ca = f'cp bin/fabric-ca-client /usr/local/bin'
        subprocess.run(cp_ca, shell=True, stdout=subprocess.PIPE)
        chmod_ca = f'chmod 775 /usr/local/bin/fabric-ca-client'
        subprocess.run(chmod_ca, shell=True, stdout=subprocess.PIPE)
        cd = f'cd'
        subprocess.run(cd, shell=True, stdout=subprocess.PIPE)
        peer_env = f'echo "---peer env build completed---"'
        subprocess.run(peer_env, shell=True, stdout=subprocess.PIPE)
    elif identity == "orderer":
        printf = f'echo "---pull fabric-orderer---"'
        subprocess.run(printf, shell=True, stdout=subprocess.PIPE)
        dock_order = f'docker pull hyperledger/fabric-orderer:2.2.0 &> /dev/null'
        subprocess.run(dock_order, shell=True, stdout=subprocess.PIPE)
        mkdir_cd = f'mkdir -p go/src/github.com/hyperledger && cd go/src/github.com/hyperledger'
        subprocess.run(mkdir_cd, shell=True, stdout=subprocess.PIPE)
        clone_plans = f'git clone https://gitee.com/planewalker/fabric-ca.git &> /dev/null'
        subprocess.run(clone_plans, shell=True, stdout=subprocess.PIPE)
        cd_ca = f'cd fabric-ca'
        subprocess.run(cd_ca, shell=True, stdout=subprocess.PIPE)
        printf = f'echo "---make fabric-ca-client---"'
        subprocess.run(printf, shell=True, stdout=subprocess.PIPE)
        make_client = f'make fabric-ca-client &> /dev/null'
        subprocess.run(make_client, shell=True, stdout=subprocess.PIPE)
        cp_client = f'cp bin/fabric-ca-client /usr/local/bin'
        subprocess.run(cp_client, shell=True, stdout=subprocess.PIPE)
        chmod_client = f'chmod 775 /usr/local/bin/fabric-ca-client'
        subprocess.run(chmod_client, shell=True, stdout=subprocess.PIPE)
        cd = f'cd ..'
        subprocess.run(cd, shell=True, stdout=subprocess.PIPE)
        clone_plane = f'git clone https://gitee.com/planewalker/fabric.git &> /dev/null'
        subprocess.run(clone_plane, shell=True, stdout=subprocess.PIPE)
        cd_fabric = f'cd fabric'
        subprocess.run(cd_fabric, shell=True, stdout=subprocess.PIPE)
        print = f'echo "---make fabric---"'
        subprocess.run(print, shell=True, stdout=subprocess.PIPE)
        make_re = f'make release &> /dev/null'
        subprocess.run(make_re, shell=True, stdout=subprocess.PIPE)
        cp_release = f'cp release/linux-amd64/bin/configtxgen /usr/local/bin'
        subprocess.run(cp_release, shell=True, stdout=subprocess.PIPE)
        chmod_usr = f'chmod 775 /usr/local/bin/configtxgen'
        subprocess.run(chmod_usr, shell=True, stdout=subprocess.PIPE)
        cd = f'cd'
        subprocess.run(cd, shell=True, stdout=subprocess.PIPE)
        printf = f'echo "---orderer env build completed---"'
        subprocess.run(printf, shell=True, stdout=subprocess.PIPE)
