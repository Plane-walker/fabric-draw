export CORE_ORDERER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/cross.com/tlsca/tlsca.cross.com-cert.pem
export CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.cross.com/users/Admin@org2.cross.com/msp
export CORE_PEER_ADDRESS=peer0.org2.cross.com:8051
export CORE_PEER_LOCALMSPID="Org2MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.cross.com/tlsca/tlsca.org2.cross.com-cert.pem
export CHANNEL_NAME=channel-1

cd /opt/gopath/src/github.com/hyperledger/fabric/peer
cp channel-artifacts/channel-1.block .
peer channel update -o orderer.cross.com:8050 -c $CHANNEL_NAME -f ./channel-artifacts/Org2MSPanchors.tx --tls --cafile $CORE_ORDERER_TLS_ROOTCERT_FILE
peer channel join -b channel-1.block

cd /opt/gopath/src/github.com/chaincode
peer lifecycle chaincode install crosscc.tar.gz
export CC_PACKAGE_ID=crosscc:5d97dea92766070d2669c4d4022f58514953f1d39dfe50749f1a2833c601b271
peer lifecycle chaincode approveformyorg -o orderer.cross.com:8050 --ordererTLSHostnameOverride orderer.cross.com --channelID channel-1 --name crosscc --version 1.0 --package-id $CC_PACKAGE_ID --sequence 1 --tls --cafile $CORE_ORDERER_TLS_ROOTCERT_FILE
