import time

from validators import ValidationBase
from . import validator


@validator('1_standard_engine_start')
class TestStandardEngineRun(ValidationBase):
    TEST_RUN_TIME: float = 60*5
    STATUS_LIST: list[str] = ['NEW', 'ACTIVE', 'COMMISSIONED']

    def setUp(self) -> None:
        super(TestStandardEngineRun, self).setUp()

        self.engine_handler.start_engine(self.uuid, remove_old_installation=True)

    def test_std_deployment(self):
        # Test standard deployments for 15 minutes
        self.assertTrue(self.get_nuvlaedge_status()[0] in ['NEW', 'ACTIVATED'], 'Initial state should be new')
        # Starts the preconfigured engine
        last_state: str = self.get_nuvlaedge_status()[0]
        state_history: list[str] = [last_state]
        status_history: list[str] = []

        start_time: float = time.time()
        valid_states: list = ['COMMISSIONED', 'COMMISSIONING', 'ACTIVATED', 'NEW']
        try:
            while self.TEST_RUN_TIME > (time.time() - start_time):
                last_update = self.get_nuvlaedge_status()

                state_history.append(last_update[0])
                self.assertTrue(last_update[0] in valid_states,
                                'States should move from NEW to ACTIVATED to COMMISSIONED')

                time.sleep(5)

        except Exception:
            ...



