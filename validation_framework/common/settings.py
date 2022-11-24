"""
Validator framework settings data schema definitions
"""

from pathlib import Path

from pydantic import BaseSettings, Field


class ValidatorSettings(BaseSettings):
    """
    General purpose settings for the validation framework
    """
    debug: bool = Field(False, env='DEBUG')

    engine_config: Path = Field(Path('engine_config®.toml'), env='ENGINE_CONFIG')
    device_config: Path = Field(Path('device_config.toml'), env='DEVICE_CONFIG')
