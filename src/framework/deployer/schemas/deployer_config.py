"""
Base config schemas the deployer
"""

from pydantic import BaseModel


class DeployerSettings(BaseModel):
    ...


class TestSettings(BaseModel):
    ...
