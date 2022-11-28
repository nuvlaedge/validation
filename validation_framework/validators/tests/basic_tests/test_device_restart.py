"""
Tests the robustness the system to automatically reboot
"""
import time

import invoke

from validators import ValidationBase
from . import validator


@validator('DeviceRestart')
class TestDeviceRestart(ValidationBase):
    """

    """
    operational_time: float = 60

    def trigger_restart(self):
        """
        Trigger a restart in the remote device
        :return:
        """
        try:
            self.engine_handler.device.run_sudo_command('sudo reboot')
        except invoke.exceptions.UnexpectedExit:
            self.logger.info(f'Successfully rebooted')

    def setUp(self) -> None:
        super(TestDeviceRestart, self).setUp()

        # self.engine_handler.start_engine(self.uuid, remove_old_installation=True)

    def test_restart_before_activation(self):
        """
        Tests the correct behaviour of the NuvlaEdge when the device is restarted right before the activation
        :return: None
        """
        assert True

    def test_restart_before_commission(self):
        """
        Tests the correct behaviour of the NuvlaEdge when the device is restarted right before commissioning
        :return:
        """
        assert True

    def test_restart_after_commissioning(self):
        """
        Tests the correct behaviour of the NuvlaEdge when the device is restarted after commissioning
        :return:
        """
        assert False

