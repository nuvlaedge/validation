import time

from nuvla.api.models import CimiCollection

from validators.validation_base import ValidationBase

from validators.tests import validator


@validator('1_standard_engine_start')
class TestStandardEngineRun(ValidationBase):
    TEST_RUN_TIME: float = 60*2
    STATUS_LIST: list[str] = ['NEW', 'ACTIVE', 'COMMISSIONED']

    def get_nuvlaedge_status(self) -> tuple[str, str]:
        """
        This function retrieves the Edge state and status. Status will be setup once the NuvlaEdge engine has started.
        State is defined by Nuvla Logic and status is defined by the NuvlaEdge system depending on the NuvlaEdge
         initialization progress.
        :return: Tuple [state, status].
        """
        response: CimiCollection = self.nuvla_client.search('nuvlabox',
                                                            filter=f'id=="{self.uuid}"')

        try:
            status_response: CimiCollection = self.nuvla_client.search(
                'nuvlabox-status',
                filter=f'id=="{response.resources[0].data["nuvlabox-status"]}"')
            status = status_response.resources[0].data['status']
        except:
            status = 'UNKNOWN'
        return response.resources[0].data['state'], status

    def setUp(self) -> None:
        super(TestStandardEngineRun, self).setUp()

        self.engine_handler.start_engine(self.uuid, remove_old_installation=True)

    def tearDown(self) -> None:
        super(TestStandardEngineRun, self).tearDown()

        self.engine_handler.stop_engine()

        # self.remove_nuvlaedge_from_nuvla()
        uuid: str = self.uuid

        ne_state: str = self.get_nuvlaedge_status()[0]

        if ne_state in ['COMMISSIONED']:
            self.nuvla_client.get(uuid + "/decommission")

        while ne_state not in ['DECOMMISSIONED', 'NEW']:
            time.sleep(1)
            ne_state = self.get_nuvlaedge_status()[0]

        self.nuvla_client.delete(uuid)

    def test_std_deployment(self):
        # Test standard deployments for 15 minutes
        self.assertEqual(self.get_nuvlaedge_status()[0], 'NEW', 'Initial state should be new')
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



