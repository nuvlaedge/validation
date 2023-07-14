"""
This module controls the NuvlaEdge release, the lack of release in favor of custom deployments. Also controls the
configuration of the deployment files in case of non-standard release and the environmental variables required to
start the NuvlaEdge (This may be better handled in the engine)
"""
import logging

import requests

from validation_framework.common import Release
from validation_framework.common.schemas.engine import EngineEnvsConfiguration
from validation_framework.common.schemas.release import TargetReleaseConfig, ReleaseSchema
from validation_framework.common import constants as cte
from validation_framework.deployer import SSHTarget


class ReleaseHandler:

    def __init__(self,
                 device: SSHTarget,
                 engine_configuration: EngineEnvsConfiguration,
                 nuvlaedge_version: str = '',
                 deployment_branch: str = '',
                 nuvlaedge_branch: str = ''):
        """
        Takes care of all the configuration related to the release, pre-release and devel versions of NuvlaEdge
        and deployment repositories. Depending on the parsed attributes, the configuration will change as follows:

        If nuvlaedge_branch is provided, the configuration of the docker-compose.yml files environmental variable
        changes as follows:
            -  NE_IMAGE_ORGANIZATION -> nuvladev
            -  NE_RELEASE_TAG -> branch name

        If deployment_branch is assigned, the compose files are downloaded from a branch instead of a release ignoring
        the possible parsed version

        If nuvlaedge_version is assigned without no branch (ne or deployment) is presents it means that the validation
        is a RELEASE VALIDATION and it should run only by tag name.

        If any of the branches are missing, nuvlaedge_version will be used instead (for either ne or deployment).
        In this case if no NuvlaEdge version is assigned, the latest (release or pre-release) tag will be taken and
        used following the previously mentioned process

        Args:
            device: SSH device class
            nuvlaedge_version (Optional): the selected nuvlaedge release tag
            deployment_branch (Optional): for development, the nuvlaedge branch to validate
            nuvlaedge_branch (Optional): for development, the deployment branch to validate
        """

        self.logger: logging.Logger = logging.getLogger(__name__)
        self.device: SSHTarget = device

        # NuvlaEdge source code configuration
        self.nuvlaedge_version = nuvlaedge_version
        self.deployment_branch = deployment_branch
        self.nuvlaedge_branch = nuvlaedge_branch

        # Deployment release download link changes depending on the configuration.
        # Whether deployment branch is provided
        self.deployment_link: str = ''

        # Remote files
        self.engine_folder: str = ''
        self.engine_files: list[str] = []

        self.engine_configuration: EngineEnvsConfiguration = engine_configuration

        # Generate source code configuration
        self.assess_nuvlaedge_sourcecode_configuration()

    def assess_nuvlaedge_sourcecode_configuration(self):
        """
        If nuvlaedge_branch is provided, the docker organization (NE_IMAGE_ORGANIZATION)
        becomes nuvladev and NE_RELEASE_TAG compose configuration becomes nuvlaedge_branch

        If deployment_branch is assigned, the compose files are downloaded from a branch instead of a release ignoring
        the possible parsed version

        If no nuvlaedge version is assigned, take the latest release. It is expected to always have deployment
        and nuvlaedge repo's releases in the same versions.
        """

        # ------------------------------------------------------------
        # Handle deployment repository configuration
        # ------------------------------------------------------------
        if self.deployment_branch:
            self.logger.info(f'Running NuvlaEdge from deployment branch: {self.deployment_branch}')
            self.deployment_link = cte.DEPLOYMENT_FILES_LINK.format(branch=self.deployment_branch,
                                                                    file='{file}')

        else:
            if not self.nuvlaedge_version:
                self.logger.info(
                    f'No deployment branch nor release version provided, gathering latest nuvlaedge release')
                self.nuvlaedge_version = self.get_latest_release(cte.NUVLAEDGE_RELEASES_LINK)

            self.logger.info(f'Running NuvlaEdge from deployment release version: {self.deployment_branch}')
            self.deployment_link = cte.RELEASE_DOWNLOAD_LINK.format(version=self.nuvlaedge_version,
                                                                    file='{file}')

        # ------------------------------------------------------------
        # Handle nuvlaedge repository configuration
        # ------------------------------------------------------------
        if self.nuvlaedge_branch:
            self.logger.info(f'Running NuvlaEdge source code from branch: nuvlaedge:{self.nuvlaedge_branch}')
            # Assign the branch to the nuvlaedge engine environmental variable configuration
            self.engine_configuration.ne_image_tag = self.nuvlaedge_branch

            # Engine env configuration changes the organization if we are in a dev branch
            self.engine_configuration.ne_image_organization = 'nuvladev'

        else:
            self.logger.info(f'Running NuvlaEdge source code on version {self.nuvlaedge_version}')
            self.engine_configuration.ne_image_tag = self.nuvlaedge_version

            # For standard release versions, the docker organization is SixSq
            self.engine_configuration.ne_image_organization = 'sixsq'

    def release_exists(self) -> bool:
        """
        Checks whether the release tag exists when is parsed as an input
        Returns:
            Bool
        """

    @staticmethod
    def get_latest_release(release_link: str) -> Release:
        available_releases: list = requests.get(release_link).json()
        if available_releases:
            return Release(available_releases[0].get('tag_name'))
        else:
            raise NotImplemented

    def download_nuvlaedge(self):
        """
        Downloads the deployment configuration files and pulls the image
        Returns:
            None
        """
        # ------------------------------------------------------------------------
        # Download compose files
        # ------------------------------------------------------------------------
        # Prepare target remote directory
        self.engine_folder = cte.ROOT_PATH + cte.ENGINE_PATH + self.nuvlaedge_version
        self.device.run_command(f'mkdir -p {self.engine_folder}')
        self.logger.info(f'Downloading deployment files into {self.engine_folder}')

        # Download deployment files
        engine_base_link = self.deployment_link.format(file=cte.ENGINE_BASE_FILE_NAME)
        if self.device.download_file(link=engine_base_link,
                                     file_name=cte.ENGINE_BASE_FILE_NAME,
                                     directory=self.engine_folder):

            self.engine_files.append(cte.ENGINE_BASE_FILE_NAME)

        # TODO: iterate here when peripheral validation is implemented to download the peripheral deployment file

        # ------------------------------------------------------------------------
        # Pull nuvlaedge image(s)
        # ------------------------------------------------------------------------
        self.device.run_command(f'docker compose -f {self.engine_folder + "/" + cte.ENGINE_BASE_FILE_NAME} pull',
                                envs=self.engine_configuration.model_dump(by_alias=True))

    def get_files_path_as_str(self) -> list[str]:
        """
        Combines the engine folder with the file names
        Returns:
            A list of full paths to the engine files
        Raises:
            NotFound if the files are not downloaded (variables not defined)
        """
        if not self.engine_folder or not self.engine_files:
            raise FileNotFoundError('Engine deployment files not downloaded')

        return [self.engine_folder + '/' + i for i in self.engine_files]

    def gather_standard_release(self) -> bool:
        """
        Checks the remote GH repository for the releases and gathers the information according
        to the ReleaseSchema class
        :return: True if the release is successfully updated, false otherwise
        """
        available_releases: requests.Response = requests.get(cte.RELEASES_LINK)
        if self.release_tag:
            # If specified, gather the given tag structure
            for release in available_releases.json():
                it_tag: str = release.get('tag_name')
                if it_tag == self.release_tag:
                    it_comp: list = []
                    for i in release.get('assets'):
                        if 'docker-compose.yml' in i.get('name'):
                            it_comp.append(i.get('name'))

                        # Add selected peripherals if any to the compose target lists
                        if self.config.peripherals:
                            if any([j in i.get('name') for j in self.config.peripherals]):
                                it_comp.append(i.get('name'))

                    self.requested_release = ReleaseSchema(
                        tag=Release(it_tag),
                        components=it_comp,
                        prerelease=release.get('prerelease')
                    )
                    return True
        else:
            serialized_releases: list = available_releases.json()
            it_tag: str = serialized_releases[0].get('tag_name')
            # If not specified get the latest version
            self.requested_release = ReleaseSchema(
                tag=Release(it_tag),
                components=[i.get('name') for i in serialized_releases[0].get('assets') if
                            i.get('name').endswith('.yml')],
                prerelease=serialized_releases[0].get('prerelease')
            )

        return False

    def get_download_cmd(self) -> list[str]:
        """
        Builds the corresponding download link of every requested component. Default: All
        :return: List of links to download the requested components and one with the fil names
        """
        # self.gather_standard_release()
        self.requested_release = ReleaseSchema(
            tag=Release(self.release_tag),
            components=['docker-compose.yml'],
            prerelease=False
        )

        gh_links: list[str] = []
        for c in self.requested_release.components:
            comp_link: str = cte.DEPLOYMENT_FILES_LINK.format(file=c)
            gh_links.append(comp_link)

        return gh_links

