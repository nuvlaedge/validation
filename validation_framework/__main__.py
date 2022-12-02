"""
Validator entrypoint python script
"""

import argparse
import io
import json
import unittest
from datetime import datetime
from enum import Enum, auto
import logging
import time
from pathlib import Path
from logging import config as logger_config

import xmlrunner
from xmlrunner.extra.xunit_plugin import transform
import xmltodict
import xml.etree.ElementTree as ET

import validation_framework.common.constants as cte
from validation_framework.common.settings import ValidatorSettings
from validation_framework.validators.tests.basic_tests import active_validators, get_validator
from validation_framework.validators.validation_base import ParametrizedTests

# Entrypoint logging object
logger: logging.Logger = logging.getLogger()

# Load validators settings
validator_settings: ValidatorSettings = ValidatorSettings()


class AvailableTests(Enum):
    STANDARD_DEPLOYMENT = auto()


def parse_results(results: list[io.BytesIO]) -> list[tuple[bytes, dict]]:
    """
    Converts a bytes stream xml formatted into a dict
    :param results: bytes stream
    :return: UnitTests results in dict format
    """
    # Convert bytes into xml string
    parsed_data: list[tuple] = []
    for res in results:
        logger.info(f'Resultados {res}')
        xml_result: bytes = transform(res.getvalue())
        # Return dict form the XML
        parsed_data.append((xml_result, xmltodict.parse(xml_result)))

    return parsed_data


def run_test_on_device(device_config_file: str) -> list[io.BytesIO]:

    test_results: list[io.BytesIO] = []

    for name, v in active_validators.items():
        logger.info(f'Validator: {get_validator(name)}')

        test_report: io.BytesIO = io.BytesIO()
        runner = xmlrunner.XMLTestRunner(output=test_report, verbosity=1)

        suite = unittest.TestSuite()
        suite.addTest(ParametrizedTests.parametrize(get_validator(name),
                                                    target_device_config=device_config_file,
                                                    target_engine_version='2.4.3'))
        result = runner.run(suite)
        test_results.append(test_report)

    return test_results


def save_results(results: list, location: Path) -> None:
    cte.JSON_RESULTS_PATH.mkdir(exist_ok=True, parents=True)
    cte.XML_RESULTS_PATH.mkdir(exist_ok=True, parents=True)
    for res in results:
        xml_results = res[0]
        json_results = res[1]

        logger.info(f'{json.dumps(res[1], indent=4)} ')
        json_location = cte.JSON_RESULTS_PATH / (
                json_results.get('testsuites').get('testsuite').get('@name').split('.')[-1] + '.json')
        with json_location.open('w') as file:
            json.dump(json_results, file, indent=4)

        xml_location = cte.XML_RESULTS_PATH / (
                    json_results.get('testsuites').get('testsuite').get('@name').split('.')[-1] + '.xml')
        with xml_location.open('wb') as file:
            tree = ET.ElementTree(ET.fromstring(xml_results))
            tree.write(file, encoding='utf-8')


def parse_arguments() -> argparse.Namespace:
    arguments: argparse.ArgumentParser = argparse.ArgumentParser()
    arguments.add_argument("--target")
    arguments.add_argument("--microservice", default=None)
    return arguments.parse_args()


def main(arguments: argparse.Namespace):
    """
    Main script for test running. Its main functionality is selecting the test parsed as parameter
    :return:
    """
    logger.info(f'Starting Validator framework at {datetime.now()}')
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    validation_time: float = time.process_time()
    elapsed_time: float = time.time()

    # Run validation
    logger.info(f'Validators size {len(active_validators)} : {active_validators.items()}')
    time.sleep(2)
    logger.info(f'Starting validation process in {arguments.target}')
    test_report: list = run_test_on_device(arguments.target)
    results = parse_results(test_report)

    save_results(results, cte.RESULTS_PATH)
    validation_time = time.process_time() - validation_time
    elapsed_time = time.time() - elapsed_time
    logger.info(f'Successfully finishing validation in {validation_time}s with a total of '
                f'{elapsed_time}s elapsed')


if __name__ == '__main__':

    # Configure the logger by file. Should be adaptable via command line
    logger_config.fileConfig(cte.LOGGING_CONFIG_FILE)
    args: argparse.Namespace = parse_arguments()
    logger.info(f'Parsed arguments: {args}')
    main(args)

