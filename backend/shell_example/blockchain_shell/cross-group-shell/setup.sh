export CA_ORDERER_IP=$GROUP1_CA_ORDERER_IP
export ORDERER_IP=$GROUP1_ORDERER_IP
export ORDERER1_IP=$GROUP2_ORDERER_IP
export CA_ORG1_IP=$GROUP1_CA_ORG1_IP
export PEER0_ORG1_IP=$GROUP1_PEER0_ORG1_IP
export CA_ORG2_IP=$GROUP2_CA_ORG1_IP
export PEER0_ORG2_IP=$GROUP2_PEER0_ORG1_IP
export CRYPTO_BASE=/root/cross


ssh root@$CA_ORDERER_IP "mkdir -p $CRYPTO_BASE;"
scp -r docker-compose-ca-orderer.yaml root@$CA_ORDERER_IP:$CRYPTO_BASE
scp -r func.sh root@$CA_ORDERER_IP:$CRYPTO_BASE
ssh root@$CA_ORDERER_IP "
export CRYPTO_BASE=/root/cross;
cd $CRYPTO_BASE;
source func.sh;
docker network create --attachable --driver overlay root_cross;
docker-compose -f docker-compose-ca-orderer.yaml up -d;
"

mkdir -p organizations/fabric-ca/ordererOrg
scp -r root@$CA_ORDERER_IP:$CRYPTO_BASE/organizations/fabric-ca/ordererOrg/tls-cert.pem organizations/fabric-ca/ordererOrg


ssh root@$ORDERER_IP "mkdir -p $CRYPTO_BASE/organizations/fabric-ca/ordererOrg;"
scp -r organizations/fabric-ca/ordererOrg/tls-cert.pem root@$ORDERER_IP:$CRYPTO_BASE/organizations/fabric-ca/ordererOrg
scp -r docker-compose-orderer.yaml root@$ORDERER_IP:$CRYPTO_BASE
scp -r configtx.yaml root@$ORDERER_IP:$CRYPTO_BASE
scp -r func.sh root@$ORDERER_IP:$CRYPTO_BASE
ssh root@$ORDERER_IP "
export CRYPTO_BASE=/root/cross;
cd $CRYPTO_BASE;
source func.sh;
echo '$CA_ORDERER_IP ca.cross.com
$PEER0_ORG1_IP peer0.org1.cross.com
$PEER0_ORG2_IP peer0.org2.cross.com' >> /etc/hosts;
create_orderer_org orderer cross.com 8054;
mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/cross.com.origin;
create_orderer orderer cross.com 8054;
"

mkdir -p organizations/ordererOrganizations/cross.com/tlsca
scp -r root@$ORDERER_IP:$CRYPTO_BASE/organizations/ordererOrganizations/cross.com/tlsca/tlsca.cross.com-cert.pem organizations/ordererOrganizations/cross.com/tlsca
mkdir -p organizations/ordererOrganizations/cross.com/orderers/orderer.cross.com/tls
scp -r root@$ORDERER_IP:$CRYPTO_BASE/organizations/ordererOrganizations/cross.com/orderers/orderer.cross.com/tls/server.crt organizations/ordererOrganizations/cross.com/orderers/orderer.cross.com/tls



ssh root@$ORDERER1_IP "mkdir -p $CRYPTO_BASE/organizations/fabric-ca/ordererOrg;
mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/cross.com/orderers/orderer.cross.com/tls;
mkdir -p $CRYPTO_BASE/channel-artifacts;"
scp -r organizations/fabric-ca/ordererOrg/tls-cert.pem root@$ORDERER1_IP:$CRYPTO_BASE/organizations/fabric-ca/ordererOrg
scp -r organizations/ordererOrganizations/cross.com/orderers/orderer.cross.com/tls/server.crt root@$ORDERER1_IP:$CRYPTO_BASE/organizations/ordererOrganizations/cross.com/orderers/orderer.cross.com/tls
scp -r docker-compose-orderer1.yaml root@$ORDERER1_IP:$CRYPTO_BASE
scp -r configtx.yaml root@$ORDERER1_IP:$CRYPTO_BASE
scp -r func.sh root@$ORDERER1_IP:$CRYPTO_BASE
ssh root@$ORDERER1_IP "
export CRYPTO_BASE=/root/cross;
cd $CRYPTO_BASE;
source func.sh;
echo '$CA_ORDERER_IP ca.cross.com
$PEER0_ORG1_IP peer0.org1.cross.com
$PEER0_ORG2_IP peer0.org2.cross.com' >> /etc/hosts;
create_orderer_org orderer1 cross.com 8054;
create_orderer orderer1 cross.com 8054;
"

