import paramiko
import time
import io
import os
from yaml_generator import CAYamlGenerator, OrderYamlGenerator, PeerYamlGenerator


def generate_ca(ca_id, ca_information, fabric_name, target_host, crypto_base):
    node_name, group_name, domain = ca_id.split('.', 2)
    address = ca_information['address']
    key_file = io.StringIO(address['sk'])
    private_key = paramiko.RSAKey.from_private_key(key_file)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=address['host'], port=address['ssh_port'], username='root', pkey=private_key)
    stdin, stdout, stderr = ssh.exec_command(f'if [ ! -d {crypto_base} ]; then mkdir -p {crypto_base}; fi')
    stdout.channel.recv_exit_status()
    ftp_client = ssh.open_sftp()
    file_name = 'node_build.py'
    ftp_client.put(file_name, f'{crypto_base}/{file_name}')
    if group_name == 'orderer':
        stdin, stdout, stderr = ssh.exec_command(f'python {crypto_base}/node_build.py --func_name init_docker_swarm {target_host} {fabric_name} {crypto_base}')
        stdout.channel.recv_exit_status()
        ftp_client.get(f'{crypto_base}/token', 'token')
    else:
        try:
            ftp_client.stat(f'{crypto_base}/token')
        except IOError:
            node_host = address['host']
            ftp_client.put('token', f'{crypto_base}/token')
            stdin, stdout, stderr = ssh.exec_command(f'python {crypto_base}/node_build.py --func_name join_docker_swarm {node_host} {target_host} {crypto_base}')
            stdout.channel.recv_exit_status()
    ca_yaml_generator = CAYamlGenerator()
    file_name = ca_yaml_generator.generate(ca_id, group_name, fabric_name, address['fabric_port'], crypto_base)
    ftp_client.put(file_name, f'{crypto_base}/{file_name}')
    stdin, stdout, stderr = ssh.exec_command(f'docker-compose -f {crypto_base}/{file_name} up -d')
    stdout.channel.recv_exit_status()
    time.sleep(5)
    tls_cert_path = f'organizations/fabric-ca/{group_name}'
    if not os.path.exists(tls_cert_path):
        os.makedirs(tls_cert_path)
    ftp_client.get(f'{crypto_base}/{tls_cert_path}/tls-cert.pem', f'{tls_cert_path}/tls-cert.pem')
    ftp_client.close()
    ssh.close()


def generate_order_msp(order_id, order_information, ca_port, crypto_base):
    node_name, group_name, domain = order_id.split('.', 2)
    address = order_information['address']
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_file = io.StringIO(address['sk'])
    private_key = paramiko.RSAKey.from_private_key(key_file)
    ssh.connect(hostname=address['host'], port=address['ssh_port'], username='root', pkey=private_key)
    tls_cert_path = f'organizations/fabric-ca/{group_name}'
    stdin, stdout, stderr = ssh.exec_command(f'if [ ! -d {crypto_base}/{tls_cert_path} ]; then mkdir -p {crypto_base}/{tls_cert_path}; fi')
    stdout.channel.recv_exit_status()
    ftp_client = ssh.open_sftp()
    ftp_client.put(f'{tls_cert_path}/tls-cert.pem', f'{crypto_base}/{tls_cert_path}/tls-cert.pem')
    file_name = 'node_build.py'
    ftp_client.put(file_name, f'{crypto_base}/{file_name}')
    stdin, stdout, stderr = ssh.exec_command(f'python {crypto_base}/node_build.py --func_name org_msp_generate {group_name} {domain} {ca_port} {crypto_base}')
    stdout.channel.recv_exit_status()
    # print(stdout.readlines(), stderr.readlines())
    stdin, stdout, stderr = ssh.exec_command(f'python {crypto_base}/node_build.py --func_name peer_msp_generate {node_name} {group_name} {domain} {ca_port} {crypto_base}')
    stdout.channel.recv_exit_status()
    # print(stdout.readlines(), stderr.readlines())
    tls_ca_path = f'organizations/{group_name}.{domain}/tlsca'
    if not os.path.exists(tls_ca_path):
        os.makedirs(tls_ca_path)
    ftp_client.get(f'{crypto_base}/{tls_ca_path}/tlsca.{group_name}.{domain}-cert.pem', f'{tls_ca_path}/tlsca.{group_name}.{domain}-cert.pem')
    server_path = f'organizations/{group_name}.{domain}/peers/{order_id}/tls'
    if not os.path.exists(server_path):
        os.makedirs(server_path)
    ftp_client.get(f'{crypto_base}/{server_path}/server.crt', f'{server_path}/server.crt')
    ftp_client.close()


