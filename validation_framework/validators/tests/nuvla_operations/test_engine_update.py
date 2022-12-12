"""

"""
import time
from pprint import pprint as pp
from nuvla.api.models import CimiResource, CimiResponse, CimiCollection

from validation_framework.validators.tests.nuvla_operations import validator
from validators import ValidationBase

sample_dict: dict = {
                    'project-name': 'nuvlaedge_validator',
                    'working-dir': '/home/ubuntu/.nuvlaedge_validation/engines/2.4.3',
                    'environment': [
                        'SKIP_MINIMUM_REQUIREMENTS=False',
                        'DOCKER_CHANNEL=stable',
                        'NUVLABOX_ENGINE_VERSION=2.4.3',
                        'HOST=nuvlabox',
                        'PYTHON_PIP_VERSION=21.1.2',
                        'NUVLABOX_UUID=nuvlabox/34414b92-ad0f-498a-ba09-b7a10e38902c',
                        'NUVLABOX_IMMUTABLE_SSH_PUB_KEY=',
                        'GPG_KEY=E3FF2839C048B25C084DEBE9B26995E310250568',
                        'HOST_HOME=/home'
                        'NUVLABOX_DATA_GATEWAY_IMAGE=eclipse-mosquitto:1.6.12',
                        'EXTERNAL_CVE_VULNERABILITY_DB=https://github.com/nuvla/vuln-db/blob/main/databases/all.aggregated.csv.gz?raw=true',
                        'LANG=C.UTF-8',
                        'SECURITY_SCAN_INTERVAL=1800',
                        'DB_SLICE_SIZE=20000',
                        'VPN_INTERFACE_NAME=vpn',
                        'IMAGE_NAME=job-lite',
                        'NUVLA_ENDPOINT=nuvla.io'
                    ],
                    'force-restart': False,
                    'current-version': '2.4.3',
                    'config-files': ['docker-compose.yml']
                    }


# @validator('EngineUpdate')
class EngineUpdateUp(ValidationBase):
    STATE_LIST: list[str] = ['NEW', 'ACTIVATED', 'COMMISSIONED', 'DECOMMISSIONED']

    def trigger_update(self):
        nuvlabox: CimiResource = self.nuvla_client.get(self.uuid)
        # pp(nuvlabox.operations)
        resp: CimiResponse = self.nuvla_client.operation(nuvlabox, 'update-nuvlabox', data=sample_dict)

        pp("Print data")
        pp(resp.data)

    def wait_for_commissioned(self):
        """

        :return:
        """
        self.logger.info(f'Waiting until device is commissioned')
        self.engine_handler.start_engine(self.uuid, remove_old_installation=True)
        last_state: str = self.get_nuvlaedge_status()[0]
        while last_state != self.STATE_LIST[2]:
            time.sleep(1)
            last_state: str = self.get_nuvlaedge_status()[0]

    def wait_for_operational(self):
        """

        :return:
        """
        self.logger.info(f'Waiting for status device: OPERATIONAL')
        last_status: str = self.get_nuvlaedge_status()[1]
        while last_status != "OPERATIONAL":
            time.sleep(1)
            last_status: str = self.get_nuvlaedge_status()[1]

    def test_update(self):
        self.wait_for_commissioned()

        last_status: str = self.get_nuvlaedge_status()[1]

        self.logger.info(f'Running update when status on {last_status}')
        response: CimiCollection = self.nuvla_client.search('nuvlabox',
                                                            filter=f'id=="{self.uuid}"')

        old_version = response.resources[0].data
        self.wait_for_operational()
        self.trigger_update()
        self.logger.info(f'Waiting some time')
        time.sleep(30)