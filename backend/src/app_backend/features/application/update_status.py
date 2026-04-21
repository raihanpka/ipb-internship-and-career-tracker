import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app_backend.domain.application import Application
from app_backend.models.application_logs import ApplicationLogs
from app_backend.models.applications import Applications
from app_backend.schemas.application import ApplicationLogResponse, ApplicationResponse


@dataclass
class UpdateApplicationStatusCommand:
    application_id: uuid.UUID
    student_id: uuid.UUID
    new_status: str
    proof_url: Optional[str] = None
    reason: Optional[str] = None
    changed_by: Optional[uuid.UUID] = None


@dataclass
class UpdateApplicationStatusResult:
    application: Optional[ApplicationResponse] = None
    log: Optional[ApplicationLogResponse] = None
    error_message: Optional[str] = None
    error_status_code: int = field(default=400)


def update_application_status_command_handler(
    command: UpdateApplicationStatusCommand,
    session: Session,
) -> UpdateApplicationStatusResult:
    # 1. Fetch application
    application = session.get(Applications, command.application_id)
    if application is None:
        return UpdateApplicationStatusResult(
            error_message="Lamaran tidak ditemukan.",
            error_status_code=404,
        )

    # 2. Verify ownership — student may only update their own application
    if application.student_id != command.student_id:
        return UpdateApplicationStatusResult(
            error_message="Anda tidak memiliki izin untuk mengubah lamaran ini.",
            error_status_code=403,
        )

    # 3. Domain-level status transition validation
    domain_app = Application(
        id=application.id,
        vacancy_id=application.vacancy_id,
        student_id=application.student_id,
        status=application.status,
    )
    try:
        domain_app.update_status(command.new_status)
    except ValueError as e:
        return UpdateApplicationStatusResult(error_message=str(e))

    # 4. Persist update and create audit log in one transaction
    previous_status = application.status
    application.status = command.new_status
    application.updated_at = datetime.now(timezone.utc)

    log = ApplicationLogs(
        application_id=application.id,
        new_status=command.new_status,
        previous_status=previous_status,
        changed_by=command.changed_by,
        proof_url=command.proof_url,
        reason=command.reason,
    )
    session.add(log)
    session.commit()
    session.refresh(application)
    session.refresh(log)

    return UpdateApplicationStatusResult(
        application=ApplicationResponse.model_validate(application),
        log=ApplicationLogResponse.model_validate(log),
    )
