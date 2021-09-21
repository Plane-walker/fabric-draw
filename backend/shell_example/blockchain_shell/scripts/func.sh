function build_env_full() {
  sudo apt update -y &> /dev/null
  sudo apt install git docker docker-compose -y &> /dev/null
  echo '
  {
      "registry-mirrors": ["https://y0qd3iq.mirror.aliyuncs.com"]
  }
  ' >> /etc/docker/daemon.json
  systemctl restart docker.service
  echo '---pull fabric-tools---'
  docker pull hyperledger/fabric-tools:2.2.0 &> /dev/null
  echo '---pull fabric-ccenv---'
  docker pull hyperledger/fabric-ccenv:2.2.0 &> /dev/null
  echo '---pull fabric-baseos---'
  docker pull hyperledger/fabric-baseos:2.2.0 &> /dev/null
  mkdir develop && cd develop
  echo '---install go---'
  wget https://studygolang.com/dl/golang/go1.15.6.linux-amd64.tar.gz &> /dev/null
  tar zxvf go1.15.6.linux-amd64.tar.gz &> /dev/null
  echo '
  export PATH=$PATH:/root/develop/go/bin
  export GOROOT=/root/develop/go
  export GOPATH=$HOME/go
  export PATH=$PATH:$GOPATH/bin
  ' >> ~/.profile
  source ~/.profile
  cd
  echo '---base env build completed---'
  if [ "$1" = "ca" ]; then
    echo '---pull fabric-ca---'
    docker pull hyperledger/fabric-ca:1.4.7 &> /dev/null
    echo '---ca env build completed---'
  elif [ "$1" = "peer" ]; then
    echo '---pull fabric-peer---'
    docker pull hyperledger/fabric-peer:2.2.0 &> /dev/null
    mkdir -p go/src/github.com/hyperledger && cd go/src/github.com/hyperledger
    git clone https://gitee.com/planewalker/fabric-ca.git &> /dev/null
    cd fabric-ca
    echo '---make fabric-ca-client---'
    make fabric-ca-client &> /dev/null
    cp bin/fabric-ca-client /usr/local/bin
    chmod 775 /usr/local/bin/fabric-ca-client
    cd
    echo '---peer env build completed---'
  elif [ "$1" = "orderer" ]; then
    echo '---pull fabric-orderer---'
    docker pull hyperledger/fabric-orderer:2.2.0 &> /dev/null
    mkdir -p go/src/github.com/hyperledger && cd go/src/github.com/hyperledger
    git clone https://gitee.com/planewalker/fabric-ca.git &> /dev/null
    cd fabric-ca
    echo '---make fabric-ca-client---'
    make fabric-ca-client &> /dev/null
    cp bin/fabric-ca-client /usr/local/bin
    chmod 775 /usr/local/bin/fabric-ca-client
    cd ..
    git clone https://gitee.com/planewalker/fabric.git &> /dev/null
    cd fabric
    echo '---make fabric---'
    make release &> /dev/null
    cp release/linux-amd64/bin/configtxgen /usr/local/bin
    chmod 775 /usr/local/bin/configtxgen
    cd
    echo '---orderer env build completed---'
  fi
}

function build_env() {
  echo '---skip build env---'
}

