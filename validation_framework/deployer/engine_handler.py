"""
Higher class that wraps together the device and the release handler
"""
import json
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
                 target_device: Path,
                 deployment_release: str = '',
                 nuvlaedge_release: str = '',
                 repo: str = '',
                 branch: str = '',
                 include_peripherals: bool = False,
                 peripherals: list[str] = None):
        """
        Engine handler constructor. It is in charge of assessing if the targets are passed as index or path to file.
        If an index is passed has to find the corresponding file in the default folder, if it's a path, directly
        loads the configuration.
        :param target_device: Index or path to target device file
        :param deployment_release: Release tag
        """
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.logger.debug(f'Creating Engine Handler on device {target_device}')

        # Assess device configuration
        self.device_config_file: Path = target_device
        if not self.device_config_file.is_file():
            raise FileNotFoundError(f'Provided file {self.device_config_file} does not exists')

        self.device_config: TargetDeviceConfig = utils.get_model_from_toml(TargetDeviceConfig, self.device_config_file)
        self.device: SSHTarget = SSHTarget(self.device_config)

        # Asses release configuration
        if deployment_release:
            target_release = Release(deployment_release)
        else:
            target_release = ReleaseHandler.get_latest_release(cte.RELEASES_LINK)

        if nuvlaedge_release:
            nuvlaedge_release = Release(nuvlaedge_release)
        else:
            nuvlaedge_release = ReleaseHandler.get_latest_release(cte.NUVLAEDGE_RELEASES_LINK)

        self.release_config: TargetReleaseConfig = TargetReleaseConfig(tag=target_release,
                                                                       nuvlaedge_tag=nuvlaedge_release,
                                                                       repository=repo,
                                                                       branch=branch,
                                                                       include_peripherals=include_peripherals,
                                                                       peripherals=peripherals)
        self.release_handler: ReleaseHandler = ReleaseHandler(self.release_config)
        self.logger.info(f'Gather information from release {self.release_config}')

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
        self.logger.info(f'Downloading files for release {self.release_handler.release_tag} into {self.target_dir}/')
        self.device.run_command(f'mkdir -p {self.target_dir}')

        for link in self.release_handler.get_download_cmd():
            self.device.download_file(link=link,
                                      file_name=link.split('/')[-1],
                                      directory=self.target_dir)

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
        files: str = ' -f '.join([self.target_dir + '/' + i for i in self.release_handler.requested_release.components])
        start_command: str = cte.COMPOSE_UP.format(prepend='nohup',
                                                   project_name=cte.PROJECT_NAME,
                                                   files=files)

        self.logger.debug(f'Starting engine with command: \n\n\t{start_command}\n')
        ne_version = self.release_config.branch if self.release_config.branch else self.release_config.nuvlaedge_tag
        docker_repo = 'nuvlaedge' if not self.release_config.branch else 'nuvladev'
        envs_configuration: dict = {'NUVLABOX_UUID': nuvlaedge_uuid,
                                    'NUVLAEDGE_UUID': nuvlaedge_uuid,
                                    'NUVLAEDGE_VERSION': 'v' + ne_version,
                                    'DOCKER_ORG': docker_repo,
                                    'COMPOSE_PROJECT_NAME': cte.PROJECT_NAME}

        if extra_envs:
            envs_configuration.update(extra_envs)

        self.logger.info(f'Pull the images and update them with envs: {json.dumps(envs_configuration,indent=4)}')
        self.device.run_command(f'docker compose -f {self.target_dir + "/" + "docker-compose.yml"} pull',
                                envs=envs_configuration)

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


