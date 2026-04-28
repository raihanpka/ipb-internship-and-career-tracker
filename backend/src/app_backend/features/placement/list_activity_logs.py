from dataclasses import dataclass
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app_backend.models.activity_logs import ActivityLogs
from app_backend.models.placements import Placements

@dataclass
class ListActivityLogsCommand:
    placement_id: uuid.UUID
    student_id: uuid.UUID

@dataclass
class ListActivityLogsResult:
    logs: Optional[List[ActivityLogs]] = None
    error_message: Optional[str] = None

    def got_error(self) -> bool:
        return self.error_message is not None

def list_activity_logs_command_handler(
    command: ListActivityLogsCommand,
    session: Session,
) -> ListActivityLogsResult:
    placement = session.query(Placements).filter_by(id=command.placement_id, student_id=command.student_id).first()
    if not placement:
        return ListActivityLogsResult(error_message="Placement tidak ditemukan")

    logs = session.query(ActivityLogs).filter_by(placement_id=placement.id).order_by(ActivityLogs.activity_date.asc()).all()
    
    return ListActivityLogsResult(logs=logs)
