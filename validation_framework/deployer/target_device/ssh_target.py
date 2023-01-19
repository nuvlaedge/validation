"""
Target Device SSH implementation
"""
import os
import logging
from contextlib import contextmanager

import fabric
from fabric import Connection
import invoke

from validation_framework.common.constants import *
from validation_framework.common.nuvla_uuid import NuvlaUUID
from validation_framework.common.schemas.target_device import TargetDeviceConfig
from validation_framework.deployer.target_device.target import TargetDevice


class SSHTarget(TargetDevice):
    SUDO_PASS = invoke.Responder(pattern=r'\[sudo\] password:',
                                 response='pi\n')

    def __init__(self, target_config: TargetDeviceConfig):
        """
        SSH target_device device constructor
        :param target_config: Target device configuration stored in the parent class
        """
        super().__init__(target_config, logging.getLogger(__name__))

        if not self.is_reachable():
            self.logger.debug(f'Device {self.target_config.alias} not reachable in {self.target_config.address} ')
            raise ConnectionError(f'Device {self.target_config.alias} not reachable in {self.target_config.address} ')
        else:
            self.logger.info(f'Device {self.target_config.alias} online and ready')
            self.build_directory_tree()

    @contextmanager
    def connection(self) -> Connection:

        new_connection: Connection = Connection(host=self.address,
                                                user=self.user,
                                                connect_timeout=3,
                                                connect_kwargs={
                                                    "key_filename": os.path.expanduser(
                                                                        self.target_config.private_key_path)})
        yield new_connection
        new_connection.close()

    def is_reachable(self, silent=False) -> bool:
        try:
            if not silent:
                self.logger.info('Running connection')
            it_result: fabric.Result = self.run_command('hostname')
            if not silent:
                self.hostname = it_result.stdout.strip()
                self.logger.info(f'Host {self.hostname} reachable')
            return not it_result.failed
        except TimeoutError:
            self.logger.error(f'Host address {self.address} not reachable')
            return False

    def build_directory_tree(self) -> None:
        # check main folder
        with self.connection() as connection:
            connection.run(f'mkdir -p {ROOT_PATH}')

            # check subdirectories
            connection.run(f'mkdir -p {ROOT_PATH + DEPLOYER_PATH}')
            connection.run(f'mkdir -p {ROOT_PATH + ENGINE_PATH}')

    def send_file(self, local_file: str, remote_path: str):
        """

        :param remote_path:
        :param local_file:
        :return: None
        """
        self.logger.info(f'Transfering {local_file} to {remote_path}')
        with self.connection() as connection:
            self.logger.info(f'Some random data {connection.put(local_file, remote=remote_path)}')

    def get_logs(self) -> None:
        pass

    def get_ms_logs(self, microservice: str) -> None:
        pass

    def get_engine_db(self) -> None:
        pass

    def run_sudo_command(self, command: str, envs: dict | None = None) -> fabric.Result:
        self.logger.debug(f'Running {command} as SuperUser in {self.target_config.address}')
        with self.connection() as connection:
            return connection.run(command, env=envs, hide=True, watchers=[self.SUDO_PASS])

    def run_command(self, command: str, envs: dict | None = None) -> fabric.Result:

        self.logger.debug(f'Running {command} in {self.target_config.address}')
        with self.connection() as connection:
            return connection.run(command, env=envs, hide=True)

    def run_command_within_folder(self, command: str, folder: str, envs: dict | None = None) -> fabric.Result:

        self.logger.debug(f'Running {command} in {self.target_config.address} within {folder} folder')
        with self.connection() as connection:
            with connection.cd(folder):
                return connection.run(command, env=envs, hide=True)

    def download_file(self, link: str, file_name: str, directory: str) -> bool:
        download_result: fabric.Result = self.run_command(f'wget {link} -t 3 -T 5 -O {directory}/{file_name}')

        return not download_result.failed

    def clean_target(self):
        """
        Removes docker containers, services, volumes and networks from previous runs
        :return: None
        """
        command_list: list = ['docker service rm $(docker service ls -q)',
                              'docker stop $(docker ps -a -q)',
                              'docker rm $(docker ps -a -q)',
                              'docker network prune --force',
                              'docker volume prune --force']

        for cmd in command_list:
            try:
                self.run_command(cmd)
            except invoke.exceptions.UnexpectedExit:
                pass
            except Exception as ex:
                self.logger.warning(f'System not present {ex}')

    def start_edge(self, nuvlaedge_uuid: NuvlaUUID) -> None:
        """
        Starts a nuvla edge given the UUID in the target device. This function should not block and return once
        the engine has been started
        :param nuvlaedge_uuid: NuvlaEdge engine to start the engine wiht
        :return:  None
        """
        start_command: str = f'nohup docker-compose -p {"nuvlaedge"} -f {"docker-compose.yml"} up -d'
        self.run_command_within_folder(start_command,
                                       'some_folder_where the file is',
                                       envs={'NUVLABOX_UUID': nuvlaedge_uuid,
                                             'NUVLAEDGE_UUID': nuvlaedge_uuid})

    def stop_edge(self):
        """
        Stops the started engine
        :return:
        """
        stop_command: str = f''
