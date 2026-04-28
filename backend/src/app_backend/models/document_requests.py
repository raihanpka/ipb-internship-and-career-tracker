"""
Model: public.document_requests
Permohonan surat pengantar/rekomendasi kampus.
"""

from __future__ import annotations

import datetime
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKeyConstraint, String, Text, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app_backend.models.base import Base

if TYPE_CHECKING:
    from app_backend.models.profiles_student import ProfilesStudent
    from app_backend.models.vacancies import Vacancies


class DocumentRequests(Base):
    __tablename__ = "document_requests"
    __table_args__ = (
        ForeignKeyConstraint(
            ["reference_vacancy_id"],
            ["vacancies.id"],
            ondelete="SET NULL",
            name="document_requests_reference_vacancy_id_fkey",
        ),
        ForeignKeyConstraint(
            ["student_id"],
            ["profiles_student.user_id"],
            ondelete="CASCADE",
            name="document_requests_student_id_fkey",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("public.gen_random_uuid()")
    )
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    student_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    reference_vacancy_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    purpose: Mapped[Optional[str]] = mapped_column(Text)
    generated_url: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(
        String(20), server_default=text("'PENDING'::character varying")
    )
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(True), server_default=text("CURRENT_TIMESTAMP")
    )

    # Relationships
    reference_vacancy: Mapped[Optional["Vacancies"]] = relationship(
        "Vacancies", back_populates="document_requests"
    )
    student: Mapped[Optional["ProfilesStudent"]] = relationship(
        "ProfilesStudent", back_populates="document_requests"
    )
