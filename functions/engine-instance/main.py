from google.cloud import secretmanager
import paramiko
from io import StringIO

PROJECT_NAME = 'climate-data-graph-scheduler'


def update_climate_data_graph_in_engine(event, context):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        private_key_file = StringIO(get_private_key())
        private_key = paramiko.RSAKey.from_private_key(private_key_file)

        ssh_client.connect(
            hostname='35.238.110.48',
            username='root',
            pkey=private_key
        )

        stdin_ls, stdout_ls, stderr_ls = ssh_client.exec_command('ls')

        if PROJECT_NAME not in stdout_ls.read().decode('utf-8'):
            stdin_clone, stdout_clone, stderr_clone = ssh_client.exec_command(f'git clone git@github.com:lxiong1/{PROJECT_NAME}.git')
            print(stdout_clone.read())

        stdin_update, stdout_update, stderr_update = ssh_client.exec_command(f'cd {PROJECT_NAME} && PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin ./update-climate-data-graph.sh')
        print(stdout_update.read())
    except Exception as exception:
        print(f'Error: {exception}')


def get_private_key():
    secret_manager_client = secretmanager.SecretManagerServiceClient()

    return secret_manager_client \
        .access_secret_version('projects/203517643656/secrets/gcp_key/versions/1') \
        .payload \
        .data \
        .decode("utf-8")
