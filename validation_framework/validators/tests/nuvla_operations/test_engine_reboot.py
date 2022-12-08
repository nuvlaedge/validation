"""
Test engine reboot
"""
from validation_framework.validators import ValidationBase
from validation_framework.validators.tests.nuvla_operations import validator
from nuvla.api.models import CimiResource, CimiResponse
import time
from fabric import Result
from pprint import pprint as pp


@validator('EngineReboot')
class TestEngineReboot(ValidationBase):
    STATE_LIST: list[str] = ['NEW', 'ACTIVATED', 'COMMISSIONED', 'DECOMMISSIONED']

    def execute_reboot_operation(self):
        nuvlabox: CimiResource = self.nuvla_client.get(self.uuid)
        pp(nuvlabox.operations)
        resp: CimiResponse = self.nuvla_client.operation(nuvlabox, 'reboot')

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

    def test_engine_reboot(self):
        # Test standard deployments for 15 minutes

        self.wait_for_commissioned()

        last_status: str = self.get_nuvlaedge_status()[1]

        self.logger.info(f'Running reboot when status on {last_status}')
        self.execute_reboot_operation()
        time.sleep(2)
        self.wait_for_operational()

        response: Result = self.engine_handler.device.run_command('uptime -p')
        if response.stdout:
            up_time = response.stdout.split(" ")[1]
            self.logger.info(f'Up time... {up_time}')
            self.assertTrue(int(up_time) < 10)

    def tearDown(self) -> None:
        super(TestEngineReboot, self).tearDown()

