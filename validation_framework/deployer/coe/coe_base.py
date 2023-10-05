import logging
from abc import ABC, abstractmethod

from validation_framework.common.nuvla_uuid import NuvlaUUID
from validation_framework.common.schemas.engine import EngineEnvsConfiguration
from validation_framework.deployer.target_device.target import TargetDevice

from fabric import Result


class COEBase(ABC):

    def __init__(self, device: TargetDevice, logger: logging.Logger):
        self.logger: logging.Logger = logger
        self.device: TargetDevice = device

        self.engine_configuration: EngineEnvsConfiguration = EngineEnvsConfiguration()

    def set_engine_configuration(self, config: EngineEnvsConfiguration):
        self.engine_configuration = config

    @abstractmethod
    def start_engine(self,
                     uuid: NuvlaUUID,
                     files_path: list[str],
                     remove_old_installation: bool = True,
                     extra_envs: dict = None):
        """

        Returns:

        """
        pass

    @abstractmethod
    def download_files(self, source, version) -> list[str]:
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
