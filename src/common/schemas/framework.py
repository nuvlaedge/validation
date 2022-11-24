"""

"""
from enum import StrEnum, auto
import uuid
from pydantic import BaseModel


class States(StrEnum):
    RUNNING = auto()
    FINISHED = auto()
    ERROR = auto()
    NOTFOUND = auto()
    UNKNOWN = auto()


class FrameWorkConfig(BaseModel):
    ...


class FrameWorkStatus(BaseModel):
    configuration: FrameWorkConfig
    status: States
    uuid: uuid.UUID
