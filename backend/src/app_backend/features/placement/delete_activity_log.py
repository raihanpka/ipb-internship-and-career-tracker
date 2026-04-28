from dataclasses import dataclass
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app_backend.models.activity_logs import ActivityLogs
from app_backend.models.placements import Placements

@dataclass
class DeleteActivityLogCommand:
    placement_id: uuid.UUID
    log_id: uuid.UUID
    student_id: uuid.UUID

@dataclass
class DeleteActivityLogResult:
    error_message: Optional[str] = None
    error_code: int = 400

    def got_error(self) -> bool:
        return self.error_message is not None

def delete_activity_log_command_handler(
    command: DeleteActivityLogCommand,
    session: Session,
) -> DeleteActivityLogResult:
    placement = session.query(Placements).filter_by(id=command.placement_id, student_id=command.student_id).first()
    if not placement:
        return DeleteActivityLogResult(error_message="Placement tidak ditemukan", error_code=404)

    log = session.query(ActivityLogs).filter_by(id=command.log_id, placement_id=placement.id).first()
    if not log:
        return DeleteActivityLogResult(error_message="Activity log tidak ditemukan", error_code=404)

    session.delete(log)
    session.commit()
    
    return DeleteActivityLogResult()
