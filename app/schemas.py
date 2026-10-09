from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from .models import JobStatus, CertificateStatus

class RecipientCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Recipient full name")
    course: str = Field(..., min_length=1, description="Course or event name")

class JobCreate(BaseModel):
    recipients: List[RecipientCreate]

class RawTextJobCreate(BaseModel):
    text: str = Field(..., min_length=1, description="Raw CSV or plain text with lines formatted as 'Name, Course'")

class CertificateResponse(BaseModel):
    id: int
    recipient_name: str
    course_name: str
    status: CertificateStatus
    file_path: Optional[str] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class JobResponse(BaseModel):
    id: int
    status: JobStatus
    certificates: List[CertificateResponse] = []

    model_config = ConfigDict(from_attributes=True)
