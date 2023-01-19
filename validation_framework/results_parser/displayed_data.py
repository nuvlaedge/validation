"""

"""
import json
import logging
import time
from pathlib import Path

from pprint import pp
from pytablewriter import MarkdownTableWriter


class DisplayedData:
    """

    """
    DATA_PATH: Path = Path('/Users/nacho/PycharmProjects/nuvlaedge/devel/validation/results/') / 'printed/data/'
    DISPLAY_PATH: Path = Path('/Users/nacho/PycharmProjects/nuvlaedge/devel/validation/docs/results/releases')

    def __init__(self):
        """

        """
        self.logger: logging.Logger = logging.getLogger(__name__)

        self.data: dict = {}
        self.retrieve_printed_data()
        self.DISPLAY_PATH.mkdir(exist_ok=True)

    def retrieve_printed_data(self):
        """

        :return:
        """
        for release_file in self.DATA_PATH.iterdir():
            release_name = (release_file.name).replace(release_file.suffix, '')

            pp(release_name)
            with release_file.open('r') as file:
                it_release = (json.load(file))
                self.data[release_name] = it_release

    @staticmethod
    def extract_test_type(class_name: str) -> str:
        """

        :param class_name:
        :return:
        """

        return class_name.split('.')[2]

    @staticmethod
    def extract_test_name(class_name: str) -> str:
        """

        :param class_name:
        :return:
        """
        return class_name.split('.')[-1]

    def build_test_type_table(self, test_type: str, release: str):
        """

        :return:
        """
        # Find unique tests
        unique_tests: list = []
        test_tab: dict = {}
        pp(self.data.get(release))
        for dev, data in self.data.get(release).get(test_type).items():
            for d in data:
                pp(d)
                if d[0] not in unique_tests:
                    unique_tests.append(d[0])
                    test_tab[d[0]] = []

        pp(unique_tests)

        # table: MarkdownTableWriter = MarkdownTableWriter(
        #     table_name=test_type.capitalize(),
        #     headers=df.columns,
        #     value_matrix=results_table,
        #     margin=1
        # )
        #
        # with open('sampel.md', 'a') as f:
        #     table.stream = f
        #     table.write_table()

    def process_new_test(self, release_name: str, test_data: dict) -> None:
        """
        Receives a specific release version and a testcase report. It expects the jUnit json test structure with
        an additional argument indicating the device in which it has been executed
        :param release_name:
        :param test_data:
        :return:
        """

        test_type: str = test_data.get('test_type')
        test_name: str = test_data.get('test_name')
        target_device: str = test_data.get('target_device')
        test_data: dict = test_data.get('testsuites').get('testsuite')

        if not self.data.get(release_name):
            # First time this release is added to the report
            self.data[release_name] = {}

        if not self.data[release_name].get(test_type):
            self.data[release_name][test_type] = {}

        if not self.data[release_name].get(test_type, {}).get(target_device):
            self.data[release_name][test_type][target_device] = []

        it_dev = self.data[release_name][test_type][target_device]
        if len(it_dev) == 0:
            it_dev.append(
                [test_name,
                 "1" == test_data.get("@failures"),
                 test_data.get("@timestamp")])

        else:
            for dev in it_dev:
                if test_name == dev[0]:
                    self.logger.info('Already registered')
                    return
            it_dev.append(
                [test_name,
                 "1" == test_data.get("@failures"),
                 test_data.get("@timestamp")])
