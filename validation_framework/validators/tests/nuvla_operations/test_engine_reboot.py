"""
Test engine reboot
"""

from validators.tests import validator


@validator('Engine Reboot')
class TestEngineReboot:

    def execute_reboot_operation(self):
        ...

    def test_engine_reboot(self):
        ...
