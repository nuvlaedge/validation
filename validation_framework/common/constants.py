"""
Constants common module for the NuvlaEdge validation system
"""

from pathlib import Path

# Release handling
DEPLOYMENT_RELEASES_LINK: str = 'https://api.github.com/repos/nuvlaedge/deployment/releases'
NUVLAEDGE_RELEASES_LINK: str = 'https://api.github.com/repos/nuvlaedge/nuvlaedge/releases'

RELEASE_DOWNLOAD_LINK: str = 'https://github.com/nuvlaedge/deployment/releases/' \
                             'download/{version}/{file}'
DEPLOYMENT_FILES_LINK: str = 'https://raw.githubusercontent.com/nuvlaedge/deployment/{branch_name}/{file}'

ENGINE_BASE_FILE_NAME: str = 'docker-compose.yml'
PERIPHERAL_BASE_FILE_NAME: str = 'docker-compose.{peripheral}.yml'

# Kubernetes
NUVLAEDGE_KUBE_REPO: str = 'https://nuvlaedge.github.io/deployment'
NUVLAEDGE_KUBE_LOCAL_REPO_NAME: str = 'nuvlaedge'
NUVLAEDGE_KUBE_LOCAL_CHART_NAME: str = 'nuvlaedge'
NUVLAEDGE_KUBE_INSTALL_IMAGE: str = ('sudo helm install nuvlaedge-{uuid} {repo}/{chart} --version {version} '
                                     '--set NUVLAEDGE_UUID=nuvlabox/{uuid} --set vpnClient=true '
                                     '--set kubernetesNode={hostname}')
NUVLAEDGE_KUBE_CERTIFICATE_MANAGER: str = 'kubernetes-credentials-manager'
NUVLAEDGE_KUBE_CSR_NAME_KEY: str = 'CSR_NAME'
NUVLAEDGE_KUBE_CREDENTIAL_CHECK_INTERVAL: int = 5  # seconds

# File locations
GENERAL_CONFIG_PATH: Path = Path('./conf/').resolve()
DEVICE_CONFIG_PATH: Path = GENERAL_CONFIG_PATH / 'targets'
ENGINE_CONFIG_PATH: Path = GENERAL_CONFIG_PATH / 'engines'
TESTS_CONFIG_PATH: Path = GENERAL_CONFIG_PATH / 'tests'

# Remote file locations
ROOT_PATH: str = '~/.nuvlaedge_validation'
ENGINE_PATH: str = '/engines/'
DEPLOYER_PATH: str = '/deployer/'
DEPLOYER_CONFIG_FILE: Path = GENERAL_CONFIG_PATH / '.deployer_config'

# STD Commands
COMPOSE_UP: str = '{prepend} docker compose -p {project_name} -f {files} up -d'
COMPOSE_DOWN: str = 'docker compose -p {project_name} -f {files} down -d'

# NuvlaEdge engine configuration constants
PROJECT_NAME: str = 'nuvlaedge_validator'
NUVLAEDGE_NAME: str = '[{device}] Validation'
DOCKER_REPOSITORY_NAME: str = 'nuvlaedge'

# Report paths
RESULTS_PATH: Path = Path('./results/temp/').resolve()
JSON_RESULTS_PATH: Path = RESULTS_PATH / 'json'
XML_RESULTS_PATH: Path = RESULTS_PATH / 'xml'

# Timeouts
DEFAULT_JOBS_TIMEOUT: int = 3 * 60
DEFAULT_DEPLOYMENTS_TIMEOUT: int = 5 * 60
