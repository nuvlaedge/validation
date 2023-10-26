"""
Tests the robustness the system to automatically reboot
"""
import time

import invoke
from fabric import Result

from validation_framework.validators import ValidationBase
from validation_framework.validators.tests.basic_tests import validator


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
            result: Result = self.engine_handler.restart_engine()

        except invoke.exceptions.UnexpectedExit as ex:
            self.logger.info(f'Successfully rebooted {ex}')

    def test_restart_after_commissioning(self):
        """
        Tests the correct behaviour of the NuvlaEdge when the device is restarted after commissioning
        :return:
        """
        self.assertTrue(self.get_nuvlaedge_status()[0] == self.STATE_LIST[0], 'Initial Status must by NEW')

        time.sleep(5)
        self.wait_for_commissioned()
        self.wait_for_operational()

        initial_up_time: float = self.get_system_up_time()
        self.logger.info(f"Initial up time {initial_up_time}")
        self.trigger_restart()

        self.logger.info('Waiting for device to come back up')
        coe_type = self.engine_handler.coe_type
        time_to_sleep = 100 if coe_type == 'docker' else 200
        time_to_wait_for_reboot = 180 if coe_type == 'docker' else 400

        # Give some time for the reboot to execute
        time.sleep(time_to_sleep)

        later_up_time: float = self.get_system_up_time()
        start_time: float = time.time()
        while later_up_time > initial_up_time:
            later_up_time = self.get_system_up_time()
            if time.time() - start_time > time_to_wait_for_reboot:
                self.logger.error("Device didn't reboot ")
                break
            time.sleep(1)

        self.assertTrue(later_up_time < time_to_wait_for_reboot)

