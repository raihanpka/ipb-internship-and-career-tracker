"""
Pydantic schemas untuk validasi request/response API wishlist
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ─────────────────────────────────────────────
# Nested Schemas
# ─────────────────────────────────────────────


class VacancySummary(BaseModel):
    """Summary info vacancy untuk wishlist"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    location: Optional[str] = None
    type: str
    payment_type: Optional[str] = None
    open_date: datetime
    close_date: datetime

class WishlistSummary(VacancySummary):
    """Backward-compatible alias for wishlist vacancy summary payloads."""
    id: UUID
    title: str
    location: Optional[str] = None
    type: str
    payment_type: Optional[str] = None
    open_date: datetime
    close_date: datetime


# ─────────────────────────────────────────────
# Create Schemas
# ─────────────────────────────────────────────


class WishlistCreate(BaseModel):
    """Payload untuk menyimpan vacancy ke wishlist"""

    vacancy_id: UUID
    notes: Optional[str] = Field(
        None, max_length=500, description="Catatan personal untuk lowongan ini"
    )


# ─────────────────────────────────────────────
# Update Schemas
# ─────────────────────────────────────────────


class WishlistUpdate(BaseModel):
    """Payload untuk update catatan wishlist"""

    notes: Optional[str] = Field(None, max_length=500)


# ─────────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────────


class WishlistResponse(BaseModel):
    """Response untuk data wishlist"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_id: UUID
    vacancy_id: UUID
    notes: Optional[str] = None
    created_at: datetime


class WishlistDetailResponse(BaseModel):
    """Response detail wishlist dengan vacancy info"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_id: UUID
    vacancy: VacancySummary
    notes: Optional[str] = None
    created_at: datetime


class WishlistListResponse(BaseModel):
    """Response untuk list wishlist student"""

    items: list[WishlistDetailResponse]
    total: int
