"""

"""

from pydantic import BaseModel


class AgentEnvs(BaseModel):
    NUVLAEDGE_API_KEY: str
    NUVLAEDGE_API_SECRET: str
    NUVLAEDGE_UUID: str
    NUVLAEDGE_ENGINE_VERSION: str
    NUVLAEDGE_IMMUTABLE_SSH_PUB_KEY: str
    HOST_HOME: str
    VPN_INTERFACE_NAME: str
    NUVLA_ENDPOINT: str
    NUVLA_ENDPOINT_INSECURE: str


class SystemManagerEnvs(BaseModel):
    SKIP_MINIMUM_REQUIREMENTS: str
    NUVLAEDGE_DATA_GATEWAY_IMAGE: str


class ComputeAPIEnvs(BaseModel):
    HOST: str


class VPNClientEnvs(BaseModel):
    NUVLAEDGE_UUID: str
