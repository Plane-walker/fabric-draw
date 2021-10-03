import subprocess
import argparse


def org_msp_generate(crypto_base: str, name: str, domain: str, port):
    """
    order org path: CRYPTO_BASE/organizations/NAME.DOMAIN
    peer  org path: CRYPTO_BASE/organizations/NAME.DOMAIN
    
    ca_tls_ca path: CRYTRO_BASE/organizations/fabric-ca/NAME/tls-cert.pem
        e.g. order: CRYTRO_BASE/organizations/fabric-ca/orderer/tls-cert.pem
              peer: CRYTRO_BASE/organizations/fabric-ca/org1/tls-cert.pem
    
    fabric-ca-client enroll -u: https://admin:adminpw@ca.NAME.DOMAIN:PORT
                    e.g. order: https://admin:adminpw@ca.orderer.test.com:7054
                          peer: https://admin:adminpw@ca.org1.test.com:7054
    """
    crypto_base += '/organizations/' if crypto_base[-1] != '/' else 'organizations/'
    org_home = f'{crypto_base}/{name}.{domain}/'
    command = f'mkdir -p ' + org_home + f';'

    ca_tls_ca = f'{crypto_base}fabric-ca/{name}/tls-cert.pem'
    command += f'fabric-ca-client enroll -u https://admin:adminpw@ca.{name}.{domain}:{port} --caname ca-{name} --tls.certfiles {ca_tls_ca};'
    
    config_text = f"NodeOUs:\n" \
                  f"Enable: true\n" \
                  f"ClientOUIdentifier:\n" \
                  f"  Certificate: cacerts/localhost-{port}-ca-{name}.pem\n" \
                  f"  OrganizationalUnitIdentifier: client\n" \
                  f"PeerOUIdentifier:\n" \
                  f"  Certificate: cacerts/localhost-{port}-ca-{name}.pem\n" \
                  f"  OrganizationalUnitIdentifier: peer\n" \
                  f"AdminOUIdentifier:\n" \
                  f"  Certificate: cacerts/localhost-{port}-ca-{name}.pem\n" \
                  f"  OrganizationalUnitIdentifier: admin\n" \
                  f"OrdererOUIdentifier:\n" \
                  f"  Certificate: cacerts/localhost-{port}-ca-{name}.pem\n" \
                  f"OrganizationalUnitIdentifier: orderer"
    command += f'echo "{config_text}" >> {org_home}msp/config.yaml;'
    command += f'cp {org_home}msp/cacerts/* {org_home}msp/cacerts/localhost-{port}-ca-{name}.pem;'
    subprocess.run(command, shell=True, stdout=subprocess.PIPE)


def peer_msp_generate(crypto_base, peer_name, org_name, org_domain, ca_port):
    org_home = f'{crypto_base}/organizations/{org_name}.{org_domain}'
    peer_home = f'{org_home}/peers/{peer_name}.{org_name}.{org_domain}'
    ca_tls_ca = f'{crypto_base}/organizations/fabric-ca/{org_name}/tls-cert.pem'
    command = f'mkdir -p {peer_home};' \
              f'fabric-ca-client register --caname ca-{org_name} --id.name {peer_name} --id.secret {peer_name}pw --id.type peer --tls.certfiles {ca_tls_ca};' \
              f'fabric-ca-client enroll -u https://{peer_name}:{peer_name}pw@ca.{org_name}.{org_domain}:{ca_port} --caname ca-{org_name} -M {peer_home}/msp --csr.hosts {peer_name}.{org_name}.{org_domain} --tls.certfiles {ca_tls_ca};' \
              f'cp {peer_home}/msp/cacerts/* {peer_home}/msp/cacerts/localhost-{ca_port}-ca-{org_name}.pem;' \
              f'fabric-ca-client enroll -u https://{peer_name}:{peer_name}pw@ca.{org_name}.{org_domain}:{ca_port} --caname ca-{org_name} -M {peer_home}/tls --enrollment.profile tls --csr.hosts {peer_name}.{org_name}.{org_domain} --csr.hosts localhost --tls.certfiles {ca_tls_ca};' \
              f'cp {org_home}/msp/config.yaml {peer_home}/msp/config.yaml;' \
              f'cp {peer_home}/tls/tlscacerts/* {peer_home}/tls/ca.crt;' \
              f'cp {peer_home}/tls/signcerts/* {peer_home}/tls/server.crt;' \
              f'cp {peer_home}/tls/keystore/* {peer_home}/tls/server.key;' \
              f'mkdir -p {org_home}/msp/tlscacerts;' \
              f'cp {peer_home}/tls/tlscacerts/* {org_home}/msp/tlscacerts/ca.crt;' \
              f'mkdir -p {org_home}/tlsca;' \
              f'cp {peer_home}/tls/tlscacerts/* {org_home}/tlsca/tlsca.{org_name}.{org_domain}-cert.pem;' \
              f'mkdir -p {org_home}/ca;' \
              f'cp {peer_home}/msp/cacerts/* {org_domain}/ca;'
    subprocess.run(command, shell=True, stdout=subprocess.PIPE)


def init_channel_artifacts(fabric_name, channel_id, peer_org_ids, crypto_base):
    channel_artifacts_path = f'{crypto_base}/channel-artifacts'
    command = f'configtxgen -profile {fabric_name}OrdererGenesis -outputBlock {channel_artifacts_path}/orderer.genesis.block -channelID system-channel;' \
              f'configtxgen -profile {fabric_name}Channel -outputCreateChannelTx {channel_artifacts_path}/{channel_id}.tx -channelID {channel_id};'
    for peer_org_id in peer_org_ids:
        org_name = peer_org_id.split('.', 1)[0]
        command += f'configtxgen -profile {fabric_name}Channel -outputAnchorPeersUpdate {channel_artifacts_path}/{org_name.capitalize()}MSPanchors.tx -channelID {channel_id} -asOrg {org_name.capitalize()}MSP;'
    subprocess.run(command, shell=True, stdout=subprocess.PIPE)


def init_docker_swarm(host, channel_name, data_path_port='5789'):
    command = f'docker swarm init --advertise-addr {host} --data-path-port {data_path_port}'
    subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    command = 'docker swarm join-token -q manager'
    token = subprocess.run(command, shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
    command = f'docker network create --attachable --driver overlay {channel_name}'
    subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    return token


def join_docker_swarm(token, host, target_host, target_port=2377):
    command = f'docker swarm join --token {token} {target_host}:{target_port} --advertise-addr {host}'
    subprocess.run(command, shell=True, stdout=subprocess.PIPE)


def docker_compose(path: str, down: bool = False) -> subprocess.CompletedProcess:
    """
    :param path: The relative path from main program or absolute path of docker-compose.yaml(including filename)
    :param down: True means `docker-compose down` and False means `docker-compose up`
    """
    command = f"docker-compose -f {path} up -d" if not down else f"docker-compose -f {path} down"
    return subprocess.run(command, shell=True, stdout=subprocess.PIPE)


def update_hosts(new_hosts):
    command = 'echo "'
    for ip, domain in new_hosts.items():
        command += f'{ip} {domain}\n'
    command += '" >> /etc/hosts'
    subprocess.run(command, shell=True, stdout=subprocess.PIPE)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--func_name", type=str, help="Function name.")
    parser.add_argument('nargs', nargs='*')
    args = parser.parse_args()
    eval(args.func_name)(*args.nargs)

