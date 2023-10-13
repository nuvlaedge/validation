"""
This module controls the NuvlaEdge release, the lack of release in favor of custom
deployments. Also controls the configuration of the deployment files in case of
non-standard release and the environmental variables required to
start the NuvlaEdge (This may be better handled in the engine)
"""
import logging

import requests

from validation_framework.common import Release
from validation_framework.common.schemas.engine import EngineEnvsConfiguration
from validation_framework.common.schemas.release import ReleaseSchema
from validation_framework.common import constants as cte
from validation_framework.deployer.coe import coe_base


class ReleaseHandler:

    def __init__(self,
                 coe: coe_base,
                 engine_configuration: EngineEnvsConfiguration,
                 nuvlaedge_version: str = '',
                 deployment_branch: str = '',
                 nuvlaedge_branch: str = ''):
        """
        Takes care of all the configuration related to the release, pre-release and devel
         versions of NuvlaEdge and deployment repositories. Depending on the parsed
         attributes, the configuration will change as follows:

        If nuvlaedge_branch is provided, the configuration of the docker-compose.yml
        files environmental variable changes as follows:
            -  NE_IMAGE_ORGANIZATION -> nuvladev
            -  NE_RELEASE_TAG -> branch name

        If deployment_branch is assigned, the compose files are downloaded from a branch
         instead of a release ignoring the possible parsed version

        If nuvlaedge_version is assigned without no branch (ne or deployment) is presents
         it means that the validation is a RELEASE VALIDATION and it should run only by
         tag name.

        If any of the branches are missing, nuvlaedge_version will be used instead
         (for either ne or deployment). In this case if no NuvlaEdge version is assigned,
         the latest (release or pre-release) tag will be taken and used following the
         previously mentioned process

        Args:
            device: SSH device class
            nuvlaedge_version (Optional): the selected nuvlaedge release tag
            deployment_branch (Optional): for development, the nuvlaedge branch to validate
            nuvlaedge_branch (Optional): for development, the deployment branch to validate
        """

        self.logger: logging.Logger = logging.getLogger(__name__)
        self.coe: coe_base = coe

        # Remote files
        self.engine_files: list[str] = []

    def release_exists(self) -> bool:
        """
        Checks whether the release tag exists when is parsed as an input
        Returns:
            Bool
        """

    def gather_standard_release(self) -> bool:
        """
        Checks the remote GH repository for the releases and gathers the information
         according to the ReleaseSchema class
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

