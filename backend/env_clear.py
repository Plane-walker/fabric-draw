import subprocess
import sys


def env_cleaer(crypto_path='/root/opt'):
    docker_rm = 'docker stop $(docker ps -a -q);' \
                'docker rm $(docker ps -a -q);' \
                'docker volume rm $(docker volume ls -q);' \
                'docker swarm leave -f;' \
                'docker network prune -f'
    subprocess.run(docker_rm, shell=True, stdout=subprocess.PIPE)
    path_rm = f'rm -rf {crypto_path}'
    subprocess.run(path_rm, shell=True, stdout=subprocess.PIPE)


if __name__ == '__main__':
    env_cleaer()
    

