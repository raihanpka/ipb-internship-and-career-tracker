from dataclasses import dataclass, field
from typing import List, Optional
import uuid

from sqlalchemy.orm import Session

from app_backend.models.document_requests import DocumentRequests


@dataclass
class ListDocumentRequestsCommand:
    student_id: uuid.UUID


@dataclass
class ListDocumentRequestsResult:
    requests: List[DocumentRequests] = field(default_factory=list)
    error_message: Optional[str] = None
    error_code: int = 400

    def got_error(self) -> bool:
        return self.error_message is not None


def list_document_requests_command_handler(
    command: ListDocumentRequestsCommand,
    session: Session,
) -> ListDocumentRequestsResult:
    requests = (
        session.query(DocumentRequests)
        .filter_by(student_id=command.student_id)
        .order_by(DocumentRequests.created_at.desc())
        .all()
    )
    return ListDocumentRequestsResult(requests=requests)
