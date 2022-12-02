"""
Common set of functions for the validators
"""
import logging
from pathlib import Path

import toml


utils_logger: logging.Logger = logging.getLogger(__name__)


def get_model_from_toml(model_class: type, file_location: Path):
    """

    :param model_class:
    :param file_location:
    :return:
    """
    return get_model_from_dict(model_class, get_dict_from_toml(file_location))


def get_model_from_dict(model_class: type, content: dict):
    """

    :param model_class:
    :param content:
    :return:
    """
    return model_class.parse_obj(content)


def get_dict_from_toml(file_location: Path) -> dict:
    """
    Tries to open a toml file given its locations and converts returning a dict with its content
    :param file_location:
    :return:
    """
    if not file_location.exists():
        raise FileExistsError(f'File {file_location} does not exists in {file_location.parent}')

    try:
        with file_location.open() as toml_file:
            return toml.load(toml_file)
    except toml.TomlDecodeError:
        utils_logger.error(f'File {file_location} not formatted as toml')
        raise
