import yaml


class YamlGenerator:
    def __init__(self):
        pass

    def generate(self, **kwargs):
        pass


class ConfigTXYamlGenerator(YamlGenerator):
    def __init__(self):
        super().__init__()

    def generate(self):
        pass


class CAYamlGenerator(YamlGenerator):
    def __init__(self):
        super().__init__()

    def generate(self, node_id, org_name, fabric_name, fabric_port, crypto_path):
        with open('template/docker-compose-ca-template.yaml') as file:
            docker_yaml = yaml.load(file, Loader=yaml.Loader)
        docker_yaml['networks']['net']['external']['name'] = fabric_name
        ca_information = docker_yaml['services']['ca.org1.test.com']
        ca_information['environment'][1] = f'FABRIC_CA_SERVER_CA_NAME=ca-{org_name}'
        ca_information['environment'][3] = f'FABRIC_CA_SERVER_PORT={fabric_port}'
        ca_information['environment'][4] = f'FABRIC_CA_SERVER_CSR_HOSTS=localhost, {node_id}'
        ca_information['ports'][0] = f'{fabric_port}:{fabric_port}'
        ca_information['volumes'][0] = f'/root/opt/organizations/fabric-ca/{org_name}:/etc/hyperledger/fabric-ca-server'
        ca_information['container_name'] = node_id
        del docker_yaml['services']['ca.org1.test.com']
        docker_yaml['services'][node_id] = ca_information
        file_name = f'docker-compose-ca-{org_name}.yaml'
        with open(file_name, 'w', encoding="utf-8") as file:
            yaml.dump(docker_yaml, file, Dumper=yaml.Dumper)
        return file_name


class OrderYamlGenerator(YamlGenerator):
    def __init__(self):
        super().__init__()

    def generate(self, node_id, org_name, node_name):
        with open('template/docker-compose-orderer-template.yaml') as file:
            docker_yaml = yaml.load(file, Loader=yaml.Loader)
        order_information = docker_yaml['services']['orderer0.orderer.test.com']
        order_information['container_name'] = node_id
        order_information['environment'][5] = f'ORDERER_GENERAL_LOCALMSPID={org_name.capitalize()}MSP'
        order_information['volumes'][1] = f'/root/opt/organizations/orderer.test.com/orderers/{node_id}/msp:/var/hyperledger/orderer/msp'
        order_information['volumes'][2] = f'/root/opt/organizations/orderer.test.com/orderers/{node_id}/tls/:/var/hyperledger/orderer/tls'
        order_information['volumes'][3] = f'{node_id}:/var/hyperledger/production/orderer'
        del docker_yaml['services']['orderer0.orderer.test.com']
        docker_yaml['services'][node_id] = order_information
        file_name = f'docker-compose-{org_name}-{node_name}.yaml'
        with open(file_name, 'w', encoding="utf-8") as file:
            yaml.dump(docker_yaml, file, Dumper=yaml.Dumper)
        return file_name


class PeerYamlGenerator(YamlGenerator):
    def __init__(self):
        super().__init__()

    def generate(self, node_id, org_name, node_name):
        with open('template/docker-compose-peer-template.yaml') as file:
            docker_yaml = yaml.load(file, Loader=yaml.Loader)
        peer_information = docker_yaml['services']['peer0.org1.test.com']
        peer_information['container_name'] = node_id
        peer_information['environment'][8] = f'CORE_PEER_ID={node_id}'
        peer_information['environment'][9] = f'CORE_PEER_ADDRESS={node_id}:7051'
        peer_information['environment'][11] = f'CORE_PEER_CHAINCODEADDRESS={node_id}:7052'
        peer_information['environment'][14] = f'CORE_PEER_GOSSIP_EXTERNALENDPOINT={node_id}:7051'
        peer_information['environment'][15] = f'CORE_PEER_LOCALMSPID={org_name.capitalize()}MSP'
        peer_information['volumes'][1] = f'/root/opt/organizations/org1.test.com/peers/{node_id}/msp:/etc/hyperledger/fabric/msp'
        peer_information['volumes'][2] = f'/root/opt/organizations/org1.test.com/peers/{node_id}/tls:/etc/hyperledger/fabric/tls'
        peer_information['volumes'][3] = f'{node_id}:/var/hyperledger/production'
        del docker_yaml['services']['peer0.org1.test.com']
        docker_yaml['services'][node_id] = peer_information
        file_name = f'docker-compose-{org_name}-{node_name}.yaml'
        with open(file_name, 'w', encoding="utf-8") as file:
            yaml.dump(docker_yaml, file, Dumper=yaml.Dumper)
        return file_name
