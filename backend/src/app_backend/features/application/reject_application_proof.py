from dataclasses import dataclass
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app_backend.models.applications import Applications

@dataclass
class RejectApplicationProofCommand:
    application_id: uuid.UUID
    admin_id: uuid.UUID
    reason: str

@dataclass
class RejectApplicationProofResult:
    application: Optional[Applications] = None
    error_message: Optional[str] = None

    def got_error(self) -> bool:
        return self.error_message is not None

def reject_application_proof_command_handler(
    command: RejectApplicationProofCommand,
    session: Session,
) -> RejectApplicationProofResult:
    application = session.query(Applications).filter_by(id=command.application_id, status="ACCEPTED").first()
    
    if not application:
        return RejectApplicationProofResult(error_message="Lamaran tidak ditemukan atau belum ACCEPTED")

    application.status = "OFFERED"
    application._changed_by = command.admin_id
    application._reason = command.reason
    
    session.commit()
    session.refresh(application)
    
    return RejectApplicationProofResult(application=application)
