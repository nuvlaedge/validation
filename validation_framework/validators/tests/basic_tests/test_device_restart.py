"""
Tests the robustness the system to automatically reboot
"""
import time

import invoke

from validation_framework.validators import ValidationBase
from . import validator


@validator('DeviceRestart')
class TestDeviceRestart(ValidationBase):
    """

    """
    operational_time: float = 60*3  # Give 3 minutes for the device to restart and come back up
    STATE_LIST: list[str] = ['NEW', 'ACTIVATED', 'COMMISSIONED', 'DECOMMISSIONED']

    def trigger_restart(self):
        """
        Trigger a restart in the remote device
        :return:
        """
        try:
            self.engine_handler.device.run_sudo_command('sudo shutdown -r now')
        except invoke.exceptions.UnexpectedExit:
            self.logger.info(f'Successfully rebooted')

    def setUp(self) -> None:
        super(TestDeviceRestart, self).setUp()

    def test_restart_before_commission(self):
        """
        Tests the correct behaviour of the NuvlaEdge when the device is restarted right before commissioning
        :return:
        """
        self.assertTrue(self.get_nuvlaedge_status()[0] == self.STATE_LIST[0], 'Initial Status must by NEW')
        self.engine_handler.start_engine(self.uuid, remove_old_installation=True)

        self.logger.info('Waiting for the device to activate')
        last_state: str = self.get_nuvlaedge_status()[0]
        while last_state != self.STATE_LIST[1]:
            time.sleep(0.5)
            last_state = self.get_nuvlaedge_status()[0]

        self.trigger_restart()

        last_status: str = self.get_nuvlaedge_status()[1]
        start_time: float = time.time()

        while time.time() - start_time < self.operational_time:
            last_status = self.get_nuvlaedge_status()[1]
            if last_status == 'OPERATIONAL':
                self.assertTrue(True, 'System returned to operational status')

        self.assertTrue(last_status == 'OPERATIONAL', 'Status should be opearationsl')

    def test_restart_after_commissioning(self):
        """
        Tests the correct behaviour of the NuvlaEdge when the device is restarted after commissioning
        :return:
        """
        self.assertTrue(self.get_nuvlaedge_status()[0] == self.STATE_LIST[0], 'Initial Status must by NEW')
        self.engine_handler.start_engine(self.uuid, remove_old_installation=True)

        self.logger.info('Waiting for the device to activate')
        last_state: str = self.get_nuvlaedge_status()[0]
        while last_state != self.STATE_LIST[2]:
            time.sleep(0.5)
            last_state = self.get_nuvlaedge_status()[0]

        self.trigger_restart()

        start_time: float = time.time()

        while time.time() - start_time < self.operational_time:
            last_status = self.get_nuvlaedge_status()[1]
            self.logger.info(f'Current status {last_status}')
            if last_status == 'OPERATIONAL':
                self.assertTrue(True, 'System returned to operational status')
            time.sleep(1)
        last_status: str = self.get_nuvlaedge_status()[1]
        self.logger.info(f'Last registered status {last_status}')
        self.assertTrue(last_status == 'OPERATIONAL', 'Status should be opearationsl')

