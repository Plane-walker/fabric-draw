import paramiko
import io
import os
from yaml_generator import CAYamlGenerator, OrderYamlGenerator


def generate_ca(ca_id, ca_information, crypto_base):
    node_name, group_name, domain = ca_id.split('.', 2)
    address = ca_information['address']
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_file = io.StringIO(address['sk'])
    private_key = paramiko.RSAKey.from_private_key(key_file)
    ssh.connect(hostname=address['host'], port=22, username='root', pkey=private_key)
    ssh.exec_command(f'if [ ! -d {crypto_base} ]; then mkdir -p {crypto_base}; fi')
    ftp_client = ssh.open_sftp()
    file_name = 'node_build.py'
    ftp_client.put(file_name, f'{crypto_base}/{file_name}')
    ca_yaml_generator = CAYamlGenerator()
    file_name = ca_yaml_generator.generate(ca_id, ca_information['org_name'])
    ftp_client.put(file_name, f'{crypto_base}/{file_name}')
    ssh.exec_command(f'python node_build.py docker_compose "{file_name}"')
    tls_cert_path = f'organizations/fabric-ca/{group_name}'
    if not os.path.exists(tls_cert_path):
        os.makedirs(tls_cert_path)
    ftp_client.get(f'{crypto_base}/{tls_cert_path}/tls-cert.pem', tls_cert_path)
    ftp_client.close()


def generate_order_msp(order_id, order_information, crypto_base='/root/opt'):
    node_name, group_name, domain = order_id.split('.', 2)
    address = order_information['address']
    node_port = address['port']
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_file = io.StringIO(address['sk'])
    private_key = paramiko.RSAKey.from_private_key(key_file)
    ssh.connect(hostname=address['host'], port=22, username='root', pkey=private_key)
    tls_cert_path = f'fabric-ca/{group_name}'
    ssh.exec_command(f'if [ ! -d {crypto_base}/{tls_cert_path} ]; then mkdir -p {crypto_base}/{tls_cert_path}; fi')
    ftp_client = ssh.open_sftp()
    ftp_client.put(f'{tls_cert_path}/tls-cert.pem', f'{crypto_base}/{tls_cert_path}')
    file_name = 'node_build.py'
    ftp_client.put(file_name, f'{crypto_base}/{file_name}')
    order_yaml_generator = OrderYamlGenerator()
    file_name = order_yaml_generator.generate(order_id, group_name, node_name)
    ftp_client.put(file_name, f'{crypto_base}/{file_name}')
    ssh.exec_command(f'python node_build.py org_msp_generate "{crypto_base}" "{group_name}" "{domain}" "{node_port}"')
    ssh.exec_command(f'python node_build.py peer_msp_generate "{crypto_base}" "{node_name}" "{group_name}" "{domain}" "{node_port}"')
    tls_ca_path = f'organizations/{group_name}.{domain}/tlsca'
    if not os.path.exists(tls_ca_path):
        os.makedirs(tls_ca_path)
    ftp_client.get(f'{crypto_base}/{tls_ca_path}/tlsca.test.com-cert.pem', tls_ca_path)
    server_path = f'organizations/{group_name}.{domain}/orderers/{order_id}/tls'
    if not os.path.exists(server_path):
        os.makedirs(server_path)
    ftp_client.get(f'{crypto_base}/{server_path}/server.crt', server_path)
    ftp_client.close()


def parse_json(network_topology_json):
    order_group_id = ''
    for group_id, group_information in network_topology_json['groups']:
        if group_id.split('.', 1)[0] == 'orderer':
            order_group_id = group_id
        generate_ca(group_information['nodes'][group_information['nodes']['ca']], network_topology_json['nodes'][group_information['nodes']['ca']], '/root/opt')
    for order_id in network_topology_json['groups'][order_group_id]['nodes']['orderer']:
        generate_order_msp(order_id, network_topology_json['nodes'][order_id])
