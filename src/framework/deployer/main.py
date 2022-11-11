"""

"""
import logging
import time

import pydantic
import toml

from framework.deployer.common.constants import *
from framework.deployer.engine.engine import EngineHandler
from framework.deployer.schemas.device import DeviceConfig
from framework.deployer.device.ssh_device import SSHDevice
from framework.deployer.schemas.engine.engine import EngineSchema


SAMPLE_VALIDATION_FILE: Path = TESTS_CONFIG_PATH/'1-Basic functional validation.toml'


def load_device_configuration() -> DeviceConfig:
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
            except pydantic.ValidationError:
                logging.warning(f'Device {alias} configuration cannot be parsed')
                raise


def load_validation_configuration() -> EngineSchema:
    """

    :return:
    """
    logging.info(f'Importing configuration for test {SAMPLE_VALIDATION_FILE.name}')

    with SAMPLE_VALIDATION_FILE.open() as file:
        open_file = toml.load(file)
        return EngineSchema.parse_obj(open_file)


def main():

    logging.info('Starting deployer...')

    # 1. Read input configuration (Validation and device)
    engine_configuration: EngineSchema = load_validation_configuration()
    device_configuration: DeviceConfig = load_device_configuration()

    # 2. Initialise device and check connectivity
    device: SSHDevice = SSHDevice(device_configuration)
    engine_handler: EngineHandler = EngineHandler(device, engine_configuration)

    while not device.is_reachable():
        time.sleep(0.1)

    # 3. Check download and desired release version
    engine_handler.download_requested_releases()

    # 4. Configure the device under the validation requirements
    logging.info(f'Basic testing iteration requires no parameters')

    # 5. Configure the engine under the validation requirements

    # 6. Start engine
    engine_handler.start_nuvlaedge()
    # 7. Gather data until validation stops
    # 8. Stop engine
    # 9. gather execution data


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] Line:%(lineno)d %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    main()
