"""
Validator entrypoint python script
"""

import argparse
import io
import json
import unittest
from datetime import datetime
import logging
import time
from pathlib import Path

import xmlrunner
from xmlrunner.extra.xunit_plugin import transform
import xmltodict
import xml.etree.ElementTree as ET

from validation_framework.common import utils
from validation_framework.common.schemas.target_device import TargetDeviceConfig
import validation_framework.common.constants as cte
from validation_framework.common.logging_config import config_logger
from validation_framework.validators.validation_base import ParametrizedTests

# Dynamically import validators


# Entrypoint logging object
logger: logging.Logger = logging.getLogger()

exit_code: int = 0
active_validators: dict = {}


def parse_results(results: list[io.BytesIO]) -> list[tuple[bytes, dict]]:
    """
    Converts a bytes stream xml formatted into a dict
    :param results: bytes stream
    :return: UnitTests results in dict format
    """
    # Convert bytes into xml string
    parsed_data: list[tuple[bytes, dict]] = []
    for res in results:
        logger.info(f'Results {res}')
        xml_result: bytes = transform(res.getvalue())
        # Return dict form the XML
        parsed_data.append((xml_result, xmltodict.parse(xml_result)))

    return parsed_data


def run_test_on_device(arguments: argparse.Namespace, validator: callable) -> list[io.BytesIO]:
    # Results holder
    test_results: list[io.BytesIO] = []

    # Target version
    device_config_file: str = arguments.target
    device_config: TargetDeviceConfig = utils.get_model_from_toml(TargetDeviceConfig, cte.DEVICE_CONFIG_PATH / device_config_file)

    for name, v in active_validators.items():
        if name in device_config.excluded_tests:
            logger.info(f"Skipping test {name} for device: {device_config.alias}")
            continue

        test_report: io.BytesIO = io.BytesIO()
        runner = xmlrunner.XMLTestRunner(output=test_report, verbosity=1)

        suite = unittest.TestSuite()
        suite.addTest(ParametrizedTests.parametrize(validator(name),
                                                    target_device_config=device_config_file,
                                                    nuvla_api_key=arguments.key,
                                                    nuvla_api_secret=arguments.secret,
                                                    nuvlaedge_version=arguments.nuvlaedge_version,
                                                    nuvlaedge_branch=arguments.nuvlaedge_branch,
                                                    deployment_branch=arguments.deployment_branch,
                                                    retrieve_logs=arguments.retrieve_logs))
        result = runner.run(suite)
        test_results.append(test_report)
    return test_results


def save_results(results: list, target_device: str, test_type: str) -> list:
    """

    :param test_type:
    :param results:
    :param target_device:
    :return:
    """

    dev_json_results_path: Path = cte.JSON_RESULTS_PATH / target_device
    dev_json_results_path.mkdir(exist_ok=True, parents=True)

    def_xml_results_path: Path = cte.XML_RESULTS_PATH / target_device
    def_xml_results_path.mkdir(exist_ok=True, parents=True)
    sum_json_results: list = []
    for res in results:
        xml_results = res[0]
        json_results = res[1]

        logger.info(f'{json.dumps(res[1], indent=4)} ')
        json_location = cte.JSON_RESULTS_PATH / (
                json_results.get('testsuites').get('testsuite').get(
                    '@name').split('.')[-1] + '.json')
        json_results['target_device'] = target_device
        json_results['test_type'] = test_type
        sum_json_results.append(json_results)

        with json_location.open('w') as file:
            json.dump(json_results, file, indent=4)

        xml_location = cte.XML_RESULTS_PATH / (
                json_results.get('testsuites').get('testsuite').get(
                    '@name').split('.')[-1] + '.xml')
        with xml_location.open('wb') as file:
            tree = ET.ElementTree(ET.fromstring(xml_results))
            tree.write(file, encoding='utf-8')

    return sum_json_results


def parse_arguments() -> argparse.Namespace:
    arguments: argparse.ArgumentParser = argparse.ArgumentParser()
    # Validator target device and target tests
    arguments.add_argument("--target")
    arguments.add_argument("--validator")

    # Until deployment and nuvlaedge are aligned we need both inputs
    arguments.add_argument("--nuvlaedge_version", default=None, nargs='?', const='')

    # Branch for devel
    arguments.add_argument("--nuvlaedge_branch", default=None, nargs='?', const='')
    arguments.add_argument("--deployment_branch", default=None, nargs='?', const='')

    # Credentials
    arguments.add_argument("--key")
    arguments.add_argument("--secret")

    # Logging
    arguments.add_argument("--log_level", default='INFO',
                           choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    # TODO: Future implementation
    arguments.add_argument("--retrieve_logs", default=False)

    return arguments.parse_args()


def main(arguments: argparse.Namespace, validator: callable):
    """
    Main script for test running. Its main functionality is selecting the test parsed as parameter
    :return:
    """
    global exit_code
    logger.info(f'Starting Validator framework at {datetime.now()}')
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    validation_time: float = time.process_time()
    elapsed_time: float = time.time()

    # Run validation
    time.sleep(2)
    logger.info(f'Starting validation process in {arguments.target}')
    test_report: list = run_test_on_device(arguments, validator)
    results = parse_results(test_report)

    json_results: list = save_results(results, arguments.target,
                                      arguments.validator)

    validation_time = time.process_time() - validation_time
    elapsed_time = time.time() - elapsed_time
    logger.info(
        f'Successfully finishing validation in {validation_time}s with a total of '
        f'{elapsed_time}s elapsed')

    # Assess exit code by reading the json results. If any failed, return 1.
    for r in json_results:
        for k, v in r.get("testsuites", {}).items():
            if v.get("@failures") != "0" or v.get("@errors") != "0":
                exit_code = 1
                break


def get_validator_type(validator_name: str) -> tuple[callable, dict]:
    """
    Factory method to select and import validation test set
    """
    match validator_name:
        case 'basic_tests':
            logger.info('Running basic tests')
            from validation_framework.validators.tests.basic_tests import \
                active_validators, get_validator
        case 'peripherals':
            logger.info('Running Peripherals validation tests')
            from validation_framework.validators.tests.peripherals import \
                active_validators, get_validator
        case 'nuvla_operations':
            logger.info('Running Nuvla Operations')
            from validation_framework.validators.tests.nuvla_operations import \
                active_validators, get_validator
        case _:
            raise ValueError('No validator selected, cannot tests...')
    return get_validator, active_validators


def entrypoint():
    global active_validators

    args: argparse.Namespace = parse_arguments()

    # Configure the logger by dict. Should be adaptable via command line
    config_logger(level=logging.getLevelName(args.log_level))

    logger.info(f'Parsed arguments: {args}')

    validator_type = args.validator

    get_validator, active_validators = get_validator_type(validator_type)
    main(args, get_validator)
    exit(exit_code)


if __name__ == '__main__':
    entrypoint()
