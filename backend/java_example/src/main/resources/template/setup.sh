function create_org() {
  mkdir -p $CRYPTO_BASE/organizations/peerOrganizations/${1}.${2}/
  export FABRIC_CA_CLIENT_HOME=$CRYPTO_BASE/organizations/peerOrganizations/${1}.${2}/
  export CA_TLS_CA=$CRYPTO_BASE/organizations/fabric-ca/${1}/tls-cert.pem
  fabric-ca-client enroll -u https://admin:adminpw@localhost:${3} --caname ca-${1} --tls.certfiles $CA_TLS_CA
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
}

function create_peer() {
  mkdir -p $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}
  fabric-ca-client register --caname ca-${1} --id.name ${2} --id.secret ${2}pw --id.type peer --tls.certfiles $CA_TLS_CA
  fabric-ca-client enroll -u https://${2}:${2}pw@localhost:${4} --caname ca-${1} -M $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/msp --csr.hosts ${2}.${1}.${3} --tls.certfiles $CA_TLS_CA
  fabric-ca-client enroll -u https://${2}:${2}pw@localhost:${4} --caname ca-${1} -M $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/tls --enrollment.profile tls --csr.hosts ${2}.${1}.${3} --csr.hosts localhost --tls.certfiles $CA_TLS_CA
  cp $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/msp/config.yaml $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/msp/config.yaml
  cp $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/tls/tlscacerts/* $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/tls/ca.crt
  cp $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/tls/signcerts/* $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/tls/server.crt
  cp $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/tls/keystore/* $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/tls/server.key
  mkdir -p $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/users/Admin@${1}.${3}
  fabric-ca-client register --caname ca-${1} --id.name ${1}admin --id.secret ${1}adminpw --id.type admin --tls.certfiles $CA_TLS_CA
  fabric-ca-client enroll -u https://${1}admin:${1}adminpw@localhost:${4} --caname ca-${1} -M $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/users/Admin@${1}.${3}/msp --tls.certfiles $CA_TLS_CA
  cp $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/msp/config.yaml $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/users/Admin@${1}.${3}/msp/config.yaml
  mkdir -p $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/msp/tlscacerts
  cp $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/tls/tlscacerts/* $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/msp/tlscacerts/ca.crt
  mkdir -p $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/tlsca
  cp $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/tls/tlscacerts/* $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/tlsca/tlsca.${1}.${3}-cert.pem
  mkdir -p $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/ca
  cp $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/peers/${2}.${1}.${3}/msp/cacerts/* $CRYPTO_BASE/organizations/peerOrganizations/${1}.${3}/ca/ca.${1}.${3}-cert.pem
}


function create_orderer_org() {
  mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${2}/
  export FABRIC_CA_CLIENT_HOME=$CRYPTO_BASE/organizations/ordererOrganizations/${2}/
  export CA_TLS_CA=$CRYPTO_BASE/organizations/fabric-ca/ordererOrg/tls-cert.pem
  fabric-ca-client enroll -u https://admin:adminpw@localhost:${3} --caname ca-${1} --tls.certfiles $CA_TLS_CA
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
      OrganizationalUnitIdentifier: orderer" >> $CRYPTO_BASE/organizations/ordererOrganizations/${2}/msp/config.yaml
}

function create_orderer() {
  mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}
  fabric-ca-client register --caname ca-orderer --id.name ${1} --id.secret ${1}pw --id.type orderer --tls.certfiles $CA_TLS_CA
  fabric-ca-client enroll -u https://${1}:${1}pw@localhost:${3} --caname ca-orderer -M $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/msp --csr.hosts ${1}.${2} --tls.certfiles $CA_TLS_CA
  fabric-ca-client enroll -u https://${1}:${1}pw@localhost:${3} --caname ca-orderer -M $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls --enrollment.profile tls --csr.hosts ${1}.${2} --csr.hosts localhost --tls.certfiles $CA_TLS_CA
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/msp/config.yaml $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/msp/config.yaml
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls/tlscacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls/ca.crt
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls/signcerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls/server.crt
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls/keystore/* $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls/server.key
  mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${2}/users/Admin@${2}
  fabric-ca-client register --caname ca-orderer --id.name ${1}admin --id.secret ${1}adminpw --id.type admin --tls.certfiles $CA_TLS_CA
  fabric-ca-client enroll -u https://ordereradmin:ordereradminpw@localhost:${3} --caname ca-orderer -M $CRYPTO_BASE/organizations/ordererOrganizations/${2}/users/Admin@${2}/msp --tls.certfiles $CA_TLS_CA
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/msp/config.yaml $CRYPTO_BASE/organizations/ordererOrganizations/${2}/users/Admin@${2}/msp/config.yaml
  mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${2}/msp/tlscacerts
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls/tlscacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${2}/msp/tlscacerts/ca.crt
  mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${2}/tlsca
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls/tlscacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${2}/tlsca/tlsca.${2}-cert.pem
  mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${2}/ca
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/msp/cacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${2}/ca/ca.${2}-cert.pem
  mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/msp/tlscacerts
  cp $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/tls/tlscacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${2}/orderers/${1}.${2}/msp/tlscacerts/tlsca.${2}-cert.pem

}


source build_env

export CRYPTO_BASE=/root/opt
docker-compose -f docker-compose-ca.yaml up -d
