import subprocess
import os
import grpc


class Node:
    def __init__(self, address, node_type, ct_result, ct_uid, fellow_list):
        self.address = address
        self.node_type = node_type
        self.ct_result = ct_result
        self.ct_uid = ct_uid
        self.fellow_list = fellow_list
        self.crypto_base = '/root/opt'

    def init_swarm(self):
        command = ['docker', 'swarm', 'init', '--advertise-addr', self.address.host, '--data-path-port', '5789']
        subprocess.run(command, stdout=subprocess.PIPE)
        command = 'docker swarm join-token -q manager'
        token = subprocess.run(command, shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
        command = ['docker', 'network', 'create', '--attachable', '--driver', 'overlay', 'root_test']
        subprocess.run(command, stdout=subprocess.PIPE)
        return token

    def join_swarm(self, token, address):
        command = ['docker', 'swarm', 'join', '--token', token, address, '--advertise-addr', self.address.host]
        subprocess.run(command, stdout=subprocess.PIPE)

    def init_container(self, node_type):
        command = ['docker-compose', '-f', 'docker-compose-' + node_type + '.yaml', 'up', '-d']
        env = os.environ.copy()
        env['CRYPTO_BASE'] = self.crypto_base
        subprocess.run(command, cwd=self.crypto_base, env=env, stdout=subprocess.PIPE)

    def generate_org_msp(self, org_seq):
        env = os.environ.copy()
        env['CRYPTO_BASE'] = self.crypto_base
        env['ORG_NAME'] = 'org' + str(org_seq)
        env['ORG_DOMAIN'] = 'test.com'
        env['CA_PORT'] = '7054'
        env['FABRIC_CA_CLIENT_HOME'] = env['CRYPTO_BASE'] + '/organizations/peerOrganizations/' + env['ORG_NAME'] + '.' + env['ORG_DOMAIN']
        env['CA_TLS_CA'] = env['CRYPTO_BASE'] + '/organizations/fabric-ca/' + env['ORG_NAME'] + '/tls-cert.pem'
        command = 'mkdir -p $FABRIC_CA_CLIENT_HOME'
        subprocess.run(command, shell=True, env=env, stdout=subprocess.PIPE)
        command = 'fabric-ca-client enroll -u https://admin:adminpw@ca.${ORG_NAME}.${ORG_DOMAIN}:${CA_PORT} --caname ca-${ORG_NAME} --tls.certfiles $CA_TLS_CA'
        subprocess.run(command, shell=True, env=env, stdout=subprocess.PIPE)
        config = 'NodeOUs:\n' \
            '  Enable: true\n' \
            '  ClientOUIdentifier:\n' \
            '    Certificate: cacerts/localhost-${CA_PORT}-ca-${ORG_NAME}.pem\n' \
            '    OrganizationalUnitIdentifier: client\n' \
            '  PeerOUIdentifier:\n' \
            '    Certificate: cacerts/localhost-${CA_PORT}-ca-${ORG_NAME}.pem\n' \
            '    OrganizationalUnitIdentifier: peer\n' \
            '  AdminOUIdentifier:\n' \
            '    Certificate: cacerts/localhost-${CA_PORT}-ca-${ORG_NAME}.pem\n' \
            '    OrganizationalUnitIdentifier: admin\n' \
            '  OrdererOUIdentifier:\n' \
            '    Certificate: cacerts/localhost-${CA_PORT}-ca-${ORG_NAME}.pem\n' \
            '    OrganizationalUnitIdentifier: orderer'
        command = 'echo ' + config + ' >> $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/msp/config.yaml'
        subprocess.run(command, shell=True, env=env, stdout=subprocess.PIPE)
        command = 'cp $CRYPTO_BASE/organizations/peerOrganizations/$ORG_NAME.$ORG_DOMAIN/msp/cacerts/* $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/msp/cacerts/localhost-${CA_PORT}-ca-${ORG_NAME}.pem'
        subprocess.run(command, shell=True, env=env, stdout=subprocess.PIPE)

    def generate_peer_msp(self, org_seq, peer_seq):
        env = os.environ.copy()
        env['CRYPTO_BASE'] = self.crypto_base
        env['ORG_NAME'] = 'org' + str(org_seq)
        env['PEER_NAME'] = 'peer' + str(peer_seq)
        env['ORG_DOMAIN'] = 'test.com'
        env['CA_PORT'] = '7054'
        env['FABRIC_CA_CLIENT_HOME'] = env['CRYPTO_BASE'] + '/organizations/peerOrganizations/' + env['ORG_NAME'] + '.' + env['ORG_DOMAIN']
        env['CA_TLS_CA'] = env['CRYPTO_BASE'] + '/organizations/fabric-ca/' + env['ORG_NAME'] + '/tls-cert.pem'
        command = 'mkdir -p $FABRIC_CA_CLIENT_HOME/peers/${PEER_NAME}.${ORG_NAME}.${ORG_DOMAIN};' \
                  'fabric-ca-client register --caname ca-${ORG_NAME} --id.name $PEER_NAME --id.secret ${PEER_NAME}pw --id.type peer --tls.certfiles $CA_TLS_CA;' \
                  'fabric-ca-client enroll -u https://${PEER_NAME}:${PEER_NAME}pw@ca.${ORG_NAME}.${ORG_DOMAIN}:${CA_PORT} --caname ca-${ORG_NAME} -M $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/peers/${PEER_NAME}.${ORG_NAME}.${ORG_DOMAIN}/msp --csr.hosts ${PEER_NAME}.${ORG_NAME}.${ORG_DOMAIN} --tls.certfiles $CA_TLS_CA;' \
                  'cp $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/peers/${PEER_NAME}.${ORG_NAME}.${ORG_DOMAIN}/msp/cacerts/* $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/peers/${PEER_NAME}.${ORG_NAME}.${ORG_DOMAIN}/msp/cacerts/localhost-${CA_PORT}-ca-${ORG_NAME}.pem;' \
                  'fabric-ca-client enroll -u https://${PEER_NAME}:${PEER_NAME}pw@ca.${ORG_NAME}.${ORG_DOMAIN}:${CA_PORT} --caname ca-${ORG_NAME} -M $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/peers/${PEER_NAME}.${ORG_NAME}.${ORG_DOMAIN}/tls --enrollment.profile tls --csr.hosts ${PEER_NAME}.${ORG_NAME}.${ORG_DOMAIN} --csr.hosts localhost --tls.certfiles $CA_TLS_CA;' \
                  'cp $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/msp/config.yaml $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/peers/${PEER_NAME}.${ORG_NAME}.${ORG_DOMAIN}/msp/config.yaml;' \
                  'cp $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/peers/${PEER_NAME}.${ORG_NAME}.${ORG_DOMAIN}/tls/tlscacerts/* $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/peers/${PEER_NAME}.${ORG_NAME}.${ORG_DOMAIN}/tls/ca.crt;' \
                  'cp $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/peers/${PEER_NAME}.${ORG_NAME}.${ORG_DOMAIN}/tls/signcerts/* $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/peers/${PEER_NAME}.${ORG_NAME}.${ORG_DOMAIN}/tls/server.crt;' \
                  'cp $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/peers/${PEER_NAME}.${ORG_NAME}.${ORG_DOMAIN}/tls/keystore/* $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/peers/${PEER_NAME}.${ORG_NAME}.${ORG_DOMAIN}/tls/server.key;' \
                  'mkdir -p $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/users/Admin@${ORG_NAME}.${ORG_DOMAIN};' \
                  'fabric-ca-client register --caname ca-${ORG_NAME} --id.name ${ORG_NAME}admin --id.secret ${ORG_NAME}adminpw --id.type admin --tls.certfiles $CA_TLS_CA;' \
                  'fabric-ca-client enroll -u https://${ORG_NAME}admin:${ORG_NAME}adminpw@ca.${ORG_NAME}.${ORG_DOMAIN}:${CA_PORT} --caname ca-${ORG_NAME} -M $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/users/Admin@${ORG_NAME}.${ORG_DOMAIN}/msp --tls.certfiles $CA_TLS_CA;' \
                  'cp $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/users/Admin@${ORG_NAME}.${ORG_DOMAIN}/msp/cacerts/* $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/users/Admin@${ORG_NAME}.${ORG_DOMAIN}/msp/cacerts/localhost-${CA_PORT}-ca-${ORG_NAME}.pem;' \
                  'cp $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/msp/config.yaml $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/users/Admin@${ORG_NAME}.${ORG_DOMAIN}/msp/config.yaml;' \
                  'mkdir -p $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/msp/tlscacerts;' \
                  'cp $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/peers/${PEER_NAME}.${ORG_NAME}.${ORG_DOMAIN}/tls/tlscacerts/* $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/msp/tlscacerts/ca.crt;' \
                  'mkdir -p $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/tlsca;' \
                  'cp $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/peers/${PEER_NAME}.${ORG_NAME}.${ORG_DOMAIN}/tls/tlscacerts/* $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/tlsca/tlsca.${ORG_NAME}.${ORG_DOMAIN}-cert.pem;' \
                  'mkdir -p $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/ca;' \
                  'cp $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/peers/${PEER_NAME}.${ORG_NAME}.${ORG_DOMAIN}/msp/cacerts/* $CRYPTO_BASE/organizations/peerOrganizations/${ORG_NAME}.${ORG_DOMAIN}/ca'
        subprocess.run(command, shell=True, env=env, stdout=subprocess.PIPE)

    def generate_orderer_org_msp(self):
        env = os.environ.copy()
        env['CRYPTO_BASE'] = self.crypto_base
        env['ORG_NAME'] = 'orderer'
        env['ORG_DOMAIN'] = 'test.com'
        env['CA_PORT'] = '7054'
        env['FABRIC_CA_CLIENT_HOME'] = env['CRYPTO_BASE'] + '/organizations/ordererOrganizations/' + env['ORG_DOMAIN']
        env['CA_TLS_CA'] = env['CRYPTO_BASE'] + '/organizations/fabric-ca/ordererOrg/tls-cert.pem'
        command = 'fabric-ca-client enroll -u https://admin:adminpw@ca.${ORG_DOMAIN}:${CA_PORT} --caname ca-${ORG_NAME} --tls.certfiles $CA_TLS_CA'
        subprocess.run(command, shell=True, env=env, stdout=subprocess.PIPE)
        config = 'NodeOUs:\n' \
                 '  Enable: true\n' \
                 '  ClientOUIdentifier:\n' \
                 '    Certificate: cacerts/localhost-${CA_PORT}-ca-${ORG_NAME}.pem\n' \
                 '    OrganizationalUnitIdentifier: client\n' \
                 '  PeerOUIdentifier:\n' \
                 '    Certificate: cacerts/localhost-${CA_PORT}-ca-${ORG_NAME}.pem\n' \
                 '    OrganizationalUnitIdentifier: peer\n' \
                 '  AdminOUIdentifier:\n' \
                 '    Certificate: cacerts/localhost-${CA_PORT}-ca-${ORG_NAME}.pem\n' \
                 '    OrganizationalUnitIdentifier: admin\n' \
                 '  OrdererOUIdentifier:\n' \
                 '    Certificate: cacerts/localhost-${CA_PORT}-ca-${ORG_NAME}.pem\n' \
                 '    OrganizationalUnitIdentifier: orderer'
        command = 'echo ' + config + ' >> $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/msp/config.yaml'
        subprocess.run(command, shell=True, env=env, stdout=subprocess.PIPE)
        command = 'cp $CRYPTO_BASE/organizations/ordererOrganizations/$ORG_DOMAIN/msp/cacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/msp/cacerts/localhost-${CA_PORT}-ca-${ORG_NAME}.pem'
        subprocess.run(command, shell=True, env=env, stdout=subprocess.PIPE)

    def generate_orderer_peer_msp(self, peer_seq):
        env = os.environ.copy()
        env['CRYPTO_BASE'] = self.crypto_base
        env['PEER_NAME'] = 'orderer' + str(peer_seq)
        env['ORG_DOMAIN'] = 'test.com'
        env['CA_PORT'] = '7054'
        env['FABRIC_CA_CLIENT_HOME'] = env['CRYPTO_BASE'] + '/organizations/ordererOrganizations/' + env['ORG_DOMAIN']
        env['CA_TLS_CA'] = env['CRYPTO_BASE'] + '/organizations/fabric-ca/ordererOrg/tls-cert.pem'
        command = 'mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/orderers/${PEER_NAME}.${ORG_DOMAIN};' \
                  'fabric-ca-client register --caname ca-orderer --id.name ${PEER_NAME} --id.secret ${PEER_NAME}pw --id.type orderer --tls.certfiles $CA_TLS_CA;' \
                  'fabric-ca-client enroll -u https://${PEER_NAME}:${PEER_NAME}pw@ca.${ORG_DOMAIN}:${CA_PORT} --caname ca-orderer -M $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/orderers/${PEER_NAME}.${ORG_DOMAIN}/msp --csr.hosts ${PEER_NAME}.${ORG_DOMAIN} --tls.certfiles $CA_TLS_CA;' \
                  'cp $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/orderers/${PEER_NAME}.${ORG_DOMAIN}/msp/cacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/orderers/${PEER_NAME}.${ORG_DOMAIN}/msp/cacerts/localhost-${CA_PORT}-ca-${PEER_NAME}.pem;' \
                  'fabric-ca-client enroll -u https://${PEER_NAME}:${PEER_NAME}pw@ca.${ORG_DOMAIN}:${CA_PORT} --caname ca-orderer -M $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/orderers/${PEER_NAME}.${ORG_DOMAIN}/tls --enrollment.profile tls --csr.hosts ${PEER_NAME}.${ORG_DOMAIN} --csr.hosts localhost --tls.certfiles $CA_TLS_CA;' \
                  'cp $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/msp/config.yaml $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/orderers/${PEER_NAME}.${ORG_DOMAIN}/msp/config.yaml;' \
                  'cp $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/orderers/${PEER_NAME}.${ORG_DOMAIN}/tls/tlscacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/orderers/${PEER_NAME}.${ORG_DOMAIN}/tls/ca.crt;' \
                  'cp $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/orderers/${PEER_NAME}.${ORG_DOMAIN}/tls/signcerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/orderers/${PEER_NAME}.${ORG_DOMAIN}/tls/server.crt;' \
                  'cp $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/orderers/${PEER_NAME}.${ORG_DOMAIN}/tls/keystore/* $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/orderers/${PEER_NAME}.${ORG_DOMAIN}/tls/server.key;' \
                  'mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/users/Admin@${ORG_DOMAIN};' \
                  'fabric-ca-client register --caname ca-orderer --id.name ${PEER_NAME}admin --id.secret ${PEER_NAME}adminpw --id.type admin --tls.certfiles $CA_TLS_CA;' \
                  'fabric-ca-client enroll -u https://ordereradmin:ordereradminpw@ca.${ORG_DOMAIN}:${CA_PORT} --caname ca-orderer -M $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/users/Admin@${ORG_DOMAIN}/msp --tls.certfiles $CA_TLS_CA;' \
                  'cp $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/users/Admin@${ORG_DOMAIN}/msp/cacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/users/Admin@${ORG_DOMAIN}/msp/cacerts/localhost-${CA_PORT}-ca-${PEER_NAME}.pem;' \
                  'cp $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/msp/config.yaml $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/users/Admin@${ORG_DOMAIN}/msp/config.yaml;' \
                  'mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/msp/tlscacerts;' \
                  'cp $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/orderers/${PEER_NAME}.${ORG_DOMAIN}/tls/tlscacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/msp/tlscacerts/ca.crt;' \
                  'mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/tlsca;' \
                  'cp $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/orderers/${PEER_NAME}.${ORG_DOMAIN}/tls/tlscacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/tlsca/tlsca.${ORG_DOMAIN}-cert.pem;' \
                  'mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/ca;' \
                  'cp $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/orderers/${PEER_NAME}.${ORG_DOMAIN}/msp/cacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/ca;' \
                  'mkdir -p $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/orderers/${PEER_NAME}.${ORG_DOMAIN}/msp/tlscacerts;' \
                  'cp $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/orderers/${PEER_NAME}.${ORG_DOMAIN}/tls/tlscacerts/* $CRYPTO_BASE/organizations/ordererOrganizations/${ORG_DOMAIN}/orderers/${PEER_NAME}.${ORG_DOMAIN}/msp/tlscacerts/tlsca.${ORG_DOMAIN}-cert.pem'
        subprocess.run(command, shell=True, env=env, stdout=subprocess.PIPE)

    def generate_docker_compose_file(self, file_type):
        pass

    def init_ca_orderer(self):
        self.generate_docker_compose_file('ca_orderer')
        self.init_container('ca_orderer')

    def init_orderer_peer(self):
        if
        self.
        self.generate_docker_compose_file('orderer')
        self.init_container('ca_orderer')

    def init_ca(self):
        pass

    def init_peer(self):
        pass

    def run(self):
        if self.node_type == 'leader':
            if 'ca-orderer' in self.fellow_list:
                channel = grpc.insecure_channel('localhost:1453')
                client = node_pb2_grpc.NodeStub(channel=channel)
            # generate peer





if __name__ == '__main__':
    pass
