"""Datu modeļi pēc API līguma (API contract) docs/openapi.yaml."""

import re
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError

# CR-1: DDMMYY-NNNNN vai 11 cipari. [0-9], nevis \d: \d pieņem arī citu rakstu ciparus.
PERSONAL_CODE_RE = re.compile(r"[0-9]{6}-?[0-9]{5}")


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


class SubmissionFields(BaseModel):
    personalCode: str
    fullName: str
    email: str  # TODO: pārbaudīt e-pasta formātu
    preferredChannel: PreferredChannel
    topic: Topic
    subject: str
    body: str


class SubmissionCreate(SubmissionFields):
    # Pārbaude tikai ievadei: saglabātos ierakstus lasot nepārbauda (CR-1).
    @field_validator("personalCode")
    @classmethod
    def normalize_personal_code(cls, value: str) -> str:
        # Kļūdas ziņojumā ievadīto vērtību neatkārtojam (CR-1).
        value = value.strip()
        if not value:
            raise PydanticCustomError("missing", "Field required")
        if not PERSONAL_CODE_RE.fullmatch(value):
            raise ValueError("invalid format")
        return value.replace("-", "")


class SubmissionCreated(BaseModel):
    id: str
    status: SubmissionStatus
    receivedAt: datetime
    dueDate: date
    replyChannel: ReplyChannel
    reasonCode: str | None = None


class Submission(SubmissionCreated, SubmissionFields):
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
