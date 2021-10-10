import yaml
import re
from ruamel.yaml import YAML


class YamlGenerator:
    def __init__(self):
        pass

    def generate(self, **kwargs):
        pass


class ConfigTXYamlGenerator:
    def __init__(self, net_name: str, crypto_base: str):
        self.yml = YAML()
        self.yml.indent(mapping=4, sequence=6, offset=4)
        self.crypto_base = crypto_base
        self.net_name = net_name
        self.configtx = None
        self.filename = ""
        
    def update_organizations(self, groups: dict, nodes: dict):
        Organizations = []
        for key in groups:
            elems = key.split(".")
            name = elems[0].capitalize()
            Organization = {}
            Organization["Name"] = name
            Organization["SkipAsForeign"] = False
            Organization["ID"] = name + "MSP"
            Organization["MSPDir"] = self.crypto_base + "/organizations/" + key + "/msp"
            if "order" in key:
                Organization["Policies"] = self.configtx["Organizations"][0]["Policies"]
                Organization["OrdererEndpoints"] = groups[key]["nodes"]["orderer"]
            else:
                Organization["Policies"] = self.configtx["Organizations"][1]["Policies"]
                Organization["AnchorPeers"] = []
                for url in groups[key]["nodes"]["anchor_peers"]:
                    Organization["AnchorPeers"].append({
                        "Host": url,
                        "Port": int(nodes[url]["address"]["fabric_port"])
                    })
            for Policie in Organization["Policies"]:
                Rule = Organization["Policies"][Policie]["Rule"]
                Organization["Policies"][Policie]["Rule"] = re.sub("Or\S+MSP", name, Rule)
            Organizations.append(Organization)
        self.configtx["Organizations"] = Organizations

    def update_orderer(self, orderers: dict):
        Orderer = self.configtx["Orderer"]
        Addresses = []
        Consenters = []
        for orderer in orderers:
            name = orderer.split(".")[0]
            Addresses.append(orderers[orderer]["address"]["host"] + ":" + orderers[orderer]["address"]["fabric_port"])
            Consenters.append({
                "Host": orderer,
                "Port": int(orderers[orderer]["address"]["fabric_port"]),
                "ClientTLSCert": self.crypto_base + "/organizations/" + ".".join(orderer.split(".")[-3:]) + "/peers/" + orderer + "/tls/server.crt",
                "ServerTLSCert": self.crypto_base + "/organizations/" + ".".join(orderer.split(".")[-3:]) + "/peers/" + orderer + "/tls/server.crt"
            })
        Orderer["Addresses"] = Addresses
        Orderer["EtcdRaft"]["Consenters"] = Consenters

    def update_profiles(self):
        OrdererGenesis = self.net_name + "OrdererGenesis"
        Channel = self.net_name + "Channel"
        Profiles = {
            OrdererGenesis: self.configtx["Profiles"]["TwoOrgsOrdererGenesis"],
            Channel: self.configtx["Profiles"]["TwoOrgsChannel"]
        }
        Profiles[OrdererGenesis]["Consortiums"]["SampleConsortium"]["Organizations"] = []
        Profiles[OrdererGenesis]["Orderer"]["Organizations"] = []
        Profiles[Channel]["Application"]["Organizations"] = []
        for org in self.configtx["Organizations"]:
            if "rder" not in org["Name"]:
                Profiles[OrdererGenesis]["Consortiums"]["SampleConsortium"]["Organizations"].append(org)
                Profiles[Channel]["Application"]["Organizations"].append(org)
            else:
                Profiles[OrdererGenesis]["Orderer"]["Organizations"].append(org)
        self.configtx["Profiles"] = Profiles
        
    def get_filename(self):
        return self.filename

    def input_from(self, filename: str):
        with open(filename) as file:
            self.configtx = self.yml.load(file)
        return self

    def output_to(self, filename: str):
        if not self.configtx:
            return None
        self.filename = filename
        with open(filename, 'w', encoding="utf-8") as file:
            self.yml.dump(self.configtx, file)
        return self

    def generate(self, groups: dict, nodes: dict, orderers: dict):
        if not self.configtx:
            return None
        self.update_organizations(groups, nodes)
        self.update_orderer(orderers)
        self.update_profiles()
        return self
        


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

    def generate(self, node_id, org_name, node_name, fabric_name, fabric_port, crypto_path):
        with open('template/docker-compose-orderer-template.yaml') as file:
            docker_yaml = yaml.load(file, Loader=yaml.Loader)
        docker_yaml['networks']['net']['external']['name'] = fabric_name
        order_information = docker_yaml['services']['orderer0.orderer.test.com']
        order_information['container_name'] = node_id
        order_information['environment'][2] = f'ORDERER_GENERAL_LISTENPORT={fabric_port}'
        order_information['environment'][5] = f'ORDERER_GENERAL_LOCALMSPID={org_name.capitalize()}MSP'
        order_information['volumes'][1] = f'{crypto_path}/organizations/orderer.test.com/peers/{node_id}/msp:/var/hyperledger/orderer/msp'
        order_information['volumes'][2] = f'{crypto_path}/organizations/orderer.test.com/peers/{node_id}/tls/:/var/hyperledger/orderer/tls'
        order_information['volumes'][3] = f'{node_id}:/var/hyperledger/production/orderer'
        order_information['ports'][0] = f'{fabric_port}:{fabric_port}'
        del docker_yaml['services']['orderer0.orderer.test.com']
        docker_yaml['services'][node_id] = order_information
        file_name = f'docker-compose-{org_name}-{node_name}.yaml'
        with open(file_name, 'w', encoding="utf-8") as file:
            yaml.dump(docker_yaml, file, Dumper=yaml.Dumper)
        with open(file_name, 'a') as file:
            file.write(f'volumes:\n  {node_id}:\n')
        return file_name


