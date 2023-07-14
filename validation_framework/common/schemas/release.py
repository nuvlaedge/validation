"""

"""
from pydantic import BaseModel, ConfigDict

from validation_framework.common.release import Release


class TargetReleaseConfig(BaseModel):
    """
    Release configuration for custom NuvlaEdge
    """
    # Model configuration
    model_config = ConfigDict(arbitrary_types_allowed=True)

    nuvlaedge_version: str

    nuvlaedge_branch: str
    deployment_branch: str


class ReleaseSchema(BaseModel):
    """
    Forms a schema for standardize releases from remote GH repo
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # NuvlaEdge deployment release tag
    tag: Release
    # Available files to download (Based on .yml deployment files)
    components: list[str] = []
    prerelease: bool = False

    # The Engine handler will fill this list with the locations of the files, once downloaded
    downloaded_files: list[str] = []
