export CORE_ORDERER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/test.com/tlsca/tlsca.test.com-cert.pem
export CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.test.com/users/Admin@org1.test.com/msp
export CORE_PEER_ADDRESS=peer0.org1.test.com:7051
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.test.com/tlsca/tlsca.org1.test.com-cert.pem
export CHANNEL_NAME=channel-1

cd /opt/gopath/src/github.com/hyperledger/fabric/peer
peer channel create -o orderer.test.com:7050 -c $CHANNEL_NAME -f ./channel-artifacts/channel-1.tx --tls --cafile $CORE_ORDERER_TLS_ROOTCERT_FILE
peer channel update -o orderer.test.com:7050 -c $CHANNEL_NAME -f ./channel-artifacts/Org1MSPanchors.tx --tls --cafile $CORE_ORDERER_TLS_ROOTCERT_FILE
peer channel join -b channel-1.block
cp channel-1.block channel-artifacts

cd /opt/gopath/src/github.com/chaincode
peer lifecycle chaincode install patcc.tar.gz
export CC_PACKAGE_ID=patcc:71464126290a7ff4792085aac22a139b08d543365278c6f2e3277ba28a4e5466
peer lifecycle chaincode approveformyorg -o orderer.test.com:7050 --ordererTLSHostnameOverride orderer.test.com --channelID channel-1 --name patcc --version 1.0 --package-id $CC_PACKAGE_ID --sequence 1 --tls --cafile $CORE_ORDERER_TLS_ROOTCERT_FILE

peer lifecycle chaincode install doccc.tar.gz
export CC_PACKAGE_ID=doccc:e59178c6bd813bfe95fd200b8eb4ffef159ba29b899f9cede1b1cfe24b1b97b7
peer lifecycle chaincode approveformyorg -o orderer.test.com:7050 --ordererTLSHostnameOverride orderer.test.com --channelID channel-1 --name doccc --version 1.0 --package-id $CC_PACKAGE_ID --sequence 1 --tls --cafile $CORE_ORDERER_TLS_ROOTCERT_FILE

peer lifecycle chaincode install pdcc.tar.gz
export CC_PACKAGE_ID=pdcc:621c6b37b25d3dd9fe0c04df71609becc10a7005482fc85bd8a337d27bb62ee6
peer lifecycle chaincode approveformyorg -o orderer.test.com:7050 --ordererTLSHostnameOverride orderer.test.com --channelID channel-1 --name pdcc --version 1.0 --package-id $CC_PACKAGE_ID --sequence 1 --tls --cafile $CORE_ORDERER_TLS_ROOTCERT_FILE

