"""
General purpose class for NuvlaEdge validation
"""

import logging
import time
import unittest
from logging import exception

import requests
from nuvla.api import Api as NuvlaClient
from nuvla.api.models import CimiResponse, CimiCollection

from validation_framework.common import constants as cte
from validation_framework.common.nuvla_uuid import NuvlaUUID
from validation_framework.deployer.engine_handler import EngineHandler

# Dynamically add methods to UpdateNuvlaEdge
def create_update_method(release, target_branch):
    def method(self):
        self.run_update(release, target_branch)
    return method

class ParametrizedTests(unittest.TestCase):

    def __init__(self,
                 test_name: str,
                 target_device_config: str,
                 nuvla_api_key: str,
                 nuvla_api_secret: str,
                 nuvlaedge_version: str = '',
                 deployment_branch: str = '',
                 nuvlaedge_branch: str = '',
                 retrieve_logs: bool = False):

        super().__init__(test_name)

        self.test_name: str = test_name
        self.target_config_file: str = target_device_config
        self.nuvla_api_key: str = nuvla_api_key
        self.nuvla_api_secret: str = nuvla_api_secret
        self.nuvlaedge_version: str = nuvlaedge_version
        self.target_nuvlaedge_branch: str = nuvlaedge_branch
        self.target_deployment_branch: str = deployment_branch
        self.retrieve_logs: bool = retrieve_logs

    @staticmethod
    def parametrize(testcase_class,
                    target_device_config: str,
                    nuvla_api_key: str,
                    nuvla_api_secret: str,
                    nuvlaedge_version: str = '',
                    deployment_branch: str = '',
                    nuvlaedge_branch: str = '',
                    retrieve_logs: bool = False):
        """
         Create a suite containing all tests taken from the given
        subclass, passing them the parameters.

        Args:
            testcase_class: Class to type to be parametrized
            target_device_config: Parameter to be added to the class
            nuvla_api_key:
            nuvla_api_secret:
            nuvlaedge_version: NuvlaEdge version
            deployment_branch:
            nuvlaedge_branch:
            retrieve_logs:

        Returns:
            A test suite
        """
        test_loader = unittest.TestLoader()

        suite = unittest.TestSuite()

        if testcase_class.__name__ == "UpdateNuvlaEdge":
            releases = testcase_class.get_sorted_releases()
            for release in releases:
                method_name = f"test_update_{release[0].replace(".", "_")}_to_{nuvlaedge_branch}"
                method = create_update_method(release[0], nuvlaedge_branch)
                setattr(testcase_class, method_name, method)
                setattr(testcase_class, 'release_id', release[1])

        test_cases = test_loader.getTestCaseNames(testcase_class)

        for name in test_cases:
            suite.addTest(testcase_class(name,
                                         target_device_config,
                                         nuvla_api_key,
                                         nuvla_api_secret,
                                         nuvlaedge_version,
                                         deployment_branch,
                                         nuvlaedge_branch,
                                         retrieve_logs))
        return suite




