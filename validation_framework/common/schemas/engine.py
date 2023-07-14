from pydantic import BaseModel, ConfigDict

from validation_framework.common import Release
import validation_framework.common.constants as cte


class EngineConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    version: Release | str
    title: str
    description: str
    project_name: str

    components: list
    peripherals: dict = {}


def to_capital(env_name: str) -> str:
    return env_name.upper()


class EngineEnvsConfiguration(BaseModel):
    model_config = ConfigDict(validate_assignment=True,
                              populate_by_name=True,
                              alias_generator=to_capital)

    nuvlabox_uuid: str | None = None
    nuvlaedge_uuid: str | None = None
    compose_project_name: str = cte.PROJECT_NAME
    ne_image_tag: str | None = None
    ne_image_organization: str | None = None
    ne_image_repository: str = cte.DOCKER_REPOSITORY_NAME
