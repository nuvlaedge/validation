"""
Constants file for the NuvlaEdge validator deployer
"""
from pathlib import Path

# Release handling
RELEASES_LINK: str = 'https://api.github.com/repos/nuvlaedge/deployment/releases'
RELEASE_DOWNLOAD_LINK: str = 'https://github.com/nuvlaedge/deployment/releases/' \
                             'download/{version}/{file}'

# File locations
GENERAL_CONFIG_PATH: Path = Path('/Users/nacho/PycharmProjects/temporal/deployer/conf')
DEVICE_CONFIG_PATH: Path = GENERAL_CONFIG_PATH / 'devices'
TESTS_CONFIG_PATH: Path = GENERAL_CONFIG_PATH / 'tests'

# Remote file locations
ROOT_PATH: str = '~/.nuvlaedge_validation'
ENGINE_PATH: str = '/engines/'
DEPLOYER_PATH: str = '/deployer/'
DEPLOYER_CONFIG_FILE: Path = GENERAL_CONFIG_PATH / '.deployer_config'

