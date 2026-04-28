"""
Model: public.applications
Rekaman pelamaran mahasiswa ke lowongan (Self-Reported ATS).
"""

from __future__ import annotations

import datetime
import decimal
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (DateTime, Enum, ForeignKeyConstraint, Index, Numeric,
                        Text, UniqueConstraint, Uuid, text, event)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.attributes import get_history

from app_backend.models.base import Base

if TYPE_CHECKING:
    from app_backend.models.application_logs import ApplicationLogs
    from app_backend.models.placements import Placements
    from app_backend.models.profiles_student import ProfilesStudent
    from app_backend.models.vacancies import Vacancies


class Applications(Base):
    __tablename__ = "applications"
    __table_args__ = (
        ForeignKeyConstraint(
            ["student_id"],
            ["profiles_student.user_id"],
            ondelete="CASCADE",
            name="applications_student_id_fkey",
        ),
        ForeignKeyConstraint(
            ["vacancy_id"],
            ["vacancies.id"],
            ondelete="RESTRICT",
            name="applications_vacancy_id_fkey",
        ),
        UniqueConstraint(
            "vacancy_id", "student_id", name="applications_vacancy_id_student_id_key"
        ),
        Index("idx_apps_student", "student_id", "status"),
        Index("idx_apps_vacancy", "vacancy_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("public.gen_random_uuid()")
    )
    vacancy_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    cv_snapshot_url: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[Optional[str]] = mapped_column(
        Enum(
            "APPLIED",
            "SCREENING",
            "INTERVIEW",
            "OFFERED",
            "ACCEPTED",
            "REJECTED",
            "WITHDRAWN",
            name="app_status_enum",
        ),
        server_default=text("'APPLIED'::app_status_enum"),
    )
    match_percentage: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    applied_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(True), server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(True), server_default=text("CURRENT_TIMESTAMP")
    )

    # Relationships
    student: Mapped["ProfilesStudent"] = relationship(
        "ProfilesStudent", back_populates="applications"
    )
    vacancy: Mapped["Vacancies"] = relationship(
        "Vacancies", back_populates="applications"
    )
    application_logs: Mapped[list["ApplicationLogs"]] = relationship(
        "ApplicationLogs", back_populates="application"
    )
    placements: Mapped[Optional["Placements"]] = relationship(
        "Placements", uselist=False, back_populates="application"
    )


@event.listens_for(Applications, 'after_update')
def receive_after_update(mapper, connection, target):
    hist = get_history(target, 'status')
    if hist.has_changes():
        old_status = hist.deleted[0] if hist.deleted else None
        new_status = hist.added[0] if hist.added else target.status
        
        changed_by = getattr(target, '_changed_by', None)
        proof_url = getattr(target, '_proof_url', None)
        reason = getattr(target, '_reason', None)
        
        connection.execute(
            text("""
            INSERT INTO application_logs (id, application_id, previous_status, new_status, changed_by, proof_url, reason)
            VALUES (public.gen_random_uuid(), :app_id, :prev, :new, :by, :proof, :reason)
            """),
            {
                "app_id": target.id,
                "prev": old_status,
                "new": new_status,
                "by": changed_by,
                "proof": proof_url,
                "reason": reason
            }
        )

@event.listens_for(Applications, 'after_insert')
def receive_after_insert(mapper, connection, target):
    changed_by = getattr(target, '_changed_by', target.student_id)
    
    connection.execute(
        text("""
        INSERT INTO application_logs (id, application_id, previous_status, new_status, changed_by)
        VALUES (public.gen_random_uuid(), :app_id, NULL, :new, :by)
        """),
        {
            "app_id": target.id,
            "new": target.status,
            "by": changed_by,
        }
    )

