"""
Device abstract class to allow the implementation of different ways of
connecting. E.g: Allow for experimenta local deployments, remote with ssh or
remote with other techniques
"""
import logging
from abc import ABC, abstractmethod

import fabric

from framework.deployer.schemas.device import DeviceConfig
from framework.deployer.schemas.release import ReleaseSchema


class Device(ABC):
    """
    Device is considered any receptor of a NuvlaEdge engine, either via
    installer or via direct deployment
    """

    def __init__(self, device_config: DeviceConfig, logger: logging.Logger):
        self.logger: logging.Logger = logger

        # General configuration from file
        self.device_config: DeviceConfig = device_config

        # Easy access configuration
        self.hostname: str = self.device_config.hostname
        self.address: str = self.device_config.address
        self.user: str = self.device_config.user

    @abstractmethod
    def is_reachable(self) -> bool:
        """
        Checks whether the device is reachable from the framework standpoint
        :return: True is reachable, false otherwise
        """
        pass

    @abstractmethod
    def start_engine(self, release_schema: ReleaseSchema, project_name: str) -> bool:
        """
        Starts the engine depending on what device in being used
        :return: True if successfully started, false otherwise
        """

    @abstractmethod
    def stop_engine(self) -> bool:
        """
        Stop an engine
        :return: None
        """

    @abstractmethod
    def run_command(self, command: str) -> fabric.Result:
        """

        :param command:
        :return:
        """

    @abstractmethod
    def run_command_within_folder(self, command: str, folder: str) -> fabric.Result:
        """

        :param command:
        :param folder:
        :return:
        """

    @abstractmethod
    def download_file(self, link: str, target_name: str, target_dir: str) -> bool:
        """

        :param link:
        :param target_name:
        :param target_dir:
        :return:
        """

    @abstractmethod
    def build_directory_tree(self) -> None:
        """
        Builds the different directories used by the validation system
        :return:
        """

    @abstractmethod
    def get_logs(self) -> None:
        """
        Retrieves all the logs from the deployed target_device engine
        :return: None
        """
        pass

    @abstractmethod
    def get_ms_logs(self, microservice) -> None:
        """
        Retrieves the logs from the selected microservice
        :param microservice: Microservice to retrieve the logs from
        :return: None
        """
        pass

    @abstractmethod
    def get_engine_db(self) -> None:
        """
        Retrieves the whole target_device engine database
        :return: None
        """
