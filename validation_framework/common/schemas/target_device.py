"""

"""

from pydantic import BaseModel, BaseSettings, Field

from common.release import Release


class SystemSetup(BaseModel):
    """
    System setup schema for validation configuration
    """
    docker_version: Release
    compose_version: Release
    swarm_enabled: bool


class TargetDeviceConfig(BaseModel):
    """
    Remote device target_device configuration for SSH target_device class
    """
    alias: str

    # Network data
    address: str
    port: int = 22
    hostname: str | None

    # Naming data
    user: str

    # Security data
    pub_key_path: str | None
    private_key_path: str | None

    password: str | None
