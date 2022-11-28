""" Schema for NuvlaEdge configuration """
from typing import Optional, List

from pydantic import BaseModel, Field

from common.nuvla_uuid import NuvlaUUID
from common.release import Release


class EdgeSchema(BaseModel):
    name: str
    uuid: NuvlaUUID = Field('', alias='id')
    release: Optional[Release]
    version: Optional[str]
    tags: List[str] = ['validation=True']
    vpn_server_id: str = Field('infrastructure-service/eb8e09c2-8387-4f6d-86a4-ff5ddf3d07d7',
                               alias='vpn-server-id')
    refresh_interval: Optional[int] = Field(30, alias='refresh-interval')
