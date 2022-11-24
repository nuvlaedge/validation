"""
Constants common module for the NuvlaEdge validation system
"""

from pathlib import Path

# Release handling
RELEASES_LINK: str = 'https://api.github.com/repos/nuvlaedge/deployment/releases'
RELEASE_DOWNLOAD_LINK: str = 'https://github.com/nuvlaedge/deployment/releases/' \
                             'download/{version}/{file}'

# File locations
GENERAL_CONFIG_PATH: Path = Path('~/PycharmProjects/nuvlaedge/devel/validation/conf').expanduser()
DEVICE_CONFIG_PATH: Path = GENERAL_CONFIG_PATH / 'targets'
ENGINE_CONFIG_PATH: Path = GENERAL_CONFIG_PATH / 'engines'
TESTS_CONFIG_PATH: Path = GENERAL_CONFIG_PATH / 'tests'
LOGGING_CONFIG_FILE: Path = GENERAL_CONFIG_PATH / 'validation_logging.ini'

# Remote file locations
ROOT_PATH: str = '~/.nuvlaedge_validation'
ENGINE_PATH: str = '/engines/'
DEPLOYER_PATH: str = '/deployer/'
DEPLOYER_CONFIG_FILE: Path = GENERAL_CONFIG_PATH / '.deployer_config'

# STD Commands
COMPOSE_UP: str = '{prepend} docker-compose -p {project_name} -f {files} up -d'
COMPOSE_DOWN: str = 'docker-compose -p {project_name} -f {files} down -d'

# NuvlaEdge engine configuration constants
PROJECT_NAME: str = 'NuvlaEdge_Validator'
NUVLAEDGE_NAME: str = '[{device}] Validation'
