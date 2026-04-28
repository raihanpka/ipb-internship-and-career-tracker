import uuid
import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DocumentRequestCreate(BaseModel):
    vacancy_id: Optional[uuid.UUID] = None
    purpose: str = Field(..., min_length=10, max_length=1000)


class DocumentRequestSubmitResponse(BaseModel):
    request_id: uuid.UUID
    task_id: Optional[str] = None
    message: str


class DocumentRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_type: str
    student_id: Optional[uuid.UUID] = None
    reference_vacancy_id: Optional[uuid.UUID] = None
    purpose: Optional[str] = None
    status: Optional[str] = None
    generated_url: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
