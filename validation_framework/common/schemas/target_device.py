"""

"""

from pydantic import BaseModel, ConfigDict, Field

from validation_framework.common.release import Release


class SystemSetup(BaseModel):
    """
    System setup schema for validation configuration
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    docker_version: Release
    compose_version: Release
    swarm_enabled: bool


class TargetDeviceConfig(BaseModel):
    """
    Remote device target_device configuration for SSH target_device class
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    alias: str
    coe: str

    # Network data
    address: str
    port: int = 22
    hostname: str | None = None

    # Naming data
    user: str

    # Security data
    pub_key_path: str | None = None
    private_key_path: str | None = None

    password: str | None = None

    excluded_tests: list[str] = Field(default_factory=list)
