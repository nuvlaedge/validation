"""
Validator entrypoint python script
"""
import io
import unittest
from datetime import datetime
from enum import Enum, auto
import logging
import time
from logging import config as logger_config
from pprint import pprint as pp


import xmlrunner
from xmlrunner.extra.xunit_plugin import transform
import xmltodict

import common.constants as cte
from common.settings import ValidatorSettings
from validators.tests import active_validators
from validators.validation_base import ParametrizedTests, ValidationBase
from validators.tests.test_standard_engine_run import TestStandardEngineRun
# Entrypoint logging object
logger: logging.Logger = logging.getLogger()

# Load validators settings
validator_settings: ValidatorSettings = ValidatorSettings()


class AvailableTests(Enum):
    STANDARD_DEPLOYMENT = auto()


def parse_results(results: io.BytesIO) -> tuple[bytes, dict]:
    """
    Converts a bytes stream xml formatted into a dict
    :param results: bytes stream
    :return: UnitTests results in dict format
    """
    # Convert bytes into xml string
    xml_result: bytes = transform(results.getvalue())
    # Return dict form the XML
    return xml_result, xmltodict.parse(xml_result)


def main():
    """
    Main script for test running. Its main functionality is selecting the test parsed as parameter
    :return:
    """
    logger.info(f'Starting Validator framework at {datetime.now()}')
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    validation_time: float = time.process_time()
    elapsed_time: float = time.time()

    # Run validation
    name = ''
    tester = None
    for name, v in active_validators.items():
        name = name
        tester = v
        logger.info(f'Detected')
    # deployer: Deployer = Deployer('devel', 'engine', 'target_device')
    test_report: io.BytesIO = io.BytesIO()
    runner = xmlrunner.XMLTestRunner(output=test_report, verbosity=1)

    suite = unittest.TestSuite()
    suite.addTest(ParametrizedTests.parametrize(TestStandardEngineRun,
                                                target_device_config='1_rpi4.toml',
                                                target_engine_version='2.4.3'))
    result = runner.run(suite)

    time.sleep(2)
    xml_result, dict_result = parse_results(test_report)
    pp(dict_result)
    pp(type(xml_result.decode()))
    validation_time = time.process_time() - validation_time
    elapsed_time = time.time() - elapsed_time
    logger.info(f'Successfully finishing validation in {validation_time}s with a total of '
                f'{elapsed_time}s elapsed')


if __name__ == '__main__':

    # Configure the logger by file. Should be adaptable via command line
    logger_config.fileConfig(cte.LOGGING_CONFIG_FILE)

    main()

