"""
Target Device SSH implementation
"""
import json
import os
import logging
from contextlib import contextmanager

import fabric
from fabric import Connection, Result
import invoke

from validation_framework.common.constants import *
from validation_framework.common.nuvla_uuid import NuvlaUUID
from validation_framework.common.schemas.target_device import TargetDeviceConfig
from validation_framework.deployer.target_device.target import TargetDevice


class SSHTarget(TargetDevice):
    SUDO_PASS = invoke.Responder(pattern=r'\[sudo\] password.*?',
                                 response='pi\n')

    def __init__(self, target_config: TargetDeviceConfig):
        """
        SSH target_device device constructor
        :param target_config: Target device configuration stored in the parent class
        """
        super().__init__(target_config, logging.getLogger(__name__))
        self.logger.info(f'Starting SSH target with configuration '
                         f'{json.dumps(target_config.dict(), indent=4)}')
        if not self.is_reachable():
            self.logger.debug(f'Device {self.target_config.alias} not reachable in {self.target_config.address} ')
            raise ConnectionError(f'Device {self.target_config.alias} not reachable in {self.target_config.address} ')
        else:
            self.logger.info(f'Device {self.target_config.alias} online and ready')
            self.build_directory_tree()

    @contextmanager
    def connection(self) -> Connection:
        new_connection: Connection = Connection(
            host=self.address,
            user=self.user,
            connect_timeout=30,
            connect_kwargs={
                "key_filename":
                    os.path.expanduser(self.target_config.private_key_path)
            }
        )
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
        except Exception as ex:
            self.logger.error(f'Host address {self.address} not reachable {ex}')
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
        self.logger.debug(f'Transferring {local_file} to {remote_path}')
        with self.connection() as connection:
            result: fabric.Result = connection.put(local_file, remote=remote_path)

    def download_remote_file(self, remote_file_path: str, local_file_path: Path) -> str | None:
        """
        Given a path on the remote ssh target device, retrieves the content of the file if exists.
        Args:
            remote_file_path: file to download from the remote device
            local_file_path:

        Returns:
            The local path where the file is stored. None if the file doesn't exist
        """

        with self.connection() as connection:
            res: Result = connection.get(remote_file_path, local=str(local_file_path))

    def run_sudo_command(self, command: str, envs: dict | None = None, hide: bool = True) -> fabric.Result:
        self.logger.debug(f'Running {command} as SuperUser in {self.target_config.address}')
        with self.connection() as connection:
            return connection.run(command, pty=False, env=envs, hide=hide, watchers=[self.SUDO_PASS])

    def run_command(self, command: str, envs: dict | None = None, hide: bool = True) -> fabric.Result:

        self.logger.debug(f'Running {command} in {self.target_config.address}')
        with self.connection() as connection:
            return connection.run(command, env=envs, hide=hide)

    def run_command_within_folder(self, command: str, folder: str, envs: dict | None = None) -> fabric.Result:

        self.logger.debug(f'Running {command} in {self.target_config.address} within {folder} folder')
        with self.connection() as connection:
            with connection.cd(folder):
                return connection.run(command, env=envs, hide=True)

    def download_file(self, link: str, file_name: str, directory: str) -> bool:
        download_result: fabric.Result = self.run_command(f'wget {link} -t 3 -T 5 -O {directory}/{file_name}')

        return not download_result.failed
