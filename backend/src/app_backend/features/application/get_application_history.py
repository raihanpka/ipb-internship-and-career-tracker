from dataclasses import dataclass
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app_backend.models.application_logs import ApplicationLogs
from app_backend.models.applications import Applications

@dataclass
class GetApplicationHistoryCommand:
    application_id: uuid.UUID
    student_id: uuid.UUID

@dataclass
class GetApplicationHistoryResult:
    logs: Optional[List[ApplicationLogs]] = None
    error_message: Optional[str] = None

    def got_error(self) -> bool:
        return self.error_message is not None

def get_application_history_command_handler(
    command: GetApplicationHistoryCommand,
    session: Session,
) -> GetApplicationHistoryResult:
    application = session.query(Applications).filter_by(id=command.application_id, student_id=command.student_id).first()
    
    if not application:
        return GetApplicationHistoryResult(error_message="Lamaran tidak ditemukan")
        
    logs = session.query(ApplicationLogs).filter_by(application_id=command.application_id).order_by(ApplicationLogs.created_at.asc()).all()
    
    return GetApplicationHistoryResult(logs=logs)
