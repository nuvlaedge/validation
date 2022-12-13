"""
Validation test for NuvlaEdge
id: StandardEngineRun
name: Standard engine run test

description: The goal of this test is to run a simple deployment on the given NuvlaEdge version. It compares
status and state simultaneously against a predefined ordered list of strings.

State must follow the next order:
 1. New
 2. Activated
 3. Commissioned
 4. Decommissioned

Status order:
 1. Unknown
 2. ---
 3. Operational

For this test, the NuvlaEdge engine is started after asserting the initial state of the machine.
"""

import time

from validation_framework.validators import ValidationBase
from validation_framework.validators.tests.basic_tests import validator

# TODO: Some change
@validator('StandardEngineRun')
class TestStandardEngineRun(ValidationBase):
    TEST_RUN_TIME: float = 60*5
    STATE_LIST: list[str] = ['NEW', 'ACTIVATED', 'COMMISSIONED', 'DECOMMISSIONED']
    SINGLE_SETUP_FLAG: bool = True

    def setUp(self) -> None:
        super(TestStandardEngineRun, self).setUp()

    def test_std_deployment(self):
        # Test standard deployments for 15 minutes
        last_state: str = self.get_nuvlaedge_status()[0]
        self.logger.debug(f'Current State {last_state}')
        self.assertTrue(self.STATE_LIST[0] == last_state, 'Initial state should be "New"')

        # Starts the preconfigured engine after checking the remote state of the nuvlaedge
        self.engine_handler.start_engine(self.uuid, remove_old_installation=True)

        # Wait until the device is activated
        last_state = self.get_nuvlaedge_status()[0]
        self.logger.debug(f'Current State {last_state}')
        while last_state != self.STATE_LIST[1]:
            self.logger.info(f'Waiting state {last_state} to be {self.STATE_LIST[1]}')
            time.sleep(2)
            last_state = self.get_nuvlaedge_status()[0]

        self.assertTrue(self.STATE_LIST[1] == last_state, 'Next Stated must be "Activated"')

        start_time: float = time.time()
        self.logger.info(f'Starting longer run of  {self.TEST_RUN_TIME}s')
        try:
            while self.TEST_RUN_TIME > (time.time() - start_time):
                last_update = self.get_nuvlaedge_status()

                self.assertTrue(last_update[0] in [self.STATE_LIST[1], self.STATE_LIST[2]],
                                'Run State must be Commissioned')

                time.sleep(5)

        except Exception as ex:
            # Capture all the exception so the teardown is always executed and cleans Nuvla and the device
            self.logger.exception(f'Something went wrong passing the test {__name__}', ex)
