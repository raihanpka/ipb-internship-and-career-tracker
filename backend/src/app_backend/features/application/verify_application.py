from dataclasses import dataclass
import uuid
import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app_backend.models.applications import Applications
from app_backend.models.placements import Placements
from app_backend.models.vacancies import Vacancies

@dataclass
class VerifyApplicationCommand:
    application_id: uuid.UUID
    admin_id: uuid.UUID
    start_date: datetime.date
    end_date: datetime.date

@dataclass
class VerifyApplicationResult:
    placement: Optional[Placements] = None
    error_message: Optional[str] = None

    def got_error(self) -> bool:
        return self.error_message is not None

def verify_application_command_handler(
    command: VerifyApplicationCommand,
    session: Session,
) -> VerifyApplicationResult:
    application = session.query(Applications).filter_by(id=command.application_id, status="ACCEPTED").first()
    
    if not application:
        return VerifyApplicationResult(error_message="Lamaran tidak ditemukan atau belum ACCEPTED")

    # Ensure no placement exists
    existing = session.query(Placements).filter_by(application_id=command.application_id).first()
    if existing:
        return VerifyApplicationResult(error_message="Penempatan sudah aktif untuk lamaran ini")

    vacancy = session.query(Vacancies).filter_by(id=application.vacancy_id).first()
    if not vacancy:
        return VerifyApplicationResult(error_message="Lowongan tidak ditemukan")

    # Create placement
    placement = Placements(
        student_id=application.student_id,
        company_id=vacancy.company_id,
        start_date=command.start_date,
        end_date=command.end_date,
        application_id=application.id,
        status="ACTIVE"
    )
    
    session.add(placement)
    
    # We could also add a log to application_logs saying verified, but changing status is easier.
    # The prompt doesn't specify changing status from ACCEPTED to VERIFIED, it just says "trigger pembuatan Placement record".
    
    session.commit()
    session.refresh(placement)
    
    return VerifyApplicationResult(placement=placement)
