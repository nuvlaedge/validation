"""
Device abstract class to allow the implementation of different ways of
connecting. E.g: Allow for experimental local deployments, remote with ssh or
remote with other techniques
"""
import logging
from abc import ABC, abstractmethod

import fabric

from common.schemas.engine import EngineConfig
from common.schemas.target_device import TargetDeviceConfig


class TargetDevice(ABC):
    """
    Device is considered any receptor of a NuvlaEdge engine, either via
    installer or via direct deployment
    """

    def __init__(self, target_config: TargetDeviceConfig, logger: logging.Logger):
        self.logger: logging.Logger = logger

        # General configuration from file
        self.target_config: TargetDeviceConfig = target_config

        # Easy access configuration
        self.hostname: str = self.target_config.hostname
        self.address: str = self.target_config.address
        self.user: str = self.target_config.user

    @abstractmethod
    def is_reachable(self) -> bool:
        """
        Checks whether the device is reachable from the framework standpoint
        :return: True is reachable, false otherwise
        """
        pass

    @abstractmethod
    def run_command(self, command: str, envs: dict | None = None) -> fabric.Result:
        """
        Executes a shell command and returns the standard output
        :param command: Command to be executed
        :param envs: Environmental variables to run within the command shell context
        :return: stdout if success, stderr if failed
        """
        pass

    @abstractmethod
    def run_command_within_folder(self, command: str, folder: str, envs: dict | None = None) -> fabric.Result:
        """
        Executes a shell command within a provided folder
        :param command: Command to be executed
        :param folder: Context folder in which to run the provided command
        :param envs: Environmental variables to run within the command shell context
        :return: stdout if success, stderr if failed
        """
        pass

    @abstractmethod
    def download_file(self, link: str, target_name: str, target_dir: str) -> bool:
        """
        Downloads a file into target_dir/target_name from the provided link
        :param link: Link hosting the file to be downloaded
        :param target_name: Target file name
        :param target_dir: Target folder
        :return: True if successfully downloaded, false otherwise
        """
        pass

    @abstractmethod
    def clean_target(self) -> None:
        """
        Removes docker containers, services, volumes and networks from previous runs
        :return: None
        """
        ...
    # @abstractmethod
    # def start_engine(self, engine_config: EngineConfig, project_name: str) -> bool:
    #     """
    #     Starts the engine depending on what device in being used
    #     :return: True if successfully started, false otherwise
    #     """
    #     pass
    #
    # @abstractmethod
    # def stop_engine(self, project_name: str) -> bool:
    #     """
    #     Stops the NuvlaEdge engine with the provided project name
    #     :param project_name: Project name to stop
    #     :return: True if successfully stopped
    #     """
    #     pass

    @abstractmethod
    def build_directory_tree(self) -> None:
        """
        Builds the different directories used by the validation system
        :return: None
        """

    # Validation retrieval
    @abstractmethod
    def get_logs(self) -> None:
        """
        Retrieves all the logs from the deployed target_device engine
        :return: None
        """
        pass

    @abstractmethod
    def get_ms_logs(self, microservice: str) -> None:
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