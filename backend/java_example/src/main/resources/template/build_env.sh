sudo apt update -y
sudo apt install git docker docker-compose -y
echo '
{
	  "registry-mirrors": ["https://y0qd3iq.mirror.aliyuncs.com"]
}
' >> /etc/docker/daemon.json
systemctl restart docker.service
docker pull hyperledger/fabric-tools:2.2.0
docker pull hyperledger/fabric-peer:2.2.0
docker pull hyperledger/fabric-orderer:2.2.0
docker pull hyperledger/fabric-ccenv:2.2.0
docker pull hyperledger/fabric-baseos:2.2.0
docker pull hyperledger/fabric-ca:1.4.7

mkdir develop && cd develop
wget https://studygolang.com/dl/golang/go1.14.4.linux-amd64.tar.gz
tar zxvf go1.14.4.linux-amd64.tar.gz
echo '
export PATH=$PATH:/root/develop/go/bin
export GOROOT=/root/develop/go
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin
' >> ~/.profile
source ~/.profile
cd

mkdir -p go/src/github.com/hyperledger/fabric-ca && cd go/src/github.com/hyperledger/fabric-ca
make fabric-ca-client
cd bin
chmod 775 fabric-ca-client
cd
