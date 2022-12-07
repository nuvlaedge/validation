"""
Hardcodes the configuration of the system root logger
"""
import logging
from logging.config import dictConfig

logging_config = {'version': 1,
                  'formatters':
                      {'f': {'format': '[%(asctime)s - %(levelname)s - %(name)s/%(funcName)s]: %(message)s'}},
                  'handlers':
                      {'h': {'class': 'logging.StreamHandler',
                             'formatter': 'f',
                             'level': logging.DEBUG}},
                  'root': {'handlers': ['h'],
                           'level': logging.DEBUG}
                  }


def config_logger(logger: logging.Logger | None = None):
    """
    Configures the root logger if no logger provided
    :param logger:
    :return:
    """
    if not logger:
        # Means we are configuring root logger
        dictConfig(logging_config)
