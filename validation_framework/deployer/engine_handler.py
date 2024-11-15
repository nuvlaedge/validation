"""
Higher class that wraps together the device and the release handler
"""
import json
import logging
from pathlib import Path
from fabric import Result

import fabric

from validation_framework.common import utils
from validation_framework.common.nuvla_uuid import NuvlaUUID
from validation_framework.common.schemas.engine import EngineEnvsConfiguration
from validation_framework.common.schemas.target_device import TargetDeviceConfig
from validation_framework.common import constants as cte
from validation_framework.deployer.coe import coe_base, coe_factory


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
        Engine handler constructor. It is in charge of assessing if the targets are
        passed as index or path to file. If an index is passed has to find the
        corresponding file in the default folder, if it's a path, directly loads the
        configuration.
        :param target_device: Index or path to target device file
        :param nuvlaedge_version: Release version. Synchronized between NuvlaEdge and
        Deployment repository
        """
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.logger.debug(f'Creating Engine Handler for device {target_device}')

        # Assess device configuration
        device_config_file: Path = target_device
        if not device_config_file.is_file():
            raise FileNotFoundError(f'Provided file {device_config_file} '
                                    f'does not exists')

        self.device_config: TargetDeviceConfig = utils.get_model_from_toml(
            TargetDeviceConfig,
            device_config_file)
        self.coe: coe_base = coe_factory(self.device_config, nuvlaedge_version=nuvlaedge_version,
                                         deployment_branch=deployment_branch,
                                         nuvlaedge_branch=nuvlaedge_branch,
                                         include_peripherals=include_peripherals,
                                         peripherals=peripherals)

        self.engine_configuration: EngineEnvsConfiguration = EngineEnvsConfiguration()

    @property
    def coe_type(self) -> str:
        return self.coe.get_coe_type()

    @staticmethod
    def get_device_config_by_index(device_index: int) -> Path:
        """

        :param device_index: Numerical index to identify specific device configurations
        :return: The file location
        """
        for file in cte.DEVICE_CONFIG_PATH.iterdir():
            if file.is_file() and file.name.startswith(str(device_index)):
                return cte.DEVICE_CONFIG_PATH / file

        raise IndexError(f'Device with index {device_index} not found in '
                         f'{cte.DEVICE_CONFIG_PATH}')

    def start_engine(self, nuvlaedge_uuid: NuvlaUUID,
                     remove_old_installation: bool = False,
                     extra_envs: dict = None):
        """

        :return:
        """
        if remove_old_installation:
            # 1. - Clean target
            self.logger.info('Removing possible old installations of NuvlaEdge')
            self.coe.purge_engine(nuvlaedge_uuid)

        # 2. Start Engine
        self.logger.info('Download NuvlaEdge related files and images')
        self.coe.start_engine(nuvlaedge_uuid, False, extra_envs)

    def get_system_up_time_in_engine(self) -> float:
        return self.coe.get_system_up_time()

    def restart_engine(self) -> Result:
        return self.coe.restart_system()

    def stop_engine(self, retrieve_logs: bool = False) -> bool:
        """

        :return:
        """
        if not self.coe.engine_running():
            self.logger.info('Engine not running')
            self.coe.finish_tasks()
            return True

        if retrieve_logs:
            self.coe.get_engine_logs()

        self.coe.purge_engine()

    def check_if_peripherals_running(self, peripherals: set) -> bool:
        """
            Check if all the peripherals are running in the device
            peripherals need to be given in lowercase
        :param peripherals:
        :return:
        """
        return self.coe.peripherals_running(peripherals)
