"""
Higher class that wraps together the device and the release handler
"""
import json
import logging
from pathlib import Path

from validation_framework.common import (Release, utils)
from validation_framework.common.nuvla_uuid import NuvlaUUID
from validation_framework.common.schemas.release import TargetReleaseConfig
from validation_framework.common.schemas.engine import EngineEnvsConfiguration
from validation_framework.common.schemas.target_device import TargetDeviceConfig
from validation_framework.common import constants as cte
from validation_framework.deployer import SSHTarget
from validation_framework.deployer.release_handler import ReleaseHandler


class EngineHandler:
    """
    (NuvlaEdge)
    """
    # TODO: Move this variable to proper place
    nuvlaedge_uuid: NuvlaUUID = ''

    def __init__(self,
                 target_device: Path,
                 nuvlaedge_version: str = '',
                 nuvlaedge_branch: str = '',
                 deployment_branch: str = '',
                 include_peripherals: bool = False,
                 peripherals: list[str] = None):
        """
        Engine handler constructor. It is in charge of assessing if the targets are passed as index or path to file.
        If an index is passed has to find the corresponding file in the default folder, if it's a path, directly
        loads the configuration.
        :param target_device: Index or path to target device file
        :param nuvlaedge_version: Release version. Synchronized between NuvlaEdge and Deployment repository
        """
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.logger.debug(f'Creating Engine Handler for device {target_device}')

        # Assess device configuration
        self.device_config_file: Path = target_device
        if not self.device_config_file.is_file():
            raise FileNotFoundError(f'Provided file {self.device_config_file} does not exists')

        self.device_config: TargetDeviceConfig = utils.get_model_from_toml(TargetDeviceConfig, self.device_config_file)
        self.device: SSHTarget = SSHTarget(self.device_config)

        self.engine_configuration: EngineEnvsConfiguration = EngineEnvsConfiguration()
        self.release_handler = ReleaseHandler(self.device,
                                              self.engine_configuration,
                                              nuvlaedge_version,
                                              deployment_branch,
                                              nuvlaedge_branch)

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

    def start_engine(self, nuvlaedge_uuid: NuvlaUUID,
                     remove_old_installation: bool = False,
                     extra_envs: dict = None):
        """

        :return:
        """
        if remove_old_installation:
            # 1. - Clean target
            self.logger.debug('Removing possible old installations of NuvlaEdge')
            self.device.clean_target()

        # 2. - Prepare remote files
        self.logger.debug('Download NuvlaEdge related files and images')
        self.release_handler.download_nuvlaedge()

        # 3. - Start engine with target release (Future custom as well)
        files: str = ' -f '.join(self.release_handler.get_files_path_as_str())
        start_command: str = cte.COMPOSE_UP.format(prepend='nohup',
                                                   project_name=cte.PROJECT_NAME,
                                                   files=files)

        self.logger.debug(f'Starting engine with command: \n\n\t{start_command}\n')

        self.engine_configuration.nuvlabox_uuid = nuvlaedge_uuid
        self.engine_configuration.nuvlaedge_uuid = nuvlaedge_uuid

        envs_configuration: dict = self.engine_configuration.model_dump(by_alias=True)

        if extra_envs:
            envs_configuration.update(extra_envs)

        self.logger.info(f'Starting NuvlaEdge with UUID: {nuvlaedge_uuid} with configuration: \n\n '
                         f'{json.dumps(envs_configuration, indent=4)} \n')
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
