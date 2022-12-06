"""
Gathers all the available validators, imports them and exposes them to be instantiated
by Telemetry class
"""
import glob
import logging

from os.path import dirname, basename, isfile
from typing import Dict

modules = glob.glob(dirname(__file__) + "/*.py")
file_logger = logging.getLogger('validators')
file_logger.setLevel(logging.INFO)

file_logger.info(f'Modules: {modules}')


class Validators:
    """
    Wrapper class for available validators

        validators: Currently registered and imported validators
    """
    active_validators: Dict = {}

    @classmethod
    def get_validator(cls, validator_name: str):
        """
        Returns a validators class provided a name
        Args:
            validator_name: validators to retreive

        Returns:

        """
        return cls.active_validators.get(validator_name)

    @classmethod
    def register_validator(cls, validator_name: str, p_validator):
        """
        Registers a new validators module provided a name and the module
        Args:
            validator_name: Monitor name to be registered
            p_validator: Monitor module to be registered
        """

        file_logger.info(f'Validator {validator_name} registered')
        cls.active_validators[validator_name] = p_validator

    @classmethod
    def validator(cls, validator_name: str = None):
        """
        Tries to register the validators name provided by name
        Args:
            validator_name: validators to be created and registered

        Returns: Monitor class

        """
        def decorator(validator_class):
            _validator_name: str = validator_name
            if not validator_name:
                _validator_name = validator_class.__name__

            if _validator_name in cls.active_validators:
                file_logger.error(f'Validator {_validator_name} is already defined')
            else:
                cls.register_validator(_validator_name, validator_class)

            return validator_class

        return decorator


validator = Validators.validator
get_validator = Validators.get_validator
register_validator = Validators.register_validator
active_validators = Validators.active_validators

for m in modules:
    if isfile(m) and not m.endswith('__init__.py'):
        __all__ = [basename(m)[:-3]]
        try:
            from . import *
        except ModuleNotFoundError as ex:
            file_logger.exception(f'Module {__all__[0]} not fount')
