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

        self.engine_handler.start_engine(self.uuid, remove_old_installation=True)

    def test_device_restarts(self):
        # 1. Restart after activation
        # 2. Restart after commissioning
        expected_states: list[str] = ['ACTIVATED', 'COMMISSIONED', 'NEW', 'OFFLINE']
        expected_status: list[str] = ['DEGRADED', 'UNKNOWN', 'RUNNING']

        state, status = self.get_nuvlaedge_status()
        # self.assertTrue(status in expected_status)
        # self.assertTrue(state in expected_states)

        while status in ['COMMISSIONED']:
            self.logger.info(f'NuvlaEdge not commission yet '
                             f'\n\tStatus: {status} {status in ["COMMISSIONED"]}'
                             f'\n\tState: {state}')
            status, state = self.get_nuvlaedge_status()
            time.sleep(1)

        self.trigger_restart()

        # Wait the telemetry period
        time.sleep(35)

        while state in ['OPERATIONAL']:
            time.sleep(1)
            state, status = self.get_nuvlaedge_status()

        self.assertTrue(state in ['OPERATIONAL'])

        self.logger.info(self.get_nuvlaedge_status())


        assert True


