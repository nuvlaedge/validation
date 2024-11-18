import logging
from abc import ABC, abstractmethod

from validation_framework.common import constants
from validation_framework.common.nuvla_uuid import NuvlaUUID
from validation_framework.common.schemas.engine import EngineEnvsConfiguration
from validation_framework.deployer.target_device.target import TargetDevice

from fabric import Result
from pathlib import Path


class COEBase(ABC):

    def __init__(self, device: TargetDevice, logger: logging.Logger, **kwargs):
        self.logger: logging.Logger = logger
        self.device: TargetDevice = device

        self.project_name: str = kwargs.get('project_name', constants.PROJECT_NAME)
        self.engine_env: list[str] = []

        self.engine_configuration: EngineEnvsConfiguration = EngineEnvsConfiguration()
        nuvlaedge_branch: str = kwargs.get('nuvlaedge_branch', '')
        nuvlaedge_version: str = kwargs.get('nuvlaedge_version', '')
        deployment_branch: str = kwargs.get('deployment_branch', '')
        self.include_peripherals = kwargs.get('include_peripherals', False)
        self.peripherals: list[str] = kwargs.get('peripherals', [])

                # NuvlaEdge source code configuration
        self.nuvlaedge_version = nuvlaedge_version.strip() if nuvlaedge_version else ''
        self.deployment_branch = deployment_branch.strip() \
            if deployment_branch and deployment_branch != 'None' else ''
        self.nuvlaedge_branch = nuvlaedge_branch.strip() \
            if nuvlaedge_branch and nuvlaedge_branch != 'None' else ''
        self.logger.info(f'\n\t Engine configuration: \n'
                         f'\t\t NuvlaEdge Version: {self.nuvlaedge_version} \n'
                         f'\t\t Deployment Branch: {self.deployment_branch} \n'
                         f'\t\t NuvlaEdge Branch: {self.nuvlaedge_branch}')

        # ------------------------------------------------------------
        # Handle nuvlaedge repository configuration
        # ------------------------------------------------------------
        if self.nuvlaedge_branch:
            self.logger.info(f'Running NuvlaEdge source code from branch: '
                             f'nuvlaedge:{self.nuvlaedge_branch}')
            # Assign the branch to the nuvlaedge engine environmental variable
            # configuration
            self.engine_configuration.ne_image_tag = self.nuvlaedge_branch

            # Engine env configuration changes the organization if we are in a dev branch
            self.engine_configuration.ne_image_organization = 'nuvladev'

        else:
            self.logger.info(f'Running NuvlaEdge source code on version '
                             f'{self.nuvlaedge_version}')
            self.engine_configuration.ne_image_tag = self.nuvlaedge_version

            # For standard release versions, the docker organization is SixSq
            self.engine_configuration.ne_image_organization = 'sixsq'

        # Deployment release download link changes depending on the configuration.
        # Whether deployment branch is provided
        self.deployment_link: str = ''

    @abstractmethod
    def start_engine(self,
                     uuid: NuvlaUUID,
                     remove_old_installation: bool = True,
                     project_name: str = constants.PROJECT_NAME,
                     extra_envs: dict = None):
        """

        Returns:

        """
        pass

    @abstractmethod
    def add_peripheral(self):
        pass

    @abstractmethod
    def remove_peripheral(self):
        pass

    @abstractmethod
    def stop_engine(self):
        pass

    @abstractmethod
    def get_engine_logs(self):
        pass

    @abstractmethod
    def get_container_logs(self, container, download_to_local=False, path: Path = None):
        pass

    @abstractmethod
    def engine_running(self) -> bool:
        pass

    @abstractmethod
    def remove_engine(self, uuid: NuvlaUUID = None):
        pass

    @abstractmethod
    def purge_engine(self, uuid: NuvlaUUID = None):
        pass

    @abstractmethod
    def get_coe_type(self):
        pass

    @abstractmethod
    def peripherals_running(self, peripherals: set) -> bool:
        pass

    @abstractmethod
    def get_authorized_keys(self):
        pass

    @abstractmethod
    def finish_tasks(self):
        pass

    def restart_system(self) -> Result:
        return self.device.run_sudo_command('sudo shutdown -r now')

    def get_system_up_time(self) -> float:
        result: Result = self.device.run_command("awk '{print $1}' /proc/uptime")
        if result.stdout:
            up_time = float(result.stdout)
            return up_time
        return 0.0
