"""

"""
from pydantic import BaseModel

from validation_framework.common.release import Release


class TargetReleaseConfig(BaseModel):
    """
    Release configuration for custom NuvlaEdge
    """
    tag: Release | None = None
    std_release: bool = True
    # If none, all available files will be targeted
    repository: str | None = None
    branch: str | None = None

    # Peripheral handling
    include_peripherals: bool = False
    peripherals: list[str] = None
    # If release is custom this section must be completely filled
    # TODO: Future implementations of custom engine validation


class ReleaseSchema(BaseModel):
    """
    Forms a schema for standardize releases from remote GH repo
    """
    # NuvlaEdge deployment release tag
    tag: Release
    # Available files to download (Based on .yml deployment files)
    components: list[str] = []
    prerelease: bool = False

    # The Engine handler will fill this list with the locations of the files, once downloaded
    downloaded_files: list[str] = []
