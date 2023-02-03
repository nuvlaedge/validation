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
from validation_framework.common.logging_config import config_logger
from validation_framework.validators.validation_base import ParametrizedTests
# Dynamically import validators


# Entrypoint logging object
logger: logging.Logger = logging.getLogger()


def parse_results(results: list[io.BytesIO]) -> list[tuple[bytes, dict]]:
    """
    Converts a bytes stream xml formatted into a dict
    :param results: bytes stream
    :return: UnitTests results in dict format
    """
    # Convert bytes into xml string
    parsed_data: list[tuple] = []
    for res in results:
        logger.info(f'Results {res}')
        xml_result: bytes = transform(res.getvalue())
        # Return dict form the XML
        parsed_data.append((xml_result, xmltodict.parse(xml_result)))

    return parsed_data


def run_test_on_device(arguments: argparse.Namespace) -> list[io.BytesIO]:

    # Results holder
    test_results: list[io.BytesIO] = []

    # Target version
    device_config_file: str = arguments.target
    repo: str = arguments.repository
    branch: str = arguments.branch
    logger.error(f'Running on repository {repo}/{branch}')
    if repo == 'deployment':
        if branch == 'main':
            logger.info(f'Running base release tests on {repo}:{branch}')

    for name, v in active_validators.items():
        logger.info(f'Validator: {get_validator(name)}')

        test_report: io.BytesIO = io.BytesIO()
        runner = xmlrunner.XMLTestRunner(output=test_report, verbosity=1)

        suite = unittest.TestSuite()
        suite.addTest(ParametrizedTests.parametrize(get_validator(name),
                                                    target_device_config=device_config_file,
                                                    target_engine_version=arguments.release,
                                                    repository=repo,
                                                    branch=branch))
        result = runner.run(suite)
        test_results.append(test_report)

    return test_results


def save_results(results: list, target_device: str, test_type: str) -> None:
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

    for res in results:
        xml_results = res[0]
        json_results = res[1]

        logger.info(f'{json.dumps(res[1], indent=4)} ')
        json_location = cte.JSON_RESULTS_PATH / (
                json_results.get('testsuites').get('testsuite').get('@name').split('.')[-1] + '.json')
        json_results['target_device'] = target_device
        json_results['test_type'] = test_type

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
    arguments.add_argument("--validator")
    arguments.add_argument("--release", default=None)
    arguments.add_argument("--repository", default=None)
    arguments.add_argument("--branch", default=None)

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
    test_report: list = run_test_on_device(arguments)
    results = parse_results(test_report)

    save_results(results, arguments.target, arguments.validator)

    validation_time = time.process_time() - validation_time
    elapsed_time = time.time() - elapsed_time
    logger.info(f'Successfully finishing validation in {validation_time}s with a total of '
                f'{elapsed_time}s elapsed')


if __name__ == '__main__':

    # Configure the logger by dict. Should be adaptable via command line
    config_logger()

    args: argparse.Namespace = parse_arguments()
    logger.info(f'Parsed arguments: {args}')

    validator_type = args.validator

    if validator_type == 'basic_tests':
        logger.info(f'Running basic tests')
        from validation_framework.validators.tests.basic_tests import active_validators, get_validator
    elif validator_type == 'features':
        logger.info(f'Running features')
        from validation_framework.validators.tests.features import active_validators, get_validator
    elif validator_type == 'microservices':
        logger.info(f'Running MS')
        from validation_framework.validators.tests.microservices import active_validators, get_validator
    elif validator_type == 'nuvla_operations':
        logger.info(f'Running Nuvla Operations')
        from validation_framework.validators.tests.nuvla_operations import active_validators, get_validator
        print(active_validators)
    else:
        raise Exception('No validator selected, cannot tests...')
    main(args)

