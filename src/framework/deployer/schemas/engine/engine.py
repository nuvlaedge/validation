"""

"""

from pydantic import BaseModel

from framework.deployer.common import Version
from framework.deployer.schemas.engine.microservices import (AgentSchema,
                                                             SystemManagerSchema,
                                                             VPNClientSchema,
                                                             JobEngineSchema,
                                                             OnStopSchema,
                                                             ComputeAPISchema)


class EngineComponents(BaseModel):
    agent: AgentSchema
    system_manager: SystemManagerSchema
    compute_api: ComputeAPISchema
    vpn_client: VPNClientSchema
    job_engine: JobEngineSchema
    on_stop: OnStopSchema


class EngineSchema(BaseModel):
    version: Version
    title: str
    description: str
    project_name: str

    components: EngineComponents
    peripherals: dict = {}
