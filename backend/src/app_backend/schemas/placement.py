import uuid
import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class PlacementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    company_id: uuid.UUID
    start_date: datetime.date
    end_date: datetime.date
    application_id: Optional[uuid.UUID] = None
    external_supervisor_name: Optional[str] = None
    status: Optional[str] = None

class ActivityLogCreate(BaseModel):
    log_date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    description_raw: str

class ActivityLogUpdate(BaseModel):
    log_date: Optional[datetime.date] = None
    start_time: Optional[datetime.time] = None
    end_time: Optional[datetime.time] = None
    description_raw: Optional[str] = None

class ActivityLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    placement_id: uuid.UUID
    activity_date: datetime.date
    duration_hours: float
    description_raw: str
    description_ai_enhanced: Optional[str] = None
    attachment_url: Optional[str] = None
