from dataclasses import dataclass
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app_backend.models.applications import Applications

@dataclass
class UpdateApplicationStatusCommand:
    application_id: uuid.UUID
    student_id: uuid.UUID
    new_status: str
    proof_url: Optional[str] = None
    reason: Optional[str] = None

@dataclass
class UpdateApplicationStatusResult:
    application: Optional[Applications] = None
    error_message: Optional[str] = None

    def got_error(self) -> bool:
        return self.error_message is not None

def update_application_status_command_handler(
    command: UpdateApplicationStatusCommand,
    session: Session,
) -> UpdateApplicationStatusResult:
    # Validate transition
    valid_statuses = ["APPLIED", "SCREENING", "INTERVIEW", "OFFERED", "ACCEPTED", "REJECTED", "WITHDRAWN"]
    
    if command.new_status not in valid_statuses:
        return UpdateApplicationStatusResult(error_message="Status tidak valid")
        
    status_order = {
        "APPLIED": 0,
        "SCREENING": 1,
        "INTERVIEW": 2,
        "OFFERED": 3,
        "ACCEPTED": 4,
        "REJECTED": 4,
        "WITHDRAWN": 4
    }

    application = session.query(Applications).filter_by(id=command.application_id, student_id=command.student_id).first()
    
    if not application:
        return UpdateApplicationStatusResult(error_message="Lamaran tidak ditemukan")

    current_order = status_order.get(application.status, -1)
    new_order = status_order.get(command.new_status, -1)

    if new_order < current_order:
        return UpdateApplicationStatusResult(error_message="Tidak boleh mundur status")

    if current_order == new_order and application.status == command.new_status:
        return UpdateApplicationStatusResult(error_message="Status sudah sama")

    application.status = command.new_status
    application._changed_by = command.student_id
    application._reason = command.reason
    application._proof_url = command.proof_url
    
    session.commit()
    session.refresh(application)
    
    return UpdateApplicationStatusResult(application=application)
