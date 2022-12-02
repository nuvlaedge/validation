"""
This module controls the NuvlaEdge release, the lack of release in favor of custom deployments. Also controls the
configuration of the deployment files in case of non-standard release and the environmental variables required to
start the NuvlaEdge (This may be better handled in the engine)
"""
import logging

import requests


from validation_framework.common import Release
from validation_framework.common.schemas.release import TargetReleaseConfig, ReleaseSchema
from validation_framework.common import constants as cte


class ReleaseHandler:

    requested_release: ReleaseSchema | None = None

    def __init__(self, release: Release | TargetReleaseConfig, std_release: bool = True):
        """
        If provided Release type provided, means we are aiming to a tagged release in GH,
        :param release: It can either be a standard release number or a Release configuration which allows for
        fine-grained selection of microservice version, name, etc
        """
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.config: TargetReleaseConfig = release
        self.release_tag = self.config.tag
        self.std_release: bool = self.config.std_release

    def gather_standard_release(self) -> bool:
        """
        Checks the remote GH repository for the releases and gathers the information according
        to the ReleaseSchema class
        :return: True if the release is successfully updated, false otherwise
        """
        available_releases: requests.Response = requests.get(cte.RELEASES_LINK)

        for release in available_releases.json():
            it_tag: str = release.get('tag_name')
            if it_tag == self.release_tag:
                self.requested_release = ReleaseSchema(
                    tag=Release(it_tag),
                    components=[i.get('name') for i in release.get('assets') if i.get('name').endswith('.yml')],
                    prerelease=release.get('prerelease')
                )
                return True

        return False

    def prepare_custom_release(self) -> None:
        """
        Based on a template (of an updated nuvlaedge release) allows to customize which images
        and tags are run in the Engine
        :return: None
        """
        # TODO: Future implementation of custom engine validation
        ...

    def get_download_cmd(self) -> list[str]:
        """
        Builds the corresponding download link of every requested component. Default: All
        :return: List of links to download the requested components and one with the fil names
        """
        if self.std_release and not self.requested_release:
            self.gather_standard_release()

        if self.std_release:
            gh_links: list[str] = []
            for c in self.requested_release.components:
                comp_link: str = cte.RELEASE_DOWNLOAD_LINK.format(version=self.requested_release.tag,
                                                                  file=c)
                gh_links.append(comp_link)

            return gh_links

        else:
            self.logger.error('Custom engine versions not implemented yet')
            raise NotImplementedError('Custom engine versions not implemented yet')

    def build_envs_configuration(self) -> dict:
        """

        :return:
        """
        self.logger.info('')
        return {}

