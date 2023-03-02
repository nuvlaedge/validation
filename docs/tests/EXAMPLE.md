# Writing and integrating new test and test set

## 1. Writing the tests.
We are going to create a validation test for the network peripheral.

1. Create a new folder:
   ```shell
   mkdir validation_framework/validatiors/tests/peripherals
   ```

2. Create the python file for the test
   ```shell
   touch validation_framework/validatiors/tests/peripherals/test_peripheral_network.py
   ```

3. Create class instance and extend ValidationBase class
   ```python
   
   from validation_framework.validators.tests.nuvla_operations import validator 
   from validation_framework.validators import ValidationBase
   
   @validator('PeripheralNetwork')
   class TestPeripheralNetwork(ValidationBase):
     ...   
   ```
   
4. In this case, we need to override the predefined `setUp()` method since the default behaviour only targets the
main components in `docker-compose.yml`. Here, we add the peripherals to test to the EngineHandler configuration. `network` in this case.
   ```python
   import logging
   
   from nuvla.api import Api as NuvlaClient
   
   from validation_framework.common.nuvla_uuid import NuvlaUUID
   from validation_framework.deployer.engine_handler import EngineHandler
   from validation_framework.common import constants as cte, Release
   from validation_framework.validators.tests.nuvla_operations import validator 
   from validation_framework.validators import ValidationBase
   
   @validator('PeripheralNetwork')
   class TestPeripheralNetwork(ValidationBase):
     def setUp(self) -> None:
         self.logger: logging.Logger = logging.getLogger(__name__)
         self.logger.info(f'Starting custom setUp in Peripheral network tests')
         self.nuvla_client: NuvlaClient = NuvlaClient()
   
         self.engine_handler: EngineHandler = EngineHandler(cte.DEVICE_CONFIG_PATH / self.target_config_file,
                                                     Release('2.4.6'),
                                                     repo=self.target_repository,
                                                     branch=self.target_branch,
                                                     include_peripherals=True,
                                                     peripherals=['network'])
   
         self.uuid: NuvlaUUID = self.create_nuvlaedge_in_nuvla()
   
         self.logger.info(f'Target device: {self.engine_handler.device_config.hostname}')
   ```

5. Create the validation tests for the peripheral

   ```python
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
   
       def setUp(self) -> None:
           self.logger: logging.Logger = logging.getLogger(__name__)
           self.logger.info(f'Starting custom setUp in Peripheral network tests')
           self.nuvla_client: NuvlaClient = NuvlaClient()
   
           self.engine_handler: EngineHandler = EngineHandler(cte.DEVICE_CONFIG_PATH / self.target_config_file,
                                                              Release('2.4.6'),
                                                              repo=self.target_repository,
                                                              branch=self.target_branch,
                                                              include_peripherals=True,
                                                              peripherals=['network'])
   
           self.uuid: NuvlaUUID = self.create_nuvlaedge_in_nuvla()
   
           self.logger.info(f'Target device: {self.engine_handler.device_config.hostname}')
   
       def test_network_peripheral(self):
           self.logger.info(f'Starting network peripheral test')
           self.wait_for_commissioned()
           self.wait_for_operational()
   
           cont_filter: dict = {"Names": "{{ .Names }}"}
           data: list[dict] = self.engine_handler.device.get_remote_containers(containers_filter=cont_filter)
   
           # Find network container in list
           self.logger.debug(f'Checking remote containers looking for network')
           found: bool = False
           for c in data:
               if 'network' in c.get('Names'):
                   found = True
                   break
               time.sleep(1)
           self.assertTrue(found, 'Network container not found in remote devices')
   
           # Gather data from Nuvla and check peripherals are being reported
           self.logger.debug(f'Checking Nuvla peripheral registration with a {self.TIMEOUT}s timeout')
           search_filter = f'created-by="{self.uuid}"'
   
           count: int = self.nuvla_client.search('nuvlabox-peripheral', filter=search_filter).data.get('count', 0)
           start_time: float = time.time()
   
           while count == 0 or time.time() - start_time > self.TIMEOUT:
               count = self.nuvla_client.search('nuvlabox-peripheral', filter=search_filter).data.get('count', 0)
   
           self.assertTrue(count > 0, "After 5 minutes the peripheral manager should have found some network device")
   ```

6. Last, as we have created a new set of tests (`peripherals/`) we need to update the root `__main__.py` file as well as
the GitHub environmental variables

   ### `__main__.py`
   ```python
   if validator_type == 'basic_tests':
     logger.info(f'Running basic tests')
     from validation_framework.validators.tests.basic_tests import active_validators, get_validator
   elif validator_type == 'peripherals':
     logger.info(f'Running Peripherals validation tests')
     from validation_framework.validators.tests.peripherals import active_validators, get_validator
   elif validator_type == 'nuvla_operations':
     logger.info(f'Running Nuvla Operations')
     from validation_framework.validators.tests.nuvla_operations import active_validators, get_validator
   else:
     raise Exception('No validator selected, cannot tests...')
   ```
   
   ### GitHub environmental variable `$VALIDATION_TESTS`
   1. Go to `https://github.com/organizations/nuvlaedge/settings/variables/actions`
   2. Edit VALIDATION_TESTS variable:
   
      `"[\"basic_tests\",\"nuvla_operations\",\"peripherals\"]"`
