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


@validator('EngineReboot')
class TestEngineReboot(ValidationBase):
    STATE_LIST: list[str] = ['NEW', 'ACTIVATED', 'COMMISSIONED', 'DECOMMISSIONED']
    WAIT_TIME: float = 60.0

    def execute_reboot_operation(self):
        nuvlabox: CimiResource = self.nuvla_client.get(self.uuid)
        resp: CimiResponse = self.nuvla_client.operation(nuvlabox, 'reboot')
        pp(resp.data)
        job: CimiResource = self.nuvla_client.get(resp.data.get('location'))
        self.logger.info(f'Waiting for restart to be executed')
        start_time: float = time.time()

        while True:
            time.sleep(0.5)
            if job.data.get('state') == 'SUCCESS':
                self.logger.info('Successfully executed reboot')
                break
            if time.time() > (start_time + self.WAIT_TIME):
                raise TimeoutError(f'Reboot Job {resp.data.get("location")} did not complete in time ')

            job = self.nuvla_client.get(resp.data.get('location'))

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
        self.wait_for_operational()

        last_status: str = self.get_nuvlaedge_status()[1]

        self.logger.info(f'Running reboot when status on {last_status}')
        self.execute_reboot_operation()
        # Operations are defined
        time.sleep(2)

        self.logger.info(f'Waiting for reboot')
        try:
            while self.engine_handler.device.is_reachable(silent=True):
                time.sleep(0.5)
        except paramiko.ssh_exception.SSHException:
            self.logger.info(f'Device rebooted')

        self.logger.info(f'Waiting for device to come back up')
        while not self.engine_handler.device.is_reachable(silent=True):
            time.sleep(0.5)

        response: Result = self.engine_handler.device.run_command("awk '{print $1}' /proc/uptime")
        pp(f'Uptime {response.stdout}')
        if response.stdout:
            up_time = float(response.stdout)
            self.logger.info(f'Up time... {up_time}')
            self.assertTrue(int(up_time) < 60)
