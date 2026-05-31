import datetime
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app_backend.models.base import Base

if TYPE_CHECKING:
    from app_backend.models.activity_logs import ActivityLogs
    from app_backend.models.applications import Applications
    from app_backend.models.master_external_companies import MasterExternalCompanies
    from app_backend.models.profiles_student import ProfilesStudent


class Placements(Base):
    __tablename__ = "placements"
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="placements_check"),
        ForeignKeyConstraint(
            ["application_id"],
            ["applications.id"],
            ondelete="RESTRICT",
            name="placements_application_id_fkey",
        ),
        ForeignKeyConstraint(
            ["company_id"],
            ["master_external_companies.id"],
            ondelete="RESTRICT",
            name="placements_company_id_fkey",
        ),
        ForeignKeyConstraint(
            ["student_id"],
            ["profiles_student.user_id"],
            ondelete="CASCADE",
            name="placements_student_id_fkey",
        ),
        UniqueConstraint("application_id", name="placements_application_id_key"),
        Index("idx_placements_student", "student_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    end_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    application_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    external_supervisor_name: Mapped[Optional[str]] = mapped_column(String(150))
    status: Mapped[Optional[str]] = mapped_column(
        Enum(
            "ACTIVE",
            "COMPLETED",
            "DROPPED",
            "EXTENDED",
            name="placement_status_enum",
        ),
        server_default=text("'ACTIVE'::placement_status_enum"),
    )
    auto_generated_report_url: Mapped[Optional[str]] = mapped_column(Text)
    last_report_generated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("CURRENT_TIMESTAMP"))

    # Relationships
    application: Mapped[Optional["Applications"]] = relationship("Applications", back_populates="placements")
    company: Mapped["MasterExternalCompanies"] = relationship("MasterExternalCompanies", back_populates="placements")
    student: Mapped["ProfilesStudent"] = relationship("ProfilesStudent", back_populates="placements")
    activity_logs: Mapped[list["ActivityLogs"]] = relationship("ActivityLogs", back_populates="placement")

    @property
    def student_name(self) -> Optional[str]:
        return self.student.full_name if self.student else None

    @property
    def student_nim(self) -> Optional[str]:
        return self.student.nim if self.student else None

    @property
    def company_name(self) -> Optional[str]:
        return self.company.name if self.company else None
