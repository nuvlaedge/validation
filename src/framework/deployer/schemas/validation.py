"""

"""

from pydantic import BaseModel

from framework.deployer.schemas.engine_configuration import EngineConfiguration


class ValidationSchema(BaseModel):
    name: str
    description: str

    engine_configuration: EngineConfiguration

    run_time: int  # Experiment runtime in seconds