class PeerYamlGenerator(YamlGenerator):
    def __init__(self):
        super().__init__()

    def generate(self, node_id, fabric_name, fabric_port, crypto_path):
        node_name, org_name, domain = node_id.split('.', 2)
        with open('template/docker-compose-peer-template.yaml') as file:
            docker_yaml = yaml.load(file, Loader=yaml.Loader)
        docker_yaml['networks']['net']['external']['name'] = fabric_name
        peer_information = docker_yaml['services']['peer0.org1.test.com']
        peer_information['container_name'] = node_id
        peer_information['environment'][8] = f'CORE_PEER_ID={node_id}'
        peer_information['environment'][9] = f'CORE_PEER_ADDRESS={node_id}:{fabric_port}'
        peer_information['environment'][11] = f'CORE_PEER_CHAINCODEADDRESS={node_id}:7052'
        peer_information['environment'][14] = f'CORE_PEER_GOSSIP_EXTERNALENDPOINT={node_id}:{fabric_port}'
        peer_information['environment'][15] = f'CORE_PEER_LOCALMSPID={org_name.capitalize()}MSP'
        peer_information['volumes'][1] = f'{crypto_path}/organizations/{org_name}.{domain}/peers/{node_id}/msp:/etc/hyperledger/fabric/msp'
        peer_information['volumes'][2] = f'{crypto_path}/organizations/{org_name}.{domain}/peers/{node_id}/tls:/etc/hyperledger/fabric/tls'
        peer_information['volumes'][3] = f'{node_id}:/var/hyperledger/production'
        peer_information['ports'][0] = f'{fabric_port}:{fabric_port}'
        del docker_yaml['services']['peer0.org1.test.com']
        docker_yaml['services'][node_id] = peer_information
        file_name = f'docker-compose-{org_name}-{node_name}.yaml'
        with open(file_name, 'w', encoding="utf-8") as file:
            yaml.dump(docker_yaml, file, Dumper=yaml.Dumper)
        with open(file_name, 'a') as file:
            file.write(f'volumes:\n  {node_id}:\n')
        return file_name
