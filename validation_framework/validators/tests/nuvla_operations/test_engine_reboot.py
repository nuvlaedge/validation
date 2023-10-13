"""
Test engine reboot
"""
import paramiko

from validation_framework.validators import ValidationBase
from validation_framework.validators.tests.nuvla_operations import validator
from nuvla.api.models import CimiResource, CimiResponse
import time
from fabric import Result
from pprint import pprint as pp


#@validator('EngineReboot')
class TestEngineReboot(ValidationBase):
    WAIT_TIME: float = 400

    def execute_reboot_operation(self):
        nuvlabox: CimiResource = self.nuvla_client.get(self.uuid)
        resp: CimiResponse = self.nuvla_client.operation(nuvlabox, 'reboot')

        job: CimiResource = self.nuvla_client.get(resp.data.get('location'))
        self.logger.info(f'Waiting for job restart {resp.data.get("location")} '
                         f'to be executed')
        start_time: float = time.time()

        while True:
            time.sleep(0.5)
            if job.data.get('state') == 'SUCCESS':
                self.logger.info('Successfully executed reboot')
                break
            if time.time() - start_time > self.WAIT_TIME:
                raise TimeoutError(f'Reboot Job {resp.data.get("location")} '
                                   f'did not complete in time ')

            job = self.nuvla_client.get(resp.data.get('location'))

    def test_engine_reboot(self):
        # Test standard deployments for 15 minutes
        self.logger.info("Starting Engine Reboot validation tests")
        self.wait_for_commissioned()
        self.wait_for_operational()

        last_status: str = self.get_nuvlaedge_status()[1]

        self.logger.info(f'Running reboot when status on {last_status}')
        initial_up_time: float = self.get_system_up_time()
        self.execute_reboot_operation()

        self.logger.info(f'Waiting for device to come back up')
        # Give some time for the reboot to execute
        time.sleep(30)

        later_up_time: float = self.get_system_up_time()
        start_time: float = time.time()
        while later_up_time > initial_up_time:
            later_up_time = self.get_system_up_time()
            if time.time() - start_time > 180:
                self.logger.error("Device didn't reboot 3 min")
                break
            time.sleep(1)

        self.assertTrue(later_up_time < 180)
