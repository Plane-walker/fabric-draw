import paramiko
import io
from yaml_generator import CAYamlGenerator


def generate_ca(ca_id, ca_information, crypto_base):
    address = ca_information['address']
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_file = io.StringIO(address['sk'])
    private_key = paramiko.RSAKey.from_private_key(key_file)
    ssh.connect(hostname=address['host'], port=22, username='root', pkey=private_key)
    ca_yaml_generator = CAYamlGenerator()
    file_name = ca_yaml_generator.generate(ca_id, ca_information['org_name'])
    ftp_client = ssh.open_sftp()
    ftp_client.put(file_name, f'{crypto_base}/{file_name}')
    ftp_client.close()
    ssh.exec_command(f'python node_build.py docker_compose {file_name}')


def parse_json(network_topology_json):
    for group_id, group_information in network_topology_json['groups']:
        generate_ca(group_information['nodes']['ca'], network_topology_json['nodes'][group_information['nodes']['ca']], '/root/opt')
