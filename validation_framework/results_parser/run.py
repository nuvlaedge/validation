"""
This script is triggered only  when a release is tested. A NuvlaEdge version is considered a release once it's
available on Nuvla

:argument origin: Device in which the test has been performed
:argument tests: Type of tests executed in the device
"""
import argparse
import json
import logging
from pathlib import Path
from pprint import pprint as pp

from results_parser.displayed_data import DisplayedData
from validation_framework.common.logging_config import config_logger

logger: logging.Logger = logging.getLogger()


DATA_PATH: Path = Path('/Users/nacho/PycharmProjects/nuvlaedge/devel/validation/results/') / 'printed/data/'
TESTS_PATH: Path = Path('/Users/nacho/PycharmProjects/nuvlaedge/devel/validation/results/temp/json/')

# [NuvlaBox Engine update to 2.4.6] ERROR: Update failed! Unable to
# retrieve files docker-compose.usb.yml,docker-compose.security.yml,docker-compose.gpu.yml,
# docker-compose.yml,docker-compose.modbus.yml,docker-compose.bluetooth.yml,docker-compose.network.yml:
# Critical error in /opt/nuvlabox/commands/nuvlabox-engine-download-configs:
# ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
# WARNING: NuvlaBox Engine update failed. Rollback to previous version
# NuvlaBox Engine was rolled back successfully after a failed update
def parse_arguments() -> argparse.Namespace:
    """
    Defines and parses the expected arguments for the result plotter
    :return: Parsed arguments namespace
    """
    arguments: argparse.ArgumentParser = argparse.ArgumentParser()
    arguments.add_argument("--origin")
    arguments.add_argument("--tests")
    arguments.add_argument("--release")
    return arguments.parse_args()


def main(arguments: argparse.Namespace):
    """

    :param arguments:
    :return:
    """
    logger.info(f'Running parser for device {arguments.origin} on tests {arguments.tests}')

    displayed_data: DisplayedData = DisplayedData()
    for test_file in TESTS_PATH.iterdir():
        pp(test_file.name)
        with test_file.open('r') as file:
            test_data = json.load(file)
            displayed_data.process_new_test(arguments.release, test_data)
    displayed_data.build_test_type_table('basic_tests', '2.4.3')


if __name__ == '__main__':
    args: argparse.Namespace = parse_arguments()
    config_logger()

    main(args)
