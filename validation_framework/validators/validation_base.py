"""
General purpose class for NuvlaEdge validation
"""
import logging
import time
import unittest

from nuvla.api import Api as NuvlaClient
from nuvla.api.models import CimiResponse, CimiCollection

from validation_framework.common import constants as cte, Release
from validation_framework.common.nuvla_uuid import NuvlaUUID
from validation_framework.deployer.engine_handler import EngineHandler


class ParametrizedTests(unittest.TestCase):

    def __init__(self, test_name: str, target_device_config: str, target_engine_version: str):

        super().__init__(test_name)

        self.test_name: str = test_name
        self.target_config_file: str = target_device_config
        self.target_engine_version: str = target_engine_version

    @staticmethod
    def parametrize(testcase_class, target_device_config: str, target_engine_version: str):
        """
        Create a suite containing all tests taken from the given
        subclass, passing them the parameters.
        :param testcase_class: Class to type to be parametrized
        :param target_device_config: Parameter to be added to the class
        :param target_engine_version: Version to be tested
        :return: A test suite
        """
        test_loader = unittest.TestLoader()
        test_names = test_loader.getTestCaseNames(testcase_class)

        suite = unittest.TestSuite()

        for name in test_names:
            suite.addTest(testcase_class(name, target_device_config, target_engine_version))
        return suite


class ValidationBase(ParametrizedTests):
    INDEX: int = 1
    DESCRIPTION: str = 'Tests a simple deployment  Start -> Activation -> Commission -> Decommission -> Stop'
    uuid: NuvlaUUID = ''
    STATE_HIST: list[str] = []
    STATE_LIST: list[str] = ['NEW', 'ACTIVATED', 'COMMISSIONED', 'DECOMMISSIONED']

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

        self.STATE_HIST.append(response.resources[0].data['state'])
        return response.resources[0].data['state'], status

    def create_nuvlaedge_in_nuvla(self) -> NuvlaUUID:
        """
        Given API keys from remote NuvlaInstallation creates a new NuvlaEdge
        :return:
        """
        if self.uuid:
            return self.uuid
        self.nuvla_client.login_apikey('credential/724bc2b6-4a2f-4f15-9239-bf375ba8174e',
                                       'pvWZNa.bXZ8AS.Les692.dYyU3F.4LtD9W')
        if self.engine_handler.release_handler.release_tag:
            it_release: int = self.engine_handler.release_handler.release_tag.major
        else:
            it_release: int = 2

        response: CimiResponse = self.nuvla_client.add(
            'nuvlabox',
            data={'refresh-interval': 30,
                  'name': cte.NUVLAEDGE_NAME.format(device=self.engine_handler.device_config.alias),
                  'tags': ['nuvlaedge.validation=True', 'cli.created=True'],
                  'version': it_release,
                  'vpn-server-id': 'infrastructure-service/eb8e09c2-8387-4f6d-86a4-ff5ddf3d07d7'})

        return NuvlaUUID(response.data.get('resource-id'))

    def remove_nuvlaedge_from_nuvla(self) -> None:
        """

        :return:
        """
        ne_state: str = self.get_nuvlaedge_status()[0]

        if ne_state in ['COMMISSIONED', 'ACTIVATED']:
            self.nuvla_client.get(self.uuid + "/decommission")

        while ne_state not in ['DECOMMISSIONED', 'NEW']:
            time.sleep(1)
            ne_state = self.get_nuvlaedge_status()[0]
        self.logger.info(f'Decommissioning...')
        self.nuvla_client.delete(self.uuid)

    def setUp(self) -> None:
        super(ValidationBase, self).setUp()
        self.logger: logging.Logger = logging.getLogger(__name__)

        self.nuvla_client: NuvlaClient = NuvlaClient()
        self.engine_handler: EngineHandler = EngineHandler(cte.DEVICE_CONFIG_PATH / self.target_config_file,
                                                           Release('2.4.3'))
        self.uuid: NuvlaUUID = self.create_nuvlaedge_in_nuvla()

        self.logger.info(f'Target device: {self.engine_handler.device_config.hostname}')

    def tearDown(self) -> None:
        super(ValidationBase, self).tearDown()
        self.logger.info(f'Parent tear down {__name__}')
        self.engine_handler.stop_engine()

        self.remove_nuvlaedge_from_nuvla()


