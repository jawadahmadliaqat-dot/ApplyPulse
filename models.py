from datetime import datetime
from enum import StrEnum
from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import BaseModel, EmailStr, Field, field_validator


class JobStatus(StrEnum):
    SAVED = "Saved"
    NEW_MATCH = "New Match"
    APPLIED = "Applied"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"
    POSITION_CLOSED = "Position Closed"


def normalize_job_url(value: Optional[str]) -> Optional[str]:
    if not value or not value.strip():
        return None

    parsed = urlsplit(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("job_url must be a valid http or https URL")

    tracking_keys = {"fbclid", "gclid", "ref", "refId", "trk", "trackingId"}
    query = urlencode(
        [
            (key, item)
            for key, item in parse_qsl(parsed.query)
            if key not in tracking_keys and not key.lower().startswith("utm_")
        ]
    )
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path.rstrip("/"), query, ""))

# --- Auth Models ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime

# --- Job Models ---
class JobCreate(BaseModel):
    title: str = Field(..., min_length=1)
    company: str = Field(..., min_length=1)
    location: Optional[str] = None
    status: JobStatus = Field(default=JobStatus.SAVED)
    notes: Optional[str] = None
    job_url: Optional[str] = None
    source: Optional[str] = None
    salary: Optional[str] = Field(default=None, max_length=120)
    experience_level: Optional[str] = Field(default=None, max_length=80)
    work_type: Optional[str] = Field(default=None, max_length=40)
    resume_version: Optional[str] = Field(default=None, max_length=160)
    follow_up_date: Optional[datetime] = None
    application_date: Optional[datetime] = None
    response_date: Optional[datetime] = None

    @staticmethod
    def validate_job_url(value: Optional[str]) -> Optional[str]:
        return normalize_job_url(value)

    _normalize_url = field_validator("job_url")(validate_job_url)

class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    status: Optional[JobStatus] = None
    notes: Optional[str] = None
    job_url: Optional[str] = None
    source: Optional[str] = None
    salary: Optional[str] = Field(default=None, max_length=120)
    experience_level: Optional[str] = Field(default=None, max_length=80)
    work_type: Optional[str] = Field(default=None, max_length=40)
    resume_version: Optional[str] = Field(default=None, max_length=160)
    follow_up_date: Optional[datetime] = None
    application_date: Optional[datetime] = None
    response_date: Optional[datetime] = None

    _normalize_url = field_validator("job_url")(normalize_job_url)

class JobResponse(BaseModel):
    id: str
    user_id: str
    title: str
    company: str
    location: Optional[str] = None
    status: str
    notes: Optional[str] = None
    job_url: Optional[str] = None
    source: Optional[str] = None
    salary: Optional[str] = None
    experience_level: Optional[str] = None
    work_type: Optional[str] = None
    resume_version: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    application_date: Optional[datetime] = None
    response_date: Optional[datetime] = None
    created_at: datetime