def generate_peer(peer_id, peer_information, order_group_id, crypto_base='/root/opt'):
    node_name, group_name, domain = peer_id.split('.', 2)
    order_group_name, order_domain = order_group_id.split('.', 1)
    address = peer_information['address']
    node_port = address['port']
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_file = io.StringIO(address['sk'])
    private_key = paramiko.RSAKey.from_private_key(key_file)
    ssh.connect(hostname=address['host'], port=address['ssh_port'], username='root', pkey=private_key)
    tls_cert_path = f'organizations/fabric-ca/{group_name}'
    ssh.exec_command(f'if [ ! -d {crypto_base}/{tls_cert_path} ]; then mkdir -p {crypto_base}/{tls_cert_path}; fi')
    ftp_client = ssh.open_sftp()
    ftp_client.put(f'{tls_cert_path}/tls-cert.pem', f'{crypto_base}/{tls_cert_path}')
    tls_ca_path = f'organizations/{order_group_name}.{order_domain}/tlsca'
    ssh.exec_command(f'if [ ! -d {crypto_base}/{tls_ca_path} ]; then mkdir -p {crypto_base}/{tls_ca_path}; fi')
    ftp_client.put(f'{tls_ca_path}/tlsca.{order_group_name}.{order_domain}-cert.pem', f'{crypto_base}/{tls_ca_path}')
    file_name = 'node_build.py'
    ftp_client.put(file_name, f'{crypto_base}/{file_name}')
    peer_yaml_generator = PeerYamlGenerator()
    file_name = peer_yaml_generator.generate(peer_id, group_name, node_name)
    ftp_client.put(file_name, f'{crypto_base}/{file_name}')
    ssh.exec_command(f'python node_build.py --func_name org_msp_generate {group_name} {domain} {node_port} {crypto_base}')
    ssh.exec_command(f'python node_build.py --func_name peer_msp_generate {node_name} {group_name} {domain} {node_port} {crypto_base}')
    ssh.exec_command(f'python node_build.py --func_name docker_compose {file_name}')
    peer_path = f'organizations/{group_name}.{domain}'
    if not os.path.exists(peer_path):
        os.makedirs(peer_path)
    # ftp_client.get(f'{crypto_base}/{tls_ca_path}/tlsca.{group_name}.{domain}-cert.pem', tls_ca_path)
    ftp_client.close()


def generate_order(order_id, order_information, fabric_name, channel_id, peer_group_ids, crypto_base='/root/opt'):
    node_name, group_name, domain = order_id.split('.', 2)
    address = order_information['address']
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_file = io.StringIO(address['sk'])
    private_key = paramiko.RSAKey.from_private_key(key_file)
    ssh.connect(hostname=address['host'], port=address['ssh_port'], username='root', pkey=private_key)
    ssh.exec_command(f'if [ ! -d {crypto_base}/channel-artifacts ]; then mkdir -p {crypto_base}/channel-artifacts; fi')
    ssh.exec_command(f'python node_build.py --func_name init_channel_artifacts {fabric_name} {channel_id} {peer_group_ids} "{crypto_base}"')


def parse_json(network_topology_json):
    order_group_id = ''
    order_ca_port = ''
    target_host = ''
    peer_group_ids = []
    peer_ca_port = []
    for group_id, group_information in network_topology_json['groups'].items():
        if group_id.split('.', 1)[0] == 'orderer':
            order_group_id = group_id
            order_ca_port = network_topology_json['nodes'][group_information['nodes']['ca']]['address']['fabric_port']
            target_host = network_topology_json['nodes'][network_topology_json['groups'][group_id]['nodes']['ca']]['address']['host']
        else:
            peer_group_ids.append(group_id)
            peer_ca_port.append(network_topology_json['nodes'][group_information['nodes']['ca']]['address']['fabric_port'])
        generate_ca(group_information['nodes']['ca'], network_topology_json['nodes'][group_information['nodes']['ca']], network_topology_json['blockchains']['fabric-1']['name'], target_host, '/root/opt')
    for order_id in network_topology_json['groups'][order_group_id]['nodes']['orderer']:
        generate_order_msp(order_id, network_topology_json['nodes'][order_id], order_ca_port, '/root/opt')
    # for org_id in peer_group_ids:
    #     leader_peers_ids = network_topology_json['groups'][org_id]['nodes']['leader_peers']
    #     anchor_peers_ids = network_topology_json['groups'][org_id]['nodes']['anchor_peers']
    #     committing_peers_ids = network_topology_json['groups'][org_id]['nodes']['committing_peers']
    #     endorsing_peers_ids = network_topology_json['groups'][org_id]['nodes']['endorsing_peers']
    #     peer_ids = list(set(leader_peers_ids).union(set(anchor_peers_ids).union(set(committing_peers_ids)).union(set(endorsing_peers_ids))))
    #     for peer_id in peer_ids:
    #         generate_peer(peer_id, network_topology_json['nodes'][peer_id], order_group_id)
    # for order_id in network_topology_json['groups'][order_group_id]['nodes']['orderer']:
    #     generate_order(order_id, network_topology_json['nodes'][order_id], network_topology_json['blockchains']['fabric-1']['name'], network_topology_json['blockchains']['fabric-1']['channels'][0], peer_group_ids)


