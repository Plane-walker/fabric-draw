export LOCAL_CRYPTO_BASE=/root/opt
export CROSS_CRYPTO_BASE=/root/cross

mkdir -p local/org1.test.com
mkdir -p local/org1.test2.com
mkdir -p cross/org1.cross.com
mkdir -p cross/org2.cross.com

scp -r root@$GROUP1_PEER0_ORG1_IP:$LOCAL_CRYPTO_BASE/organizations/peerOrganizations/org1.test.com/* local/org1.test.com
cp scripts/local/connection-org1.yaml local/org1.test.com
sed -i "s/PEER0_ORG1_IP/$GROUP1_PEER0_ORG1_IP/g" local/org1.test.com/connection-org1.yaml
mv local/org1.test.com/users/Admin@org1.test.com/msp/keystore/* local/org1.test.com/users/Admin@org1.test.com/msp/keystore/sk
scp -r root@$GROUP1_PEER0_ORG1_IP:$CROSS_CRYPTO_BASE/organizations/peerOrganizations/org1.cross.com/* cross/org1.cross.com
cp scripts/cross/connection-org1.yaml cross/org1.cross.com
sed -i "s/PEER0_ORG1_IP/$GROUP1_PEER0_ORG1_IP/g" cross/org1.cross.com/connection-org1.yaml
mv cross/org1.cross.com/users/Admin@org1.cross.com/msp/keystore/* cross/org1.cross.com/users/Admin@org1.cross.com/msp/keystore/sk

scp -r root@$GROUP2_PEER0_ORG1_IP:$LOCAL_CRYPTO_BASE/organizations/peerOrganizations/org1.test2.com/* local/org1.test2.com
cp scripts/local/connection-org2.yaml local/org1.test2.com
sed -i "s/PEER0_ORG1_IP/$GROUP2_PEER0_ORG1_IP/g" local/org1.test2.com/connection-org2.yaml
mv local/org1.test2.com/users/Admin@org1.test2.com/msp/keystore/* local/org1.test2.com/users/Admin@org1.test2.com/msp/keystore/sk
scp -r root@$GROUP2_PEER0_ORG1_IP:$CROSS_CRYPTO_BASE/organizations/peerOrganizations/org2.cross.com/* cross/org2.cross.com
cp scripts/cross/connection-org2.yaml cross/org2.cross.com
sed -i "s/PEER0_ORG2_IP/$GROUP2_PEER0_ORG1_IP/g" cross/org2.cross.com/connection-org2.yaml
mv cross/org2.cross.com/users/Admin@org2.cross.com/msp/keystore/* cross/org2.cross.com/users/Admin@org2.cross.com/msp/keystore/sk
