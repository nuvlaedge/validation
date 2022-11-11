"""

"""
import logging

import toml
import unittest

from pydantic import ValidationError

from framework.deployer.common.constants import *
from framework.deployer.device.ssh_device import SSHDevice
from framework.deployer.engine.engine import EngineHandler
from framework.deployer.schemas.device import DeviceConfig
from framework.deployer.schemas.engine.engine import EngineSchema


class BaseValidationTest(unittest.TestCase):
    """

    """
    SAMPLE_VALIDATION_FILE: Path = TESTS_CONFIG_PATH / '1-Basic functional validation.toml'

    logger: logging.Logger = logging.getLogger(__name__)

    def load_device_configuration(self) -> DeviceConfig:
        """
        Loads the possible device configuration stored in the default path
        :return:
        """
        devices: dict = {}
        for file in DEVICE_CONFIG_PATH.iterdir():
            with file.open() as conf:
                devices = toml.load(conf)

        if devices:
            devices.pop('title')

            for alias, conf in devices.items():
                conf['alias'] = alias
                try:
                    return DeviceConfig.parse_obj(conf)
                except ValidationError:
                    self.logger.warning(f'Device {alias} configuration cannot be parsed')
                    raise

    def load_validation_configuration(self) -> EngineSchema:
        """

        :return:
        """
        self.logger.info(f'Importing configuration for test {self.SAMPLE_VALIDATION_FILE.name}')
        with self.SAMPLE_VALIDATION_FILE.open() as file:
            open_file = toml.load(file)
            return EngineSchema.parse_obj(open_file)

    def setUp(self) -> None:
        """
        Sets up the basic configuration for deployments
        This method may be overwritten by subclasses requiring different configuration approaches
        :return: None
        """
        # Check targeted device
        self.logger.info(f'Starting tests for  {1}')

        # Parse configurations
        self.device_configuration: DeviceConfig = self.load_device_configuration()
        self.engine_configuration: EngineSchema = self.load_validation_configuration()

        # Instantiate main objects
        self.device: SSHDevice = SSHDevice(self.device_configuration)
        self.engine_handler: EngineHandler = EngineHandler(self.device, self.engine_configuration)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] Line:%(lineno)d %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    logging.info('Some info')
    unittest.main()
