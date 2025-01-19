import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, FilePath, HttpUrl


class ApplicationStatus(Enum):
    PENDING = "pending"
    APPLICATION_CONFIRMATION = "application_confirmation"
    INVITATION_TO_INTERVIEW = "invitation_to_interview"
    OFFER_RECEIVED = "offer_received"
    REJECTED = "rejected"


class JobListing(BaseModel):
    id: UUID
    tracking_urn: str
    url: HttpUrl
    title: str
    location: str
    company: str | None = None
    description: str | None = None
    reposted: bool = False
    poster_id: str | None = None
    keywords: list[str] = []
    cv_path: FilePath | None = None
    cv_changes: list[str] = []
    status: ApplicationStatus = ApplicationStatus.PENDING
    application_date: datetime.datetime | None = None


class CvCustomizationResponse(BaseModel):
    resume: FilePath
    changes: list[str]


class EmailValidationResponse(BaseModel):
    sender: str
    subject: str
    is_job_related: bool
    notification_category: str
