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
    TIMEOUT: int = 300  # Maximum of 5  minutes for the peripherals to show up

    def setUp(self) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.logger.info(f'Starting custom setUp in Peripheral network tests')
        self.nuvla_client: NuvlaClient = NuvlaClient()

        self.engine_handler: EngineHandler = EngineHandler(
            cte.DEVICE_CONFIG_PATH / self.target_config_file,
            self.target_engine_version,
            repo=self.target_repository,
            branch=self.target_branch,
            include_peripherals=True,
            peripherals=['network'])

        self.uuid: NuvlaUUID = self.create_nuvlaedge_in_nuvla()

        self.logger.info(
            f'Target device: {self.engine_handler.device_config.hostname}')

    def test_network_peripheral(self):
        self.logger.info(f'Starting network peripheral test')
        self.wait_for_commissioned()
        self.wait_for_operational()

        cont_filter: dict = {"Names": "{{ .Names }}"}
        data: list[dict] = self.engine_handler.device.get_remote_containers(
            containers_filter=cont_filter)

        # Find network container in list
        self.logger.debug(f'Checking remote containers looking for network')
        found: bool = False
        for c in data:
            if 'network' in c.get('Names'):
                found = True
                break
        self.assertTrue(found, 'Network container not found in remote devices')

        # Gather data from Nuvla and check peripherals are being reported
        self.logger.debug(
            f'Checking Nuvla peripheral registration with a {self.TIMEOUT}s timeout')
        search_filter = f'created-by="{self.uuid}"'

        count: int = self.nuvla_client.search('nuvlabox-peripheral',
                                              filter=search_filter).data.get(
            'count', 0)
        start_time: float = time.time()

        while count == 0 or time.time() - start_time > self.TIMEOUT:
            count = self.nuvla_client.search('nuvlabox-peripheral',
                                             filter=search_filter).data.get(
                'count', 0)

        self.assertTrue(count > 0,
                        'After 5 minutes the peripheral manager should have '
                        'found some network device')
