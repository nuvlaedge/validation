from pydantic import BaseModel

from common import Release


class EngineConfig(BaseModel):
    version: Release | None
    title: str
    description: str
    project_name: str

    components: list
    peripherals: dict = {}


