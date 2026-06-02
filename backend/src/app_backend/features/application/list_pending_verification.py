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
    from sqlalchemy.orm import joinedload
    from app_backend.models.vacancies import Vacancies
    from app_backend.models.profiles_student import ProfilesStudent

    applications = (
        session.query(Applications)
        .options(
            joinedload(Applications.student).joinedload(ProfilesStudent.user),
            joinedload(Applications.vacancy).joinedload(Vacancies.company),
            joinedload(Applications.application_logs),
        )
        .filter(Applications.status.in_(["APPLIED", "ACCEPTED"]))
        .order_by(Applications.updated_at.asc())
        .all()
    )

    # Tampilkan lamaran yang APPLIED (untuk didaftarkan oleh admin) ATAU ACCEPTED yang punya bukti LoA (untuk dibuat Placement)
    applications_with_proof = [
        app for app in applications 
        if app.status == "APPLIED" or any(log.proof_url for log in app.application_logs)
    ]

    return ListPendingVerificationResult(items=applications_with_proof)