class ValidationBase(ParametrizedTests):
    uuid: NuvlaUUID = ''
    STATE_HIST: list[str] = []
    STATE_LIST: list[str] = ['NEW', 'ACTIVATED', 'COMMISSIONED', 'DECOMMISSIONED']

    def wait_for_commissioned(self, engine: EngineHandler = None, uuid: NuvlaUUID = None):
        """

        :return:
        """
        if not engine:
            engine = self.engine_handler

        if not uuid:
            uuid = self.uuid

        engine.start_engine(uuid, remove_old_installation=True)
        try:
            last_state: str = self.get_nuvlaedge_status(uuid=uuid)[0]
        except IndexError:
            last_state: str = 'UNKNOWN'

        self.logger.info('Waiting until device is commissioned')
        while last_state != self.STATE_LIST[2]:
            time.sleep(1)
            last_state: str = self.get_nuvlaedge_status(uuid=uuid)[0]

    def wait_for_operational(self):
        """

        :return:
        """
        self.logger.info('Waiting for status device: OPERATIONAL')
        last_status: str = self.get_nuvlaedge_status()[1]
        while last_status != "OPERATIONAL":
            time.sleep(1)
            last_status: str = self.get_nuvlaedge_status()[1]
        self.wait_for_capabilities(['NUVLA_JOB_PULL'])

    def get_system_up_time(self) -> float:
        return self.engine_handler.get_system_up_time_in_engine()

    def wait_for_capabilities(self, capabilities: list):
        """
        :param capabilities: Capabilities to match against the NuvlaBox resource
        """
        self.logger.info(f'Waiting for capabilities {capabilities} in NuvlaEdge {self.uuid}')
        nuvlabox: CimiResponse = self.nuvla_client.get(self.uuid)
        t_time = time.time()

        if not capabilities:
            return

        while time.time() < t_time + cte.DEFAULT_JOBS_TIMEOUT:
            time.sleep(5)
            res_capabilities = nuvlabox.data.get('capabilities')
            if not res_capabilities:
                self.logger.debug(f'No capabilities in NuvlaBox {self.uuid}')
                continue
            cap_flag = True
            for i in capabilities:
                if i not in res_capabilities:
                    self.logger.debug(f'Capability {i} not in NuvlaBox {self.uuid}')
                    cap_flag = False

            if cap_flag:
                self.logger.info(f'NuvlaEdge {self.uuid} ready with capabilities: {capabilities}')
                return
        self.logger.info(f'NuvlaEdge {self.uuid} does not have {capabilities} capabilities')
        self.assertTrue(False, f'NuvlaEdge {self.uuid} does not have {capabilities} capabilities')


    def get_field_from_resource(self, res_id: str, field: str) -> str | dict:
        """
        Retrieve a field from a resource

        :param res_id:  ID
        :param field: Field to retrieve
        :return: Field value
        """
        try:
            return self.nuvla_client.get(res_id).data[field]
        except Exception:
            self.logger.debug(f'Could not retrieve {field} from {res_id}')
            return 'UNKNOWN'

    def wait_update_ready(self, uuid: NuvlaUUID = None) -> tuple[str, dict | None]:
        t_time = time.time()
        status = 'UNKNOWN'
        while time.time() < t_time + cte.DEFAULT_JOBS_TIMEOUT:
            time.sleep(1)
            status = self.get_field_from_resource(uuid, 'nuvlabox-status')
            if status and status != 'UNKNOWN':
                break

        if not status or status == 'UNKNOWN':
            self.logger.error(f'Could not retrieve status from {uuid}')
            return 'UNKNOWN', None

        while time.time() < t_time + cte.DEFAULT_JOBS_TIMEOUT:
            time.sleep(1)
            version = self.get_field_from_resource(status, 'nuvlabox-engine-version')
            params = self.get_field_from_resource(status, 'installation-parameters')
            ready = (version and params) and (version != 'UNKNOWN' and params != 'UNKNOWN')
            if not ready:
                self.logger.debug(f'Version or params  not yet available in NuvlaBox status {status}')
                continue
            return version, params

        return 'UNKNOWN', None

    def get_nuvlaedge_status(self, uuid: NuvlaUUID = None) -> tuple[str, str]:
        """
        This function retrieves the Edge state and status. Status will be setup once the
        NuvlaEdge engine has started. State is defined by Nuvla Logic and status is
        defined by the NuvlaEdge system depending on the NuvlaEdge initialization
        progress.
        :return: Tuple [state, status].
        """
        if not uuid:
            uuid = self.uuid
        response: CimiCollection = self.nuvla_client.search('nuvlabox',
                                                            filter=f'id=="{uuid}"')

        try:
            status_response: CimiCollection = self.nuvla_client.search(
                'nuvlabox-status',
                filter=f'id=="{response.resources[0].data["nuvlabox-status"]}"')
            status = status_response.resources[0].data['status']
        except:
            status = 'UNKNOWN'

        self.STATE_HIST.append(response.resources[0].data['state'])
        return response.resources[0].data['state'], status

    def create_nuvlaedge_in_nuvla(self, name: str = '', suffix: str = '') -> NuvlaUUID:
        """
        Given API keys from remote NuvlaInstallation creates a new NuvlaEdge
        :return:
        """
        if self.uuid:
            return self.uuid
        self.nuvla_client.login_apikey(self.nuvla_api_key, self.nuvla_api_secret)

        it_release: int = 2

        if not name:
            name = cte.NUVLAEDGE_NAME.format(device=self.target_config_file.replace(".toml", ""))

        if suffix:
            name = f'{name}-{suffix}'

        response: CimiResponse = self.nuvla_client.add(
            'nuvlabox',
            data={'refresh-interval': 60,
                  'heartbeat-interval': 20,
                  'name': name,
                  'tags': ['nuvlaedge.validation=True', 'cli.created=True'],
                  'version': it_release,
                  'vpn-server-id':
                      'infrastructure-service/eb8e09c2-8387-4f6d-86a4-ff5ddf3d07d7'})

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
        self.logger.info('Decommissioning...')
        self.nuvla_client.delete(self.uuid)

    def setUp(self) -> None:
        super(ValidationBase, self).setUp()
        self.logger: logging.Logger = logging.getLogger(__name__)

        self.nuvla_client: NuvlaClient = NuvlaClient(reauthenticate=True)

        self.logger.info(f'Creating engine handler on deployment version: '
                         f'{self.nuvlaedge_version}')
        self.engine_handler: EngineHandler = EngineHandler(
            cte.DEVICE_CONFIG_PATH / self.target_config_file,
            nuvlaedge_version=self.nuvlaedge_version,
            nuvlaedge_branch=self.target_nuvlaedge_branch,
            deployment_branch=self.target_deployment_branch)

        self.uuid: NuvlaUUID = self.create_nuvlaedge_in_nuvla()

        self.logger.info(f'Target device: {self.engine_handler.device_config.hostname}')

    def tearDown(self) -> None:
        super(ValidationBase, self).tearDown()
        self.logger.info('ValidationBase tear down, stopping and cleaning engine')

        # Retrieve NuvlaEdge logs if UnitTest fail. If retrieve logs is selected as an
        # input, ignore whether tests fail and always download logs
        if not self.retrieve_logs:
            if hasattr(self._outcome, 'errors'):
                # Python 3.4 - 3.10  (These two methods have no side effects)
                result = self.defaultTestResult()
                self._feedErrorsToResult(result, self._outcome.errors)
            else:
                # Python 3.11+
                result = self._outcome.result
            ok = all(test != self for test, text in result.errors + result.failures)

            # Demo output:  (print short info immediately - not important)
            if not ok:
                self.retrieve_logs = True
                self.logger.error(f'Test failed with exception: {self.failureException}')

        self.engine_handler.stop_engine(retrieve_logs=self.retrieve_logs)
        self.remove_nuvlaedge_from_nuvla()
