""" Schema for Nuvla User configuration """

from datetime import datetime
from typing import Optional

from pydantic import BaseSettings, Field, BaseModel, Extra

from validation_framework.common.nuvla_uuid import NuvlaUUID


class UserSchema(BaseSettings):
    API_KEY: str = Field('', env='NUVLA_API_KEY')
    API_SECRET: str = Field('', env='NUVLA_API_SECRET')
    name: Optional[str]
    updated: Optional[datetime]
    created: Optional[datetime]
    state: Optional[str]
    resource_type: str = Field('', alias='resource-type', env='')
    id: Optional[NuvlaUUID]

    class Config:
        allow_population_by_field_name = True
        extra = Extra.ignore


class SessionSchema(BaseModel):
    # Session tools
    method: str = ''
    id: NuvlaUUID = ''
    resource_type: str = Field('', alias='resource-type', env='')

    # User data
    roles: Optional[str] = ''
    client_ip: str = Field('', alias='client-ip')
    created_by: str = Field('', alias='created-by')
    identifier: NuvlaUUID = ''
    user: NuvlaUUID = ''

    # Dates
    expiry: Optional[datetime]
    updated: Optional[datetime]
    created: Optional[datetime]

    class Config:
        allow_population_by_field_name = True



