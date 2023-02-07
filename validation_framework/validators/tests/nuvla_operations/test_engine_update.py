"""

"""
import json
import time
from pprint import pprint as pp
from nuvla.api.models import CimiResource, CimiResponse, CimiCollection

from validation_framework.validators.tests.nuvla_operations import validator
from validation_framework.validators import ValidationBase


# @validator('EngineUpdate')
class EngineUpdateUp(ValidationBase):
    # Max 5 mins of time to update the engine
    UPDATE_MAX_TIME: int = 60.0*5

    def trigger_update(self) -> str:
        nuvlabox: CimiResource = self.nuvla_client.get(self.uuid)

        status: CimiResource = self.nuvla_client.get(nuvlabox.data.get('nuvlabox-status'))
        releases: CimiResource = self.nuvla_client.get('nuvlabox-release')

        available_releases: list = releases.data.get('resources')
        selected_release: str = ''
        selected_rel_version: str = ''
        current_release: str = nuvlabox.data.get('nuvlabox-engine-version')

        for rel in available_releases:
            if current_release < rel.get('release'):
                selected_release = rel.get('id')
                selected_rel_version = rel.get('release')
                self.logger.info(f'Selected release {rel.get("release")}')
                break

        install_params: dict = status.data.get('installation-parameters')
        release_data: dict = {
            'nuvlabox-release': selected_release,
            'payload': json.dumps(install_params)
        }

        resp: CimiResponse = self.nuvla_client.operation(nuvlabox,
                                                         'update-nuvlabox',
                                                         data=release_data)
        return selected_rel_version

    def test_update(self):
        self.wait_for_commissioned()
        self.wait_for_operational()

        last_status: str = self.get_nuvlaedge_status()[1]

        self.logger.info(f'Running update when status on {last_status}')

        target_release = self.trigger_update()
        current_release = self.nuvla_client.get(self.uuid).data.get('nuvlabox-engine-version')
        self.logger.info(f'Waiting for the update to finish')
        start_time: float = time.time()
        while target_release != current_release:
            time.sleep(0.5)
            current_release = self.nuvla_client.get(self.uuid).data.get('nuvlabox-engine-version')
            if time.time() - start_time > self.UPDATE_MAX_TIME:
                self.logger.warning(f'Update process timeout')

                break

        self.assertEqual(target_release, current_release, f'Update from {current_release} to {target_release}'
                                                          f' failed')
        self.logger.info(f'Current release')
