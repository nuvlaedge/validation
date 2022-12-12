import argparse
import json
import logging
import os
from pathlib import Path

from validation_framework.common.logging_config import config_logger
from pytablewriter import MarkdownTableWriter
from pprint import pprint as pp


logger: logging.Logger = logging.getLogger()

results_path: Path = Path('../../results/temp/json/').resolve()

if not results_path.exists():
    exit(1)


def parse_arguments() -> argparse.Namespace:
    arguments: argparse.ArgumentParser = argparse.ArgumentParser()
    arguments.add_argument("--origin")
    arguments.add_argument("--test-files")
    return arguments.parse_args()


def find_files(files: str) -> list[Path]:
    """
    Receives a list of files to process and resturns the list of Path object types if exists
    :param files: File names as a concatenated string comma separated
    :return: A list of check absolute paths of the files
    """
    file_list: list[str] = files.split(',')
    path_list: list[Path] = []
    for file in file_list:
        it_path: Path = results_path / file
        if it_path.exists():
            path_list.append(it_path)
    pp(path_list)
    return path_list


def get_test_name(class_name: str) -> str:
    """
    extracts the test name from the whole
    :param class_name:
    :return:
    """


def parse_file(file_path: Path) -> dict:
    """

    :param file_path:
    :return:
    """
    with file_path.open('r') as file:
        it_d = json.load(file).get('testsuites').get('testsuite')
        # it_d['target_device'] = json.load(file).get('target_device')

        pp(it_d)
        return it_d


def main(arguments: argparse.Namespace):
    """

    :param arguments:
    :return:
    """
    logger.info(f'Updating results from validation of: {arguments.origin}')
    paths = find_files(arguments.test_files)
    for p in paths:
        parse_file(p)

    writer = MarkdownTableWriter(
        table_name="Basic Tests",
        headers=["rpi4", "ubuntu_vm"],
        value_matrix=[
            [0,   0.1,      "hoge", True,   0,      "2017-01-01 03:04:05+0900"],
            [2,   "-2.23",  "foo",  False,  None,   "2017-12-23 45:01:23+0900"],
            [3,   0,        "bar",  "true",  "inf", "2017-03-03 33:44:55+0900"],
            [-10, -9.9,     "",     "FALSE", "nan", "2017-01-01 00:00:00+0900"],
        ],
        margin=1
    )
    with open('sampel.md', 'w') as f:
        writer.stream = f
        writer.write_table()


if __name__ == '__main__':
    args: argparse.Namespace = parse_arguments()
    config_logger()

    main(args)
