"""
Engine controller
"""
import logging

import requests

from framework.deployer.common import Version
from framework.deployer.common.constants import *
from framework.deployer.device.device import Device
from framework.deployer.schemas.engine.engine import EngineSchema
from framework.deployer.schemas.release import ReleaseSchema


class EngineHandler:
    """

    """
    releases: dict[str, ReleaseSchema] = {}

    def __init__(self, device: Device, engine: EngineSchema):
        """

        :param device:
        """
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.gather_remote_releases()
        self.device: Device = device
        self.engine_configuration: EngineSchema = engine

    def gather_remote_releases(self):
        """
        Retrieves the available releases for NuvlaEdge and composes its download links
        """
        available_releases: requests.Response = requests.get(RELEASES_LINK)

        for release in available_releases.json():

            it_assets: list = [i.get('name') for i in release.get('assets') if i.get('name').endswith('.yml')]
            it_tag: str = release.get('tag_name')

            self.releases[Version(release.get('tag_name'))] = ReleaseSchema(version=it_tag,
                                                                            downloadable_assets=it_assets,
                                                                            downloaded=False,
                                                                            prerelease=release.get('prerelease'))

    def gather_downloaded_releases(self):
        ...

    def download_requested_releases(self):
        """
        Downloads the requested version of the device into the target device
        :return: None
        """
        req_release: ReleaseSchema = self.releases.get(self.engine_configuration.version)

        if not req_release:
            self.logger.error(f'Release requested {self.engine_configuration.version} not available in the current '
                              f'list {self.releases.keys()}')
            exit(1)

        target_path: str = ROOT_PATH + '/' + ENGINE_PATH + '/' + req_release.version
        self.device.run_command(f'mkdir -p {target_path}')

        for file_name in req_release.downloadable_assets:
            it_link: str = RELEASE_DOWNLOAD_LINK.format(version=req_release.version,
                                                        file=file_name)

            self.logger.info(f'Downloading with link: {it_link}')
            self.device.download_file(it_link, file_name, target_path)
            req_release.downloaded_components.append(file_name)

    def start_nuvlaedge(self):
        """
        Starts a NuvlaEdge on the target and preconfigured device
        :return: None
        """
        req_release: ReleaseSchema = self.releases.get(self.engine_configuration.version)
        files: str = " -f ".join(req_release.downloaded_components)
        base_command: str = f'docker-compose -p {self.engine_configuration.project_name} -f {files} up -d'
        command_location: str = ROOT_PATH + '/' + ENGINE_PATH + '/' + self.engine_configuration.version

        self.logger.info(f'Starting NuvlaEdge with command {base_command} in {command_location}')
        self.device.run_command_within_folder(base_command, command_location)

    def stop_nuvlaedge(self):
        """
        Stops the running nuvlaedge
        :return:
        """
        req_release: ReleaseSchema = self.releases.get(self.engine_configuration.version)
        files: str = " -f ".join(req_release.downloaded_components)
        base_command: str = f'docker-compose -p {self.engine_configuration.project_name} -f {files} down'
        command_location: str = ROOT_PATH + '/' + ENGINE_PATH + '/' + self.engine_configuration.version

        self.logger.info(f'Starting NuvlaEdge with command {base_command} in {command_location}')
        self.device.run_command_within_folder(base_command, command_location)

