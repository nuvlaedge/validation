"""
Higher class that wraps together the device and the release handler
"""
import logging
import os
from pathlib import Path

import wget

from validation_framework.common import (Release, utils)
from validation_framework.common.nuvla_uuid import NuvlaUUID
from validation_framework.common.schemas.release import TargetReleaseConfig
from validation_framework.common.schemas.target_device import TargetDeviceConfig
from validation_framework.common import constants as cte
from validation_framework.deployer import SSHTarget
from validation_framework.deployer.release_handler import ReleaseHandler


class EngineHandler:
    """
    (NuvlaEdge)
    """
    # TODO: Move this variable to proper place
    target_dir: str = ''
    nuvlaedge_uuid: NuvlaUUID = ''

    def __init__(self,
                 target_device: int | Path,
                 target_release: str,
                 repo: str = '',
                 branch: str = '',
                 include_peripherals: bool = False,
                 peripherals: list[str] = None):
        """
        Engine handler constructor. It is in charge of assessing if the targets are passed as index or path to file.
        If an index is passed has to find the corresponding file in the default folder, if it's a path, directly
        loads the configuration.
        :param target_device: Index or path to target device file
        :param target_release: Index or Release tag or path to target release file
        """
        self.logger: logging.Logger = logging.getLogger(__name__)

        # Assess device configuration
        if isinstance(target_device, int):
            self.logger.debug('Gather information from index')
            self.device_config_file: Path = Path(self.get_device_config_by_index(target_device))
        else:
            self.logger.debug('Gather information from path')
            self.device_config_file: Path = target_device
        if not self.device_config_file.is_file():
            raise FileNotFoundError(f'Provided file {self.device_config_file} does not exists')

        self.device_config: TargetDeviceConfig = utils.get_model_from_toml(TargetDeviceConfig, self.device_config_file)
        self.device: SSHTarget = SSHTarget(self.device_config)

        # Asses release configuration
        self.release_config: TargetReleaseConfig = TargetReleaseConfig(tag=Release(target_release),
                                                                       repository=repo,
                                                                       branch=branch,
                                                                       include_peripherals=include_peripherals,
                                                                       peripherals=peripherals)
        self.release_handler: ReleaseHandler = ReleaseHandler(self.release_config)
        self.logger.error(f'Gather information from release {self.release_config}')

    @staticmethod
    def get_device_config_by_index(device_index: int) -> Path:
        """

        :param device_index: Numerical index to identify specific device configurations
        :return: The file location
        """
        for file in cte.DEVICE_CONFIG_PATH.iterdir():
            if file.is_file() and file.name.startswith(str(device_index)):
                return cte.DEVICE_CONFIG_PATH / file

        raise IndexError(f'Device with index {device_index} not found in {cte.DEVICE_CONFIG_PATH}')

    def prepare_compose_files(self,
                              include_peripherals: bool = False,
                              peripherals: list[str] = None):
        """

        :return: the path location of the files.
        """
        self.target_dir: str = cte.ROOT_PATH + cte.ENGINE_PATH + self.release_handler.release_tag
        self.logger.error(f'Downloading files for release {self.release_handler.release_tag} into {self.target_dir}/')
        self.device.run_command(f'mkdir -p {self.target_dir}')
        for link in self.release_handler.get_download_cmd():
            self.device.download_file(link=link,
                                      file_name=link.split('/')[-1],
                                      directory=self.target_dir)

        if self.release_config.branch and self.release_config.repository:
            self.logger.info(f'Working on pull request, editing microservice {self.release_config.branch} '
                             f'to match nuvladev repository on tag {self.release_handler.requested_release.tag}')
            if os.path.exists('docker-compose.yml'):
                os.remove('docker-compose.yml')

            wget.download('https://raw.githubusercontent.com/nuvlaedge/deployment/preprod-validation/docker-compose.yml',
                          out='docker-compose.yml')
            self.release_handler.prepare_custom_release(os.getcwd())
            self.device.send_file(os.getcwd() + '/docker-compose.yml', '/tmp/')

            target_path: str = cte.ROOT_PATH + cte.ENGINE_PATH + '/' + self.release_handler.release_tag + '/' \
                               + 'docker-compose.yml'

            self.device.run_command(f'rm {target_path}')
            self.device.run_command(f'mv /tmp/docker-compose.yml {target_path}')

    def start_engine(self, nuvlaedge_uuid: NuvlaUUID,
                     remove_old_installation: bool = False,
                     extra_envs: dict = None):
        """

        :return:
        """
        if remove_old_installation:
            # 1. - Clean target
            self.device.clean_target()

        # 2. - Check remote files
        self.prepare_compose_files()

        # 3. - Start engine with target release (Future custom as well)
        files: str = f' -f '.join([self.target_dir + '/' + i for i in self.release_handler.requested_release.components])
        start_command: str = cte.COMPOSE_UP.format(prepend='nohup',
                                                   project_name=cte.PROJECT_NAME,
                                                   files=files)

        self.logger.debug(f'Starting engine with command: \n\n{start_command}\n')
        envs_configuration: dict = {'NUVLABOX_UUID': nuvlaedge_uuid,
                                    'NUVLAEDGE_UUID': nuvlaedge_uuid,
                                    'COMPOSE_PROJECT_NAME': cte.PROJECT_NAME}

        if extra_envs:
            envs_configuration.update(extra_envs)

        self.logger.info('Pull the images and update them')
        self.device.run_command(f'docker compose -f {self.target_dir + "/" + "docker-compose.yml"} pull')

        self.logger.info(f'Starting engine with Edge uuid: {nuvlaedge_uuid} and envs {envs_configuration}')
        self.device.run_command(start_command, envs=envs_configuration)
        self.logger.info('Device start command executed')

    def stop_engine(self) -> bool:
        """

        :return:
        """
        if not self.engine_running():
            self.logger.info('Engine not running')
            return True

        self.device.clean_target()

    def engine_running(self) -> bool:
        """

        :return:
        """
        self.device.run_command('docker ps')
        return True

    def clean_device(self):
        """

        :return:
        """


