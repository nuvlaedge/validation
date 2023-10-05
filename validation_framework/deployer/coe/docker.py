import logging
import json
import invoke

from validation_framework.common.nuvla_uuid import NuvlaUUID
from validation_framework.deployer.coe import COEBase
from validation_framework.deployer.target_device.target import TargetDeviceConfig
from validation_framework.deployer.target_device.ssh_target import SSHTarget
from validation_framework.common import constants as cte
from fabric import Result
from pathlib import Path

logger: logging.Logger = logging.getLogger(__name__)


class DockerCOE(COEBase):

    def __init__(self, device_config: TargetDeviceConfig, **kwargs):
        self.engine_folder: str = ''
        self.device = SSHTarget(device_config)
        super().__init__(self.device, logger)

    def start_engine(self,
                     uuid: NuvlaUUID,
                     files_path: list[str],
                     remove_old_installation: bool = True,
                     extra_envs: dict = None):

        files: str = ' -f '.join(files_path)
        start_command: str = cte.COMPOSE_UP.format(prepend='nohup',
                                                   project_name=cte.PROJECT_NAME,
                                                   files=files)

        self.logger.debug(f'Starting engine with command: \n\n\t{start_command}\n')

        self.engine_configuration.nuvlabox_uuid = uuid
        self.engine_configuration.nuvlaedge_uuid = uuid

        envs_configuration: dict = self.engine_configuration.model_dump(by_alias=True)

        if extra_envs:
            envs_configuration.update(extra_envs)

        self.logger.info(f'Starting NuvlaEdge with UUID: {uuid} with'
                         f' configuration: '
                         f'\n\n {json.dumps(envs_configuration, indent=4)} \n')
        self.device.run_command(start_command, envs=envs_configuration)
        self.logger.info('Device start command executed')

    def add_peripheral(self):
        pass

    def remove_peripheral(self):
        pass

    def stop_engine(self):
        self.purge_engine()

    def get_engine_logs(self):
        self.logger.info(f'Retrieving Log files from engine run with UUID: {self.engine_configuration.nuvlaedge_uuid}')
        # 1. Retrieve deployment containers ID's
        result: Result = self.device.run_command(
            "docker ps -a --format '{\"ID\":\"{{ .ID }}\", \"Image\": \"{{ .Image }}\", \"Names\":\"{{ .Names }}\"}' "
            f"--filter label=com.docker.compose.project={self.engine_configuration.compose_project_name} | jq --tab -s .")

        self.logger.debug(f'Extracting logs from: \n\n\t{result.stdout}\n')
        containers = json.loads(result.stdout)

        # 2. Iteratively copy files from /var/docker/logs/<container_id>.log to
        # /tmp/<new_folder> and chmod before transferring it the running machine
        self.device.run_command(
            f'mkdir -p /tmp/{self.engine_configuration.compose_project_name}')
        local_tmp_path: Path = Path(f'/tmp/{self.engine_configuration.compose_project_name}')
        local_tmp_path.mkdir(parents=True, exist_ok=True)

        for c in containers:
            c_name = c.get('Names')
            full_id = self.device.run_command(command='docker inspect --format="{{.Id}}" ' + c_name).stdout
            full_id = full_id.replace('\n', '')
            full_id = full_id.replace('\\', '')

            self.logger.debug(f'Processing logs for nuvlaedge {c_name}')
            self.device.run_sudo_command(f'sudo cp /var/lib/docker/containers/{full_id}/{full_id}-json.log '
                                         f'/tmp/{c_name}.log')
            self.device.run_sudo_command(f'sudo chmod 777 /tmp/{c_name}.log')

            # 3. Transfer back the files

            self.device.download_remote_file(remote_file_path=f'/tmp/{c_name}.log',
                                             local_file_path=local_tmp_path / (c_name + '.log'))

        # 4. Remove remote temporal folder
        self.device.run_sudo_command(
            f'sudo rm -r /tmp/{self.engine_configuration.compose_project_name}/')
    def get_container_logs(self, container):
        pass

    def engine_running(self) -> bool:
        result: Result = self.device.run_command(f'docker ps | grep {cte.PROJECT_NAME}')
        return result.stdout.strip() != ''

    def remove_engine(self):
        self.purge_engine()

    def purge_engine(self):
        """
        Removes docker containers, services, volumes and networks from the device
        :return: None
        """
        self.logger.info(f'Purging engine in device {self.device}')

        command_list: list = ['docker service rm $(docker service ls -q)',
                              'docker stop $(docker ps -a -q)',
                              'docker rm $(docker ps -a -q)',
                              'docker network prune --force',
                              'docker volume rm $(docker volume ls -q)']

        for cmd in command_list:
            try:
                self.device.run_command(cmd)
            except invoke.exceptions.UnexpectedExit:
                pass
            except Exception as ex:
                self.logger.warning(f'Unable to run commands on {self.device} {ex}')

    def download_files(self, source, version) -> list[str]:
        self.engine_folder = cte.ROOT_PATH + cte.ENGINE_PATH + version
        self.device.run_command(f'mkdir -p {self.engine_folder}')
        self.logger.info(f'Downloading deployment files into {self.engine_folder}')
        # Download deployment files
        if not self.device.download_file(link=source,
                                         file_name=cte.ENGINE_BASE_FILE_NAME,
                                         directory=self.engine_folder):
            self.logger.error(f'Deployment file {cte.ENGINE_BASE_FILE_NAME} could not'
                              f' be downloaded from {source}')
            return []

        # TODO: iterate here when peripheral validation is implemented to download the
        #  peripheral deployment file
        # ------------------------------------------------------------------------
        # Pull nuvlaedge image(s)
        # ------------------------------------------------------------------------
        print(f'Engine Configuration Amit {self.engine_configuration.model_dump(by_alias=True)}')
        self.logger.info(f'Engine Configuration Amit {self.engine_configuration.model_dump(by_alias=True)}')
        pull_result: Result = self.device.run_command(f'docker compose -f '
                                                      f'{self.engine_folder + "/" + cte.ENGINE_BASE_FILE_NAME} '
                                                      f'pull',
                                                      envs=self.engine_configuration.model_dump(
                                                          by_alias=True))
        return [self.engine_folder + '/' + cte.ENGINE_BASE_FILE_NAME] if not pull_result.failed else []
