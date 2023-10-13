import logging
import time

from nuvla.api import Api as NuvlaClient

from validation_framework.common.nuvla_uuid import NuvlaUUID
from validation_framework.validators.tests.peripherals import validator
from validation_framework.validators import ValidationBase
from validation_framework.deployer.engine_handler import EngineHandler
from validation_framework.common import constants as cte, Release


@validator('PeripheralNetwork')
class TestPeripheralNetwork(ValidationBase):
    TIMEOUT: int = 60  # Maximum of 5  minutes for the peripherals to show up

    def setUp(self) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.logger.info(f'Starting custom setUp in Peripheral network tests')
        self.nuvla_client: NuvlaClient = NuvlaClient()

        self.engine_handler: EngineHandler = EngineHandler(
            cte.DEVICE_CONFIG_PATH / self.target_config_file,
            nuvlaedge_version=self.nuvlaedge_version,
            nuvlaedge_branch=self.target_nuvlaedge_branch,
            deployment_branch=self.target_deployment_branch,
            include_peripherals=True,
            peripherals=['Network'])

        self.uuid: NuvlaUUID = self.create_nuvlaedge_in_nuvla()

        self.logger.info(
            f'Target device: {self.engine_handler.device_config.hostname}')

    def test_network_peripheral(self):
        self.logger.info(f'Starting network peripheral test')
        self.wait_for_commissioned()
        self.wait_for_operational()

        time.sleep(10)
        peripherals: set = {'network'}

        self.assertTrue(self.engine_handler.check_if_peripherals_running(peripherals),
                        'Network peripheral is not running')
        # Gather data from Nuvla and check peripherals are being reported
        self.logger.debug(
            f'Checking Nuvla peripheral registration with a {self.TIMEOUT}s timeout')
        search_filter = f'created-by="{self.uuid}"'

        count: int = self.nuvla_client.search('nuvlabox-peripheral',
                                              filter=search_filter).data.get(
            'count', 0)
        start_time: float = time.time()

        while count == 0 and time.time() - start_time < self.TIMEOUT:
            count = self.nuvla_client.search('nuvlabox-peripheral',
                                             filter=search_filter).data.get('count', 0)

        self.assertTrue(count > 0,
                        'After 5 minutes the peripheral manager should have '
                        'found some network device')
