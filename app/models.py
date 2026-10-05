"""Datu modeļi pēc API līguma (API contract) docs/openapi.yaml."""

import re
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError

# CR-1: 11 cipari vai DDMMYY-NNNNN. Tikai formāts, bez kontrolcipara un datuma.
PERSONAL_CODE = re.compile(r"[0-9]{11}|[0-9]{6}-[0-9]{5}")


class PreferredChannel(str, Enum):
    EMAIL = "EMAIL"
    POST = "POST"
    E_ADDRESS = "E_ADDRESS"


class ReplyChannel(str, Enum):
    EMAIL = "EMAIL"
    POST = "POST"
    E_ADDRESS = "E_ADDRESS"


class Topic(str, Enum):
    ROADS = "ROADS"
    WASTE = "WASTE"
    PLANNING = "PLANNING"
    OTHER = "OTHER"


class SubmissionStatus(str, Enum):
    RECEIVED = "RECEIVED"
    IN_PROGRESS = "IN_PROGRESS"
    FORWARDED = "FORWARDED"
    ANSWERED = "ANSWERED"
    WITHDRAWN = "WITHDRAWN"


class SubmissionCreate(BaseModel):
    personalCode: str
    fullName: str
    email: str  # TODO: pārbaudīt e-pasta formātu
    preferredChannel: PreferredChannel
    topic: Topic
    subject: str
    body: str

    @field_validator("personalCode", mode="before")
    @classmethod
    def normalize_personal_code(cls, value: object) -> str:
        # Kļūdas tekstā ievadīto vērtību neatkārtojam: tie ir personas dati.
        if value is None or (isinstance(value, str) and not value.strip()):
            raise PydanticCustomError("missing", "Field required")
        if not isinstance(value, str) or not PERSONAL_CODE.fullmatch(value.strip()):
            raise PydanticCustomError("invalid_format", "Invalid format")
        return value.strip().replace("-", "")


class SubmissionCreated(BaseModel):
    id: str
    status: SubmissionStatus
    receivedAt: datetime
    dueDate: date
    replyChannel: ReplyChannel
    reasonCode: str | None = None


class Submission(SubmissionCreated, SubmissionCreate):
    pass


class Health(BaseModel):
    status: str
    version: str


class ErrorDetail(BaseModel):
    field: str
    issue: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] | None = None


class Error(BaseModel):
    error: ErrorBody
