import logging
from abc import ABC, abstractmethod

from validation_framework.common.nuvla_uuid import NuvlaUUID
from validation_framework.common.schemas.engine import EngineEnvsConfiguration
from validation_framework.deployer.target_device.target import TargetDevice


class COEBase(ABC):

    def __init__(self, device: TargetDevice, logger: logging.Logger):
        self.logger: logging.Logger = logger
        self.device: TargetDevice = device

        self.engine_configuration: EngineEnvsConfiguration = EngineEnvsConfiguration()

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
    def download_files(self):
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
    def engine_running(self):
        pass

    @abstractmethod
    def remove_engine(self):
        pass

    @abstractmethod
    def purge_engine(self):
        pass
