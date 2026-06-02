import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator


class ApplicationCreate(BaseModel):
    vacancy_id: uuid.UUID


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
    match_percentage: Optional[float] = None


class VacancyMinimalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    type: str
    location: Optional[str] = None
    payment_type: Optional[str] = None
    company_name: str
    company_logo: Optional[str] = None


class ApplicationDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vacancy_id: uuid.UUID
    student_id: uuid.UUID
    cv_snapshot_url: str
    status: str
    match_percentage: Optional[float] = None
    applied_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    vacancy: Optional[VacancyMinimalResponse] = None
    admin_notes: Optional[str] = None
    student_reply: Optional[str] = None


class ApplicationUpdateStatus(BaseModel):
    status: str
    reason: str | None = None
    proof_url: str | None = None


class ApplicationVerifyPayload(BaseModel):
    start_date: date
    end_date: date


class ApplicationRejectPayload(BaseModel):
    reason: str


class ApplicationAdminNotesPayload(BaseModel):
    admin_notes: str


class ApplicationStudentReplyPayload(BaseModel):
    student_reply: str


class UserMinimal(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: str
    full_name: str

    @model_validator(mode="before")
    @classmethod
    def resolve_fields(cls, data):
        if not isinstance(data, dict):
            profile_student = getattr(data, "profile_student", None)
            profile_admin = getattr(data, "profile_admin", None)
            full_name = ""
            if profile_student:
                full_name = profile_student.full_name
            elif profile_admin:
                full_name = profile_admin.full_name
            return {
                "id": data.id,
                "email": data.email,
                "full_name": full_name,
            }
        return data


class StudentMinimalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: uuid.UUID
    nim: str
    full_name: str
    user: UserMinimal


class CompanyMinimal(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    logo_url: Optional[str] = None


class VacancyAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    type: str
    location: Optional[str] = None
    payment_type: Optional[str] = None
    company: CompanyMinimal


class AdminApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vacancy_id: uuid.UUID
    student_id: uuid.UUID
    cv_snapshot_url: str
    cv_url: str
    status: str
    created_at: datetime
    student: StudentMinimalResponse
    vacancy: VacancyAdminResponse
    match_percentage: Optional[float] = None
    proof_url: Optional[str] = None
    admin_notes: Optional[str] = None
    student_reply: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def map_created_at(cls, data):
        if not isinstance(data, dict):
            applied_at = getattr(data, "applied_at", None)
            cv_snapshot_url = getattr(data, "cv_snapshot_url", "")
            match_percentage = getattr(data, "match_percentage", None)
            if match_percentage is not None:
                match_percentage = float(match_percentage)
            logs = list(getattr(data, "application_logs", []) or [])
            logs_with_proof = [log for log in logs if getattr(log, "proof_url", None)]
            logs_with_proof.sort(key=lambda log: str(getattr(log, "created_at", "") or ""), reverse=True)
            return {
                "id": data.id,
                "vacancy_id": data.vacancy_id,
                "student_id": data.student_id,
                "cv_snapshot_url": cv_snapshot_url,
                "cv_url": cv_snapshot_url,
                "status": data.status,
                "created_at": applied_at or datetime.now(),
                "student": data.student,
                "vacancy": data.vacancy,
                "match_percentage": match_percentage,
                "proof_url": logs_with_proof[0].proof_url if logs_with_proof else None,
                "admin_notes": getattr(data, "admin_notes", None),
                "student_reply": getattr(data, "student_reply", None),
            }
        return data
