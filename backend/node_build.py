import subprocess
import argparse


def docker_compose(path: str, down: bool=False) -> subprocess.CompletedProcess:
    '''
    :param path: The relative path from main program or absolute path of docker-compose.yaml(including filename)
    :param down: True means `docker-compose down` and False means `docker-compose up`
    '''
    command = f"docker-compose -f {path} up -d" if not down else f"docker-compose -f {path} down"
    return subprocess.run(command, shell=True, stdout=subprocess.PIPE)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    
    parser.add_argument("--docker-compose", type=str, help="Test docker_compose function.")
    # Test: python3 node_build.py --docker-compose ./docker-compose.yml 

    args = parser.parse_args()

    print(args)
    if args.docker_compose:
        docker_compose(args.docker_compose)
        docker_compose(args.docker_compose, down=True)