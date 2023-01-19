"""

"""
import json
from pathlib import Path
from pprint import pp

from pydantic import BaseModel


class ResultSchema(BaseModel):
    """

    """
    name: str
    test_type: str
    release: str
    target_device: str
    result: bool


def process_name_from_class(class_name: str) -> str:
    """

    :param class_name:
    :return:
    """
    name = class_name.split('.')
    return name[-1]


def process_type_from_class(class_name: str) -> str:
    it_type = class_name.split('.')
    return it_type[2]
