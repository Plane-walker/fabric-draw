import subprocess
import argparse


def peer_msp_generate(crypto_base, peer_name, org_name, org_domain, ca_port):
    org_home = f'{crypto_base}/organizations/peerOrganizations/{org_name}.{org_domain}'
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
              f'cp {peer_home}/tls/tlscacerts/* {org_home}/tlsca/tlsca.{org_name}.${org_domain}-cert.pem;' \
              f'mkdir -p {org_home}/ca;' \
              f'cp {peer_home}/msp/cacerts/* {org_domain}/ca;'
    subprocess.run(command, shell=True, stdout=subprocess.PIPE)


def init_channel_artifacts(crypto_base, fabric_name, channel_id, channel_name, org_names):
    channel_artifacts_path = f'{crypto_base}/channel-artifacts'
    command = f'mkdir -p {channel_artifacts_path};'\
              f'configtxgen -profile {fabric_name}OrdererGenesis -outputBlock {channel_artifacts_path}/orderer.genesis.block -channelID system-channel;' \
              f'configtxgen -profile {channel_name}Channel -outputCreateChannelTx {channel_artifacts_path}/{channel_id}.tx -channelID {channel_id};'
    for org_name in org_names:
        command += f'configtxgen -profile {channel_name}Channel -outputAnchorPeersUpdate {channel_artifacts_path}/{org_name}MSPanchors.tx -channelID {channel_id} -asOrg {org_name}MSP;'
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
    command += ' >> /etc/hosts'
    subprocess.run(command, shell=True, stdout=subprocess.PIPE)


if __name__ == "__main__":
    update_hosts({'1.1.1.1': 'a.com', '2.2.2.2': 'b.vom'})
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("--docker-compose", type=str, help="Test docker_compose function.")
    # Test: python3 node_build.py --docker-compose ./docker-compose.yml

    args = parser.parse_args()

    print(args)
    if args.docker_compose:
        docker_compose(args.docker_compose)
        docker_compose(args.docker_compose, down=True)
