from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy.orm import Session

from app_backend.models.document_requests import DocumentRequests


@dataclass
class GetDocumentRequestCommand:
    request_id: uuid.UUID
    student_id: uuid.UUID


@dataclass
class GetDocumentRequestResult:
    request: Optional[DocumentRequests] = None
    error_message: Optional[str] = None
    error_code: int = 400

    def got_error(self) -> bool:
        return self.error_message is not None


def get_document_request_command_handler(
    command: GetDocumentRequestCommand,
    session: Session,
) -> GetDocumentRequestResult:
    doc_request = session.query(DocumentRequests).filter_by(
        id=command.request_id,
        student_id=command.student_id,
    ).first()

    if not doc_request:
        return GetDocumentRequestResult(
            error_message="Permohonan surat tidak ditemukan", error_code=404
        )

    return GetDocumentRequestResult(request=doc_request)
