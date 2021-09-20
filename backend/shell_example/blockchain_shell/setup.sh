export GROUP1_CA_ORDERER_IP=47.105.115.125
export GROUP1_ORDERER_IP=118.190.158.73
export GROUP1_CA_ORG1_IP=47.104.158.207
export GROUP1_PEER0_ORG1_IP=47.104.193.209
export GROUP1_CA_ORG2_IP=47.104.29.109
export GROUP1_PEER0_ORG2_IP=47.104.221.234

export GROUP2_CA_ORDERER_IP=47.104.143.86
export GROUP2_ORDERER_IP=47.104.4.217
export GROUP2_CA_ORG1_IP=118.190.105.215
export GROUP2_PEER0_ORG1_IP=47.104.9.22
export GROUP2_CA_ORG2_IP=47.104.16.238
export GROUP2_PEER0_ORG2_IP=47.105.105.100


cp scripts/func.sh group1-shell
cp chaincode/* group1-shell/chaincode
cd group1-shell
sh setup.sh
cd ..
cp group1-shell/token group2-shell
cp scripts/func.sh group2-shell
cp chaincode/* group2-shell/chaincode
cd group2-shell
sh setup.sh
cd ..
cp scripts/func.sh cross-group-shell
cp chaincode/* cross-group-shell/chaincode
cd cross-group-shell
sh setup.sh
cd ..

sh scripts/attach.sh
