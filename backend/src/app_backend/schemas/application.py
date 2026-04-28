import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app_backend.domain.application import ApplicationStatus


class ApplicationCreate(BaseModel):
    vacancy_id: uuid.UUID


class ApplicationStatusUpdate(BaseModel):
    new_status: str
    proof_url: Optional[str] = None
    reason: Optional[str] = None

    @field_validator("new_status")
    @classmethod
    def validate_new_status(cls, v: str) -> str:
        valid = [s.value for s in ApplicationStatus]
        if v not in valid:
            raise ValueError(f"Status tidak valid. Pilih salah satu: {', '.join(valid)}")
        return v

    @model_validator(mode="after")
    def require_proof_url_for_accepted(self) -> "ApplicationStatusUpdate":
        if self.new_status == ApplicationStatus.ACCEPTED.value and not self.proof_url:
            raise ValueError("proof_url wajib diisi saat status diubah ke ACCEPTED")
        return self


class ApplicationLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    new_status: str
    previous_status: Optional[str] = None
    changed_by: Optional[uuid.UUID] = None
    proof_url: Optional[str] = None
    reason: Optional[str] = None
    created_at: Optional[datetime] = None


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vacancy_id: uuid.UUID
    student_id: uuid.UUID
    cv_snapshot_url: str
    status: str


class ApplicationStatusUpdateResponse(BaseModel):
    application: ApplicationResponse
    log: ApplicationLogResponse
class ApplicationUpdateStatus(BaseModel):
    status: str
    reason: str | None = None
    proof_url: str | None = None

class ApplicationLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    new_status: str
    previous_status: str | None = None
    proof_url: str | None = None
    reason: str | None = None
    changed_by: uuid.UUID | None = None

import datetime

class ApplicationVerifyPayload(BaseModel):
    start_date: datetime.date
    end_date: datetime.date

class ApplicationRejectPayload(BaseModel):
    reason: str