function create_org() {
  mkdir -p $CRYPTO_BASE/organizations/peerOrganizations/${1}.${2}/
  export FABRIC_CA_CLIENT_HOME=$CRYPTO_BASE/organizations/peerOrganizations/${1}.${2}/
  export CA_TLS_CA=$CRYPTO_BASE/organizations/fabric-ca/${1}/tls-cert.pem
  fabric-ca-client enroll -u https://admin:adminpw@ca.${1}.${2}:${3} --caname ca-${1} --tls.certfiles $CA_TLS_CA
  echo "NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/localhost-${3}-ca-${1}.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/localhost-${3}-ca-${1}.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/localhost-${3}-ca-${1}.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/localhost-${3}-ca-${1}.pem
    OrganizationalUnitIdentifier: orderer" >> $CRYPTO_BASE/organizations/peerOrganizations/${1}.${2}/msp/config.yaml
  cp $CRYPTO_BASE/organizations/peerOrganizations/${1}.${2}/msp/cacerts/* $CRYPTO_BASE/organizations/peerOrganizations/${1}.${2}/msp/cacerts/localhost-${3}-ca-${1}.pem
}

function create_peer() {
  mkdir -p $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}
  fabric-ca-client register --caname ca-${1} --id.name ${2} --id.secret ${2}pw --id.type peer --tls.certfiles $CA_TLS_CA
  fabric-ca-client enroll -u https://${2}:${2}pw@ca.${1}.${3}:${4} --caname ca-${1} -M $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/msp --csr.hosts ${2}.${1}.${3} --tls.certfiles $CA_TLS_CA
  cp $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/msp/cacerts/* $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/msp/cacerts/localhost-${4}-ca-${1}.pem
  fabric-ca-client enroll -u https://${2}:${2}pw@ca.${1}.${3}:${4} --caname ca-${1} -M $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/tls --enrollment.profile tls --csr.hosts ${2}.${1}.${3} --csr.hosts localhost --tls.certfiles $CA_TLS_CA
  cp $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/msp/config.yaml $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/msp/config.yaml
  cp $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/tls/tlscacerts/* $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/tls/ca.crt
  cp $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/tls/signcerts/* $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/tls/server.crt
  cp $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/tls/keystore/* $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/tls/server.key
  mkdir -p $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/users/Admin@${1}.${3}
  fabric-ca-client register --caname ca-${1} --id.name ${1}admin --id.secret ${1}adminpw --id.type admin --tls.certfiles $CA_TLS_CA
  fabric-ca-client enroll -u https://${1}admin:${1}adminpw@ca.${1}.${3}:${4} --caname ca-${1} -M $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/users/Admin@${1}.${3}/msp --tls.certfiles $CA_TLS_CA
  cp $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/users/Admin@${1}.${3}/msp/cacerts/* $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/users/Admin@${1}.${3}/msp/cacerts/localhost-${4}-ca-${1}.pem
  cp $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/msp/config.yaml $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/users/Admin@${1}.${3}/msp/config.yaml
  mkdir -p $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/msp/tlscacerts
  cp $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/tls/tlscacerts/* $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/msp/tlscacerts/ca.crt
  mkdir -p $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/tlsca
  cp $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/tls/tlscacerts/* $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/tlsca/tlsca.${1}.${3}-cert.pem
  mkdir -p $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/ca
  cp $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/msp/cacerts/* $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/ca
}


function create_orderer_org() {
  mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${2}/
  export FABRIC_CA_CLIENT_HOME=$CRYPTO_BASE/organizations/ordererOrganizations/${2}/
  export CA_TLS_CA=$CRYPTO_BASE/organizations/fabric-ca/ordererOrg/tls-cert.pem
  fabric-ca-client enroll -u https://admin:adminpw@ca.${2}:${3} --caname ca-orderer --tls.certfiles $CA_TLS_CA
  echo "NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/localhost-${3}-ca-orderer.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/localhost-${3}-ca-orderer.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/localhost-${3}-ca-orderer.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/localhost-${3}-ca-orderer.pem
    OrganizationalUnitIdentifier: orderer" >> $CRYPTO_BASE/organizations/ordererOrganizations/${2}/msp/config.yaml
      cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/msp/cacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${2}/msp/cacerts/localhost-${3}-ca-orderer.pem
}

function create_orderer() {
  mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}
  export CA_TLS_CA=$CRYPTO_BASE/organizations/fabric-ca/ordererOrg/tls-cert.pem
  fabric-ca-client register --caname ca-orderer --id.name ${1} --id.secret ${1}pw --id.type orderer --tls.certfiles $CA_TLS_CA
  fabric-ca-client enroll -u https://${1}:${1}pw@ca.${2}:${3} --caname ca-orderer -M $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/msp --csr.hosts ${1}.${2} --tls.certfiles $CA_TLS_CA
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/msp/cacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/msp/cacerts/localhost-${3}-ca-${1}.pem
  fabric-ca-client enroll -u https://${1}:${1}pw@ca.${2}:${3} --caname ca-orderer -M $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls --enrollment.profile tls --csr.hosts ${1}.${2} --csr.hosts localhost --tls.certfiles $CA_TLS_CA
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/msp/config.yaml $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/msp/config.yaml
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls/tlscacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls/ca.crt
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls/signcerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls/server.crt
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls/keystore/* $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls/server.key
  mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${2}/users/Admin@${2}
  fabric-ca-client register --caname ca-orderer --id.name ${1}admin --id.secret ${1}adminpw --id.type admin --tls.certfiles $CA_TLS_CA
  fabric-ca-client enroll -u https://ordereradmin:ordereradminpw@ca.${2}:${3} --caname ca-orderer -M $CRYPTO_BASE/organizations/ordererOrganizations/${2}/users/Admin@${2}/msp --tls.certfiles $CA_TLS_CA
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/users/Admin@${2}/msp/cacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${2}/users/Admin@${2}/msp/cacerts/localhost-${3}-ca-${1}.pem
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/msp/config.yaml $CRYPTO_BASE/organizations/ordererOrganizations/${2}/users/Admin@${2}/msp/config.yaml
  mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${2}/msp/tlscacerts
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls/tlscacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${2}/msp/tlscacerts/ca.crt
  mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${2}/tlsca
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls/tlscacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${2}/tlsca/tlsca.${2}-cert.pem
  mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${2}/ca
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/msp/cacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${2}/ca
  mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/msp/tlscacerts
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls/tlscacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/msp/tlscacerts/tlsca.${2}-cert.pem
}
