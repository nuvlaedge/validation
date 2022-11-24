"""
General purpose class for NuvlaEdge validation
"""
import logging
import time
import unittest
from pathlib import Path

from nuvla.api import Api as NuvlaClient
from nuvla.api.models import CimiResponse

from common import constants as cte, Release
from common.nuvla_uuid import NuvlaUUID
from deployer.engine_handler import EngineHandler


class ParametrizedTests(unittest.TestCase):

    def __init__(self, test_name: str, target_device_config: str, target_engine_version: str):

        super().__init__(test_name)

        self.test_name: str = test_name
        self.target_config_file: Path = Path(target_device_config)
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

    def create_nuvlaedge_in_nuvla(self) -> NuvlaUUID:
        """
        Given API keys from remote NuvlaInstallation creates a new NuvlaEdge
        :return:
        """
        if self.uuid:
            return self.uuid
        if self.engine_handler.release_handler.release_tag:
            it_release: int = self.engine_handler.release_handler.release_tag.major
        else:
            it_release: int = 2

        response: CimiResponse = self.nuvla_client.add(
            'nuvlabox',
            data={'refresh-interval': 30,
                  'name': cte.NUVLAEDGE_NAME.format(device=self.engine_handler.device_config.alias),
                  'tags': ['nuvlaedge.validation=True', 'cli.created=True'],
                  'version': it_release})
        return NuvlaUUID(response.data.get('resource-id'))

    def remove_nuvlaedge_from_nuvla(self) -> None:
        """

        :return:
        """
        ...

    def setUp(self) -> None:
        super(ValidationBase, self).setUp()
        self.logger: logging.Logger = logging.getLogger(__name__)

        self.logger.info(f'THIS IS MAGIC {self.target_config_file}')
        self.nuvla_client: NuvlaClient = NuvlaClient()
        self.engine_handler: EngineHandler = EngineHandler(1, Release('2.4.3'))
        self.uuid: NuvlaUUID = self.create_nuvlaedge_in_nuvla()

        self.logger.info(f'Target device: {self.engine_handler.device_config.hostname}')

    def tearDown(self) -> None:
        # self.device.stop_engine()
        ...
