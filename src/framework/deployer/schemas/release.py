"""

"""
from pydantic import BaseModel

from framework.deployer.common import Version


class ReleaseSchema(BaseModel):
    version: Version
    downloaded: bool
    downloaded_components: list[str] = []
    downloadable_assets: list[str] = []
    prerelease: bool = False
