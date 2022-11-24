"""
Device SSH implementation
"""
import logging

import fabric
from fabric import Connection

from fabric.runners import Result

from framework.deployer.common.constants import *
from framework.deployer.device.device import Device
from framework.deployer.schemas.device import DeviceConfig
from framework.deployer.schemas.release import ReleaseSchema


class SSHDevice(Device):

    def stop_engine(self) -> bool:
        pass

    def __init__(self, device_config: DeviceConfig):
        """
        Constructor of the SSH type device
        :param device_config: Initial device Configuration
        """
        super().__init__(device_config, logging.getLogger(self.__class__.__name__))

        self.connection: Connection = Connection(host=self.address,
                                                 user=self.user,
                                                 connect_timeout=3,
                                                 connect_kwargs={
                                                     "password": device_config.password})

    def clean_target(self):
        """
        Removes docker containers, services, volumes and networks from previous runs
        :return: None
        """
        self.run_command('docker controller rm $(docker controller ls -q)')
        self.run_command('docker stop $(docker ps -a -q)')
        self.run_command('docker rm $(docker ps -a -q)')
        self.run_command('docker network prune --force')
        self.run_command('docker volume prune --force')

    def is_reachable(self) -> bool:
        try:
            self.logger.info('Running connection')
            it: Result = self.connection.run('hostname', hide=True)
            self.hostname = it.stdout.strip()
            self.logger.info(f'Host {self.hostname} reachable')
        except TimeoutError:
            self.logger.error(f'Host address {self.address} not reachable')
            return False

        return self.connection.is_connected

    def run_command(self, command: str) -> fabric.Result:

        return self.connection.run(command, hide=True)

    def run_command_within_folder(self, command: str, folder: str) -> fabric.Result:
        with self.connection.cd(folder):
            return self.run_command(command)

    def new_connection(self) -> Connection:
        """
        Creates and returns a new connection
        :return:
        """
        return Connection(host=self.address,
                          user=self.user,
                          connect_timeout=3,
                          connect_kwargs={"password": self.device_config.password})

    def download_file(self, link: str, target_name: str, target_dir: str) -> bool:
        """
        Downl
        :param link:
        :param target_name:
        :param target_dir:
        :return:
        """
        # Download with either wget or curl
        download_result: Result = self.run_command(f'wget {link} -t 3 -T 5 -O {target_dir}/{target_name}')

        return not download_result.failed

    def build_directory_tree(self):
        # check main folder
        self.connection.run(f'mkdir -p {ROOT_PATH}')

        # check subdirectories
        self.connection.run(f'mkdir -p {ROOT_PATH + DEPLOYER_PATH}')
        self.connection.run(f'mkdir -p {ROOT_PATH + ENGINE_PATH}')

    def start_engine(self, release_schema: ReleaseSchema, project_name: str) -> bool:
        """

        :return:
        """
        req_release: ReleaseSchema = self.releases.get(self.engine_configuration.version)
        files: str = " -f ".join(req_release.downloaded_components)

    def get_logs(self) -> None:
        pass

    def get_ms_logs(self, microservice) -> None:
        pass

    def get_engine_db(self) -> None:
        pass
