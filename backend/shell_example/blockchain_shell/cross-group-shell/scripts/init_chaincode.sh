export CORE_ORDERER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/cross.com/tlsca/tlsca.cross.com-cert.pem
export CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.cross.com/users/Admin@org1.cross.com/msp
export CORE_PEER_ADDRESS=peer0.org1.cross.com:8051
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.cross.com/tlsca/tlsca.org1.cross.com-cert.pem
export CHANNEL_NAME=channel-1

cd /opt/gopath/src/github.com/hyperledger/fabric/peer
peer lifecycle chaincode commit -o orderer.cross.com:8050 --ordererTLSHostnameOverride orderer.cross.com --channelID channel-1 --name crosscc --version 1.0 --sequence 1 --tls --cafile $CORE_ORDERER_TLS_ROOTCERT_FILE --peerAddresses peer0.org1.cross.com:8051 --tlsRootCertFiles $CORE_PEER_TLS_ROOTCERT_FILE --peerAddresses peer0.org2.cross.com:8051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.cross.com/tlsca/tlsca.org2.cross.com-cert.pem
# peer chaincode invoke -o orderer.cross.com:8050 --ordererTLSHostnameOverride orderer.cross.com --tls --cafile $CORE_ORDERER_TLS_ROOTCERT_FILE -C channel-1 -n ecgcc --peerAddresses peer0.org1.cross.com:8051 --tlsRootCertFiles $CORE_PEER_TLS_ROOTCERT_FILE --peerAddresses peer0.org2.cross.com:8051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.cross.com/tlsca/tlsca.org2.cross.com-cert.pem -c '{"function":"createAccount","Args":["user0", "publicKey", "hello world"]}'