if __name__ == '__main__':
    network_json = {
        "groups": {
            "orderer.test.com": {
                "nodes": {
                    "ca": "ca.orderer.test.com",
                    "orderer": ["orderer0.orderer.test.com", "orderer1.orderer.test.com", "orderer2.orderer.test.com"]
                },
                "blockchains": "fabric-1"
            },
            "org0.test.com": {
                "nodes": {
                    "ca": "ca.org0.test.com",
                    "leader_peers": ["peer0.org0.test.com"],
                    "anchor_peers": ["peer0.org0.test.com"],
                    "committing_peers": ["peer0.org0.test.com"],
                    "endorsing_peers": ["peer0.org0.test.com"]
                },
                "blockchains": "fabric-1",
                "channel": ["channel-1"]
            },
            "org1.test.com": {
                "nodes": {
                    "ca": "ca.org1.test.com",
                    "leader_peers": ["peer0.org1.test.com"],
                    "anchor_peers": ["peer0.org1.test.com"],
                    "committing_peers": ["peer0.org1.test.com"],
                    "endorsing_peers": ["peer0.org1.test.com"]
                },
                "blockchains": "fabric-1",
                "channel": ["channel-1"]
            },
            "org2.test.com": {
                "nodes": {
                    "ca": "ca.org2.test.com",
                    "leader_peers": ["peer0.org2.test.com"],
                    "anchor_peers": ["peer0.org2.test.com"],
                    "committing_peers": ["peer0.org2.test.com"],
                    "endorsing_peers": ["peer0.org2.test.com"]
                },
                "blockchains": "fabric-1",
                "channel": ["channel-1"]
            }
        },
        "nodes": {
            "ca.orderer.test.com": {
                "address": {"host": "10.134.66.131", "ssh_port": "22", "fabric_port": "7054", "sk": ""},
                "type": ["ca"]
            },
            "orderer0.orderer.test.com": {
                "address": {"host": "10.134.66.131", "ssh_port": "22", "fabric_port": "7050", "sk": ""},
                "type": ["orderer"]
            },
            "orderer1.orderer.test.com": {
                "address": {"host": "10.134.50.142", "ssh_port": "22", "fabric_port": "7050", "sk": ""},
                "type": ["orderer"]
            },
            "orderer2.orderer.test.com": {
                "address": {"host": "10.134.50.70", "ssh_port": "22", "fabric_port": "7050", "sk": ""},
                "type": ["orderer"]
            },
            "ca.org0.test.com": {
                "address": {"host": "10.134.66.131", "ssh_port": "22", "fabric_port": "8054", "sk": ""},
                "type": ["ca"]
            },
            "peer0.org0.test.com": {
                "address": {"host": "10.134.66.131", "ssh_port": "22", "fabric_port": "7051", "sk": ""},
                "bootstrap": ["127.0.0.1:7051"],
                "type": ["leader_peer", "anchor_peer", "committing_peer", "endorsing_peers"]
            },
            "ca.org1.test.com": {
                "address": {"host": "10.134.50.142", "ssh_port": "22", "fabric_port": "7054", "sk": ""},
                "type": ["ca"]
            },
            "peer0.org1.test.com": {
                "address": {"host": "10.134.50.142", "ssh_port": "22", "fabric_port": "7051", "sk": ""},
                "bootstrap": ["127.0.0.1:7051"],
                "type": ["leader_peer", "anchor_peer", "committing_peer", "endorsing_peers"]
            },
            "ca.org2.test.com": {
                "address": {"host": "10.134.50.70", "ssh_port": "22", "fabric_port": "7054", "sk": ""},
                "type": ["ca"]
            },
            "peer0.org2.test.com": {
                "address": {"host": "10.134.50.70", "ssh_port": "22", "fabric_port": "7051", "sk": ""},
                "bootstrap": ["127.0.0.1:7051"],
                "type": ["leader_peer", "anchor_peer", "committing_peer", "endorsing_peers"]
            },
        },
        "blockchains": {
            "fabric-1": {
                "name": "FabricDraw",
                "channels": ["channel-1"]
            }
        }
    }
    with open('id_rsa', 'r') as file:
        sk = file.read()
    for node_id in network_json['nodes'].keys():
        network_json['nodes'][node_id]['address']['sk'] = sk
    parse_json(network_json)
