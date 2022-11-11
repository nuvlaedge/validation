"""

"""

from pydantic import BaseModel

from common import Version


class EngineConfiguration(BaseModel):
    """
    This schema comprises all the microservice configuration for fine-tuning and single microservice configuration
    """
    version: Version  # NuvlaEdge overall release version for release and pre-release testing

    # Subcomponent configuration
    # Agent
