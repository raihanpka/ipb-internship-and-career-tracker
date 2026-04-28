from dataclasses import dataclass
from typing import List, Optional
from sqlalchemy.orm import Session
from app_backend.models.applications import Applications

@dataclass
class ListPendingVerificationCommand:
    pass

@dataclass
class ListPendingVerificationResult:
    items: Optional[List[Applications]] = None
    error_message: Optional[str] = None

    def got_error(self) -> bool:
        return self.error_message is not None

def list_pending_verification_command_handler(
    command: ListPendingVerificationCommand,
    session: Session,
) -> ListPendingVerificationResult:
    applications = session.query(Applications).filter_by(status="ACCEPTED").order_by(Applications.updated_at.asc()).all()
    
    return ListPendingVerificationResult(items=applications)
