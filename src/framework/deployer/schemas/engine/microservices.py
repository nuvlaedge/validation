"""

"""

from pydantic import BaseModel

from framework.deployer.common import Version
from framework.deployer.schemas.engine.settings import AgentEnvs, SystemManagerEnvs, VPNClientEnvs, ComputeAPIEnvs


class AgentSchema(BaseModel):
    """

    """
    version: Version
    settings: AgentEnvs


class SystemManagerSchema(BaseModel):
    version: Version
    settings: SystemManagerEnvs


class ComputeAPISchema(BaseModel):
    version: Version
    settings: ComputeAPIEnvs


class VPNClientSchema(BaseModel):
    version: Version
    settings: VPNClientEnvs


class JobEngineSchema(BaseModel):
    version: Version


class OnStopSchema(BaseModel):
    version: Version

