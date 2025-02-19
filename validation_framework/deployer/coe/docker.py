import logging
import json
import invoke
import requests

from validation_framework.common.nuvla_uuid import NuvlaUUID
from validation_framework.deployer.coe import COEBase
from validation_framework.deployer.target_device.target import TargetDeviceConfig
from validation_framework.deployer.target_device.ssh_target import SSHTarget
from validation_framework.common import constants as cte
from fabric import Result
from pathlib import Path
from validation_framework.common import Release


class DockerCOE(COEBase):

    def __init__(self, device_config: TargetDeviceConfig, **kwargs):
        self.engine_folder: str = ''
        self.device = SSHTarget(device_config)
        super().__init__(self.device, logging.getLogger(__name__), **kwargs)

        self.assess_nuvlaedge_sourcecode_configuration()

    @staticmethod
    def get_latest_release(release_link: str) -> Release:
        available_releases: list = requests.get(release_link).json()
        if available_releases:
            return Release(available_releases[0].get('tag_name'))
        else:
            raise NotImplemented('')

    def assess_nuvlaedge_sourcecode_configuration(self):
        """
        If nuvlaedge_branch is provided, the docker organization (NE_IMAGE_ORGANIZATION)
        becomes nuvladev and NE_RELEASE_TAG compose configuration becomes nuvlaedge_branch

        If deployment_branch is assigned, the compose files are downloaded from a branch
        instead of a release ignoring the possible parsed version

        If no nuvlaedge version is assigned, take the latest release. It is expected to
        always have deployment and nuvlaedge repo's releases in the same versions.
        """

        # ------------------------------------------------------------
        # Handle deployment repository configuration
        # ------------------------------------------------------------
        if self.deployment_branch:
            self.logger.info(f'Running NuvlaEdge from deployment branch: '
                             f'{self.deployment_branch}')
            self.deployment_link = cte.DEPLOYMENT_FILES_LINK.format(
                branch_name=self.deployment_branch,
                file='{file}')

        else:
            if not self.nuvlaedge_version or self.nuvlaedge_version == 'latest':
                self.logger.info('No deployment branch nor release version provided, '
                                 'gathering latest nuvlaedge release')
                self.nuvlaedge_version = \
                    self.get_latest_release(cte.NUVLAEDGE_RELEASES_LINK)

            self.logger.info(f'Running NuvlaEdge from deployment release version: '
                             f'{self.deployment_branch}')
            self.deployment_link = cte.RELEASE_DOWNLOAD_LINK.format(
                version=self.nuvlaedge_version,
                file='{file}')

    def start_engine(self,
                     uuid: NuvlaUUID,
                     remove_old_installation: bool = True,
                     extra_envs: dict = None,
                     project_name: str = cte.PROJECT_NAME):

        if remove_old_installation:
            self.purge_engine()
        engine_base_link = self.deployment_link.format(file=cte.ENGINE_BASE_FILE_NAME)
        files_path = self.download_files(engine_base_link, self.nuvlaedge_version)
        files: str = ' -f '.join(files_path)
        start_command: str = cte.COMPOSE_UP.format(prepend='nohup',
                                                   project_name=project_name,
                                                   files=files)
        self.project_name = project_name

        self.logger.debug(f'Starting engine with command: \n\n\t{start_command}\n')

        self.engine_configuration.nuvlabox_uuid = uuid
        self.engine_configuration.nuvlaedge_uuid = uuid

        envs_configuration: dict = self.engine_configuration.model_dump(by_alias=True)

        if extra_envs:
            envs_configuration.update(extra_envs)
        self.logger.info(f"Parsed UUID: {uuid}")
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
        command = 'docker stop $(docker ps -a --format "{{.ID}} {{.Names}}" | grep -vE "nuvlaedge-agent|sshgateway|shellinabox" | awk "{print $1}")'
        try:
            self.device.run_command(command)
        except invoke.exceptions.UnexpectedExit:
            self.logger.debug("No containers to stop")
            pass
        except Exception as ex:
            self.logger.warning(f'Unable to run commands on {self.device} {ex} ')

    def get_authorized_keys(self):
        return self.device.run_command("cat ~/.ssh/authorized_keys")

    def peripherals_running(self, peripherals: set) -> bool:
        cont_filter: dict = {"Names": "{{ .Names }}"}

        data: list[dict] = self.device.get_remote_containers(
            containers_filter=cont_filter)

        # Find network container in list
        self.logger.debug('Removing ')
        for c in data:
            if peripherals.__contains__(c):
                peripherals.remove(c.get("Names"))
        return not bool(peripherals)

    def get_remote_containers(self, containers_filter: dict = None) -> list:
        return self.device.get_remote_containers(containers_filter)

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
            f'mkdir -p /tmp/{self.engine_configuration.compose_project_name}/logs')
        local_tmp_path: Path = Path(f'/tmp/{self.engine_configuration.compose_project_name}/logs')
        local_tmp_path.mkdir(parents=True, exist_ok=True)

        self.device.run_sudo_command(
            f'sudo chmod 777 /tmp/{self.engine_configuration.compose_project_name}/logs'
        )

        for c in containers:
            # 3. Download and transfer back the files
            self.get_container_logs(c, True, local_tmp_path)

        # 4. Remove remote temporal folder
        self.device.run_sudo_command(
            f'sudo rm -r /tmp/{self.engine_configuration.compose_project_name}/')

    def get_container_logs(self, container, download_to_local=False, path: Path = None):
        c_name = container.get('Names')
        get_logs_cmd = f'sudo docker logs {c_name} >> /tmp/{self.engine_configuration.compose_project_name}/{c_name}.log'

        self.logger.debug(f'Processing logs for nuvlaedge {c_name}')
        try:
            self.device.run_sudo_command(get_logs_cmd)
        except Exception as ex:
            self.logger.warning(f'Unable to get logs for the container {container} : {ex}')
            return

        if download_to_local and path is not None:
            self.device.download_remote_file(
                remote_file_path=f'/tmp/{self.engine_configuration.compose_project_name}/{c_name}.log',
                local_file_path=path / (c_name + '.log'))

    def engine_running(self) -> bool:
        try:
            result: Result = self.device.run_command(f'docker ps | grep {cte.PROJECT_NAME}')
        except invoke.exceptions.UnexpectedExit:
            return False
        return result.stdout.strip() != ''

    def _get_all_containers(self) -> list[dict]:
        result: Result = self.device.run_command('docker ps --all --format=json')
        containers = []
        try:
            containers: list[dict] = [json.loads(entry) for entry in result.stdout.split("\n")]
        except:
            pass
        return containers

    def remove_engine(self, uuid: NuvlaUUID = None, black_list: list = None):
        """
        Removes docker containers, services, volumes and networks from the device
        :return: None
        """
        self.logger.info(f'Purging engine in device {self.device}')

        command_list: list = ['docker service rm $(docker service ls -q)',
                              'docker rm $(docker ps -a -q)',
                              'docker network prune --force',
                              'docker volume rm $(docker volume ls -q)']

        for cmd in command_list:
            try:
                result = self.device.run_command(cmd)

                self.logger.info(f'Command {cmd} result: {result.stdout}')
            except invoke.exceptions.UnexpectedExit:
                pass
            except Exception as ex:
                self.logger.warning(f'Unable to run commands on {self.device} {ex}')

    def get_coe_type(self):
        return "docker"

    def finish_tasks(self):
        pass

    def purge_engine(self, uuid: NuvlaUUID = None, black_list: list = None):
        self.stop_engine()
        self.remove_engine(uuid, black_list=black_list)

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
        pull_result: Result = self.device.run_command(f'docker compose -f '
                                                      f'{self.engine_folder + "/" + cte.ENGINE_BASE_FILE_NAME} '
                                                      f'pull',
                                                      envs=self.engine_configuration.model_dump(
                                                          by_alias=True))
        return [self.engine_folder + '/' + cte.ENGINE_BASE_FILE_NAME] if not pull_result.failed else []
