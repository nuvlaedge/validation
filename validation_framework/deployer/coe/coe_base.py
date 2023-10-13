import logging
from abc import ABC, abstractmethod

from validation_framework.common.nuvla_uuid import NuvlaUUID
from validation_framework.common.schemas.engine import EngineEnvsConfiguration
from validation_framework.deployer.target_device.target import TargetDevice

from fabric import Result


class COEBase(ABC):

    def __init__(self, device: TargetDevice, logger: logging.Logger, **kwargs):
        self.logger: logging.Logger = logger
        self.device: TargetDevice = device

        self.engine_configuration: EngineEnvsConfiguration = EngineEnvsConfiguration()
        nuvlaedge_branch: str = ''
        nuvlaedge_version: str = ''
        deployment_branch: str = ''
        for key, value in kwargs.items():
            if key == 'nuvlaedge_branch':
                nuvlaedge_branch = value
            elif key == 'nuvlaedge_version':
                nuvlaedge_version = value
            elif key == 'deployment_branch':
                deployment_branch = value
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

        # Deployment release download link changes depending on the configuration.
        # Whether deployment branch is provided
        self.deployment_link: str = ''

    @abstractmethod
    def start_engine(self,
                     uuid: NuvlaUUID,
                     remove_old_installation: bool = True,
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
    def get_container_logs(self, container):
        pass

    @abstractmethod
    def engine_running(self) -> bool:
        pass

    @abstractmethod
    def remove_engine(self):
        pass

    @abstractmethod
    def purge_engine(self):
        pass

    def restart_system(self) -> Result:
        return self.device.run_sudo_command('sudo shutdown -r now')

    def get_system_up_time(self) -> float:
        result: Result = self.device.run_command("awk '{print $1}' /proc/uptime")
        if result.stdout:
            up_time = float(result.stdout)
            return up_time
        return 0.0
