from dataclasses import dataclass
from typing import Optional
import uuid

from sqlalchemy.orm import Session

from app_backend.models.document_requests import DocumentRequests
from app_backend.models.profiles_student import ProfilesStudent
from app_backend.models.vacancies import Vacancies
from app_backend.shared.tasks.document_tasks import generate_cover_letter


@dataclass
class CreateDocumentRequestCommand:
    student_id: uuid.UUID
    purpose: str
    vacancy_id: Optional[uuid.UUID] = None


@dataclass
class CreateDocumentRequestResult:
    request_id: Optional[uuid.UUID] = None
    task_id: Optional[str] = None
    message: Optional[str] = None
    error_message: Optional[str] = None
    error_code: int = 400

    def got_error(self) -> bool:
        return self.error_message is not None


def create_document_request_command_handler(
    command: CreateDocumentRequestCommand,
    session: Session,
) -> CreateDocumentRequestResult:
    student = session.query(ProfilesStudent).filter_by(user_id=command.student_id).first()
    if not student:
        return CreateDocumentRequestResult(
            error_message="Profil mahasiswa tidak ditemukan", error_code=404
        )

    if command.vacancy_id is not None:
        vacancy = session.query(Vacancies).filter_by(id=command.vacancy_id).first()
        if not vacancy:
            return CreateDocumentRequestResult(
                error_message="Lowongan tidak ditemukan", error_code=404
            )

    doc_request = DocumentRequests(
        document_type="INTRODUCTION_LETTER",
        student_id=command.student_id,
        reference_vacancy_id=command.vacancy_id,
        purpose=command.purpose,
        status="PENDING",
    )
    session.add(doc_request)
    session.flush()

    request_id = doc_request.id
    session.commit()

    task = generate_cover_letter.apply_async(
        args=[str(request_id)],
        queue="document",
    )

    return CreateDocumentRequestResult(
        request_id=request_id,
        task_id=task.id,
        message="Permohonan surat pengantar sedang diproses. Gunakan GET /document-requests/{id} untuk mengecek status.",
    )
