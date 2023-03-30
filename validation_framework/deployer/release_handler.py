"""
This module controls the NuvlaEdge release, the lack of release in favor of custom deployments. Also controls the
configuration of the deployment files in case of non-standard release and the environmental variables required to
start the NuvlaEdge (This may be better handled in the engine)
"""
import logging
from pathlib import Path

import requests
import ruamel.yaml

from validation_framework.common import Release
from validation_framework.common.schemas.release import TargetReleaseConfig, ReleaseSchema
from validation_framework.common import constants as cte


class ReleaseHandler:

    requested_release: ReleaseSchema | None = None

    def __init__(self, release: TargetReleaseConfig):
        """
        If provided Release type provided, means we are aiming to a tagged release in GH,
        :param release: It can either be a standard release number or a Release configuration which allows for
        fine-grained selection of microservice version, name, etc
        """
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.config: TargetReleaseConfig = release
        self.release_tag = self.config.tag

    @staticmethod
    def get_latest_release() -> Release:
        available_releases: list = requests.get(cte.RELEASES_LINK).json()
        if available_releases:
            return Release(available_releases[0].get('tag_name'))

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
                        # components=[i.get('name') for i in release.get('assets') if i.get('name').endswith('.yml')],
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

    def prepare_custom_release(self, directory: str) -> None:
        """
        Locally prepares the release for branch pull requests, then pushes it to the target.
        :return: None
        """
        # Not a standard release, means the test is being triggered by a Pull Request. Then, after downloading the
        # corresponding files, we need to edit the given image
        engine_file: Path = Path(directory) / 'docker-compose.yml'
        engine_file = engine_file.expanduser()
        if not engine_file.exists():
            raise FileNotFoundError(f'Target file {engine_file} does not exist')

        yaml = ruamel.yaml.YAML()
        yaml.preserve_quotes = True
        yaml.indent(sequence=3, offset=1)

        with engine_file.open('r') as file:
            compose_config = yaml.load(file)
            compose_config['services'][self.config.repository]['image'] = \
                f"nuvladev/{self.config.repository}:{self.config.branch}"

        with engine_file.open('w') as file:
            yaml.dump(compose_config, file)

    def get_download_cmd(self) -> list[str]:
        """
        Builds the corresponding download link of every requested component. Default: All
        :return: List of links to download the requested components and one with the fil names
        """
        self.gather_standard_release()

        gh_links: list[str] = []
        for c in self.requested_release.components:
            comp_link: str = cte.RELEASE_DOWNLOAD_LINK.format(version=self.requested_release.tag,
                                                              file=c)
            gh_links.append(comp_link)

        return gh_links

    def build_envs_configuration(self) -> dict:
        """

        :return:
        """
        self.logger.info('')
        return {}

