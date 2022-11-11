"""

"""

from pydantic import BaseModel

from framework.deployer.common import Version


class DeviceSetup(BaseModel):
    """

    """
    docker_version: Version
    compose_version: Version
    swarm_enabled: bool


class DeviceConfig(BaseModel):
    """

    """
    alias: str

    # Network data
    address: str
    port: int = 22
    hostname: str | None

    # Naming data
    user: str

    # Security data
    pub_key_path: str
    private_key_path: str
    password: str