mkdir -p organizations/ordererOrganizations/cross.com/orderers/orderer1.cross.com/tls
scp -r root@$ORDERER1_IP:$CRYPTO_BASE/organizations/ordererOrganizations/cross.com/orderers/orderer1.cross.com/tls/server.crt organizations/ordererOrganizations/cross.com/orderers/orderer1.cross.com/tls


ssh root@$CA_ORG1_IP "mkdir -p $CRYPTO_BASE;"
scp -r docker-compose-ca-org1.yaml root@$CA_ORG1_IP:$CRYPTO_BASE
scp -r func.sh root@$CA_ORG1_IP:$CRYPTO_BASE
ssh root@$CA_ORG1_IP "
export CRYPTO_BASE=/root/cross;
cd $CRYPTO_BASE;
source func.sh;
docker-compose -f docker-compose-ca-org1.yaml up -d;
"

mkdir -p organizations/fabric-ca/org1
scp -r root@$CA_ORG1_IP:$CRYPTO_BASE/organizations/fabric-ca/org1/tls-cert.pem organizations/fabric-ca/org1


ssh root@$PEER0_ORG1_IP "mkdir -p $CRYPTO_BASE/organizations/fabric-ca/org1;
mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/cross.com/tlsca;
mkdir -p $CRYPTO_BASE/scripts;
mkdir -p $CRYPTO_BASE/chaincode;"
scp -r organizations/fabric-ca/org1/tls-cert.pem root@$PEER0_ORG1_IP:$CRYPTO_BASE/organizations/fabric-ca/org1
scp -r organizations/ordererOrganizations/cross.com/tlsca/tlsca.cross.com-cert.pem root@$PEER0_ORG1_IP:$CRYPTO_BASE/organizations/ordererOrganizations/cross.com/tlsca
scp -r docker-compose-peer0-org1.yaml root@$PEER0_ORG1_IP:$CRYPTO_BASE
scp -r func.sh root@$PEER0_ORG1_IP:$CRYPTO_BASE
scp -r scripts/* root@$PEER0_ORG1_IP:$CRYPTO_BASE/scripts
scp -r chaincode/* root@$PEER0_ORG1_IP:$CRYPTO_BASE/chaincode
ssh root@$PEER0_ORG1_IP "
export CRYPTO_BASE=/root/cross;
cd $CRYPTO_BASE;
source func.sh;
echo '$CA_ORG1_IP ca.org1.cross.com
$ORDERER_IP orderer.cross.com' >> /etc/hosts;
create_org org1 cross.com 8054;
create_peer org1 peer0 cross.com 8054;
docker-compose -f docker-compose-peer0-org1.yaml up -d;
"

mkdir -p organizations/peerOrganizations/org1.cross.com
scp -r root@$PEER0_ORG1_IP:$CRYPTO_BASE/organizations/peerOrganizations/org1.cross.com/* organizations/peerOrganizations/org1.cross.com


ssh root@$CA_ORG2_IP "mkdir -p $CRYPTO_BASE;"
scp -r docker-compose-ca-org2.yaml root@$CA_ORG2_IP:$CRYPTO_BASE
scp -r func.sh root@$CA_ORG2_IP:$CRYPTO_BASE
ssh root@$CA_ORG2_IP "
export CRYPTO_BASE=/root/cross;
cd $CRYPTO_BASE;
source func.sh;
docker-compose -f docker-compose-ca-org2.yaml up -d;
"

mkdir -p organizations/fabric-ca/org2
scp -r root@$CA_ORG2_IP:$CRYPTO_BASE/organizations/fabric-ca/org2/tls-cert.pem organizations/fabric-ca/org2


ssh root@$PEER0_ORG2_IP "mkdir -p $CRYPTO_BASE/organizations/fabric-ca/org2;
mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/cross.com/tlsca;
mkdir -p $CRYPTO_BASE/scripts;
mkdir -p $CRYPTO_BASE/chaincode;"
scp -r organizations/fabric-ca/org2/tls-cert.pem root@$PEER0_ORG2_IP:$CRYPTO_BASE/organizations/fabric-ca/org2
scp -r organizations/ordererOrganizations/cross.com/tlsca/tlsca.cross.com-cert.pem root@$PEER0_ORG2_IP:$CRYPTO_BASE/organizations/ordererOrganizations/cross.com/tlsca
scp -r docker-compose-peer0-org2.yaml root@$PEER0_ORG2_IP:$CRYPTO_BASE
scp -r func.sh root@$PEER0_ORG2_IP:$CRYPTO_BASE
scp -r scripts/* root@$PEER0_ORG2_IP:$CRYPTO_BASE/scripts
scp -r chaincode/* root@$PEER0_ORG2_IP:$CRYPTO_BASE/chaincode
ssh root@$PEER0_ORG2_IP "
export CRYPTO_BASE=/root/cross;
cd $CRYPTO_BASE;
source func.sh;
echo '$CA_ORG2_IP ca.org2.cross.com
$ORDERER_IP orderer.cross.com' >> /etc/hosts;
create_org org2 cross.com 8054;
create_peer org2 peer0 cross.com 8054;
docker-compose -f docker-compose-peer0-org2.yaml up -d;
"

mkdir -p organizations/peerOrganizations/org2.cross.com
scp -r root@$PEER0_ORG2_IP:$CRYPTO_BASE/organizations/peerOrganizations/org2.cross.com/* organizations/peerOrganizations/org2.cross.com


scp -r organizations/peerOrganizations root@$ORDERER_IP:$CRYPTO_BASE/organizations
scp -r organizations/peerOrganizations root@$ORDERER1_IP:$CRYPTO_BASE/organizations
ssh root@$ORDERER_IP "mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/cross.com/orderers/orderer1.cross.com/tls;"
scp -r organizations/ordererOrganizations/cross.com/orderers/orderer1.cross.com/tls/server.crt root@$ORDERER_IP:$CRYPTO_BASE/organizations/ordererOrganizations/cross.com/orderers/orderer1.cross.com/tls
ssh root@$ORDERER_IP "
export CRYPTO_BASE=/root/cross;
cd $CRYPTO_BASE;
mkdir -p $CRYPTO_BASE/channel-artifacts
configtxgen -profile TwoOrgsOrdererGenesis -outputBlock $CRYPTO_BASE/channel-artifacts/orderer.genesis.block -channelID system-channel
configtxgen -profile TwoOrgsChannel -outputCreateChannelTx $CRYPTO_BASE/channel-artifacts/channel-1.tx -channelID channel-1
configtxgen -profile TwoOrgsChannel -outputAnchorPeersUpdate $CRYPTO_BASE/channel-artifacts/Org1MSPanchors.tx -channelID channel-1 -asOrg Org1MSP
configtxgen -profile TwoOrgsChannel -outputAnchorPeersUpdate $CRYPTO_BASE/channel-artifacts/Org2MSPanchors.tx -channelID channel-1 -asOrg Org2MSP

docker-compose -f docker-compose-orderer.yaml up -d;
"

mkdir -p channel-artifacts
scp -r root@$ORDERER_IP:$CRYPTO_BASE/channel-artifacts/* channel-artifacts
scp -r channel-artifacts/* root@$ORDERER1_IP:$CRYPTO_BASE/channel-artifacts

ssh root@$ORDERER1_IP "
export CRYPTO_BASE=/root/cross;
cd $CRYPTO_BASE;
docker-compose -f docker-compose-orderer1.yaml up -d;
"

sleep 30s
scp -r channel-artifacts/* root@$PEER0_ORG1_IP:$CRYPTO_BASE/channel-artifacts


ssh root@$PEER0_ORG1_IP "mkdir -p $CRYPTO_BASE/organizations/peerOrganizations/org2.cross.com/tlsca;"
scp -r root@$PEER0_ORG2_IP:$CRYPTO_BASE/organizations/peerOrganizations/org2.cross.com/tlsca/tlsca.org2.cross.com-cert.pem .
scp -r tlsca.org2.cross.com-cert.pem root@$PEER0_ORG1_IP:$CRYPTO_BASE/organizations/peerOrganizations/org2.cross.com/tlsca

ssh root@$PEER0_ORG1_IP "docker exec cross_cli /bin/bash -c 'cd /opt/gopath/src/github.com/hyperledger/fabric/peer/scripts && ./setup_org1.sh'"
scp -r root@$PEER0_ORG1_IP:$CRYPTO_BASE/channel-artifacts/* channel-artifacts
scp -r channel-artifacts/* root@$PEER0_ORG2_IP:$CRYPTO_BASE/channel-artifacts
ssh root@$PEER0_ORG2_IP "docker exec -i cross_cli /bin/bash -c 'cd /opt/gopath/src/github.com/hyperledger/fabric/peer/scripts && ./setup_org2.sh'"

ssh root@$PEER0_ORG1_IP "docker exec -i cross_cli /bin/bash -c 'cd /opt/gopath/src/github.com/hyperledger/fabric/peer/scripts && ./init_chaincode.sh'"
