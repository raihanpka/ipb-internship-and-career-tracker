"""
Search Vacancies Feature – Command Handler.
Mencari lowongan berdasarkan filter.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload, selectinload

from app_backend.models.vacancies import Vacancies
from app_backend.models.vacancy_skills import VacancySkills
from app_backend.schemas.vacancy import (
    CompanyInfo,
    SkillRequirement,
    VacancyDetailResponse,
    VacancyListResponse,
)


class SearchVacanciesException(Exception):
    pass


@dataclass
class SearchVacanciesCommand:
    query: Optional[str] = None
    location: Optional[str] = None
    vacancy_type: Optional[str] = None
    payment_type: Optional[str] = None
    is_active: bool = True
    page: int = 1
    per_page: int = 10


@dataclass
class SearchVacanciesResult:
    data: Optional[VacancyListResponse] = None
    error_message: Optional[str] = None

    def got_error(self) -> bool:
        return self.error_message is not None


def search_vacancies_command_handler(
    command: SearchVacanciesCommand,
    session: Session,
) -> SearchVacanciesResult:
    """
    Search vacancies dengan berbagai filter.
    Menggunakan eager loading untuk menghindari N+1 query.
    """
    page = max(1, command.page)
    per_page = min(max(1, command.per_page), 100)
    offset = (page - 1) * per_page

    # Base query with eager loading untuk company dan vacancy_skills + skill
    query = session.query(Vacancies).options(
        joinedload(Vacancies.company),
        selectinload(Vacancies.vacancy_skills).joinedload(VacancySkills.skill),
    )

    # Filter by active status
    query = query.filter(Vacancies.is_active == command.is_active)

    # Filter by query (title or description)
    if command.query:
        search_term = f"%{command.query}%"
        query = query.filter(
            or_(
                Vacancies.title.ilike(search_term),
                Vacancies.description.ilike(search_term),
            )
        )

    # Filter by location
    if command.location:
        query = query.filter(Vacancies.location.ilike(f"%{command.location}%"))

    # Filter by vacancy type
    if command.vacancy_type:
        query = query.filter(Vacancies.type == command.vacancy_type)

    # Filter by payment type
    if command.payment_type:
        query = query.filter(Vacancies.payment_type == command.payment_type)

    # Get total count (tanpa eager loading untuk efisiensi)
    count_query = session.query(Vacancies).filter(Vacancies.is_active == command.is_active)
    if command.query:
        search_term = f"%{command.query}%"
        count_query = count_query.filter(
            or_(
                Vacancies.title.ilike(search_term),
                Vacancies.description.ilike(search_term),
            )
        )
    if command.location:
        count_query = count_query.filter(Vacancies.location.ilike(f"%{command.location}%"))
    if command.vacancy_type:
        count_query = count_query.filter(Vacancies.type == command.vacancy_type)
    if command.payment_type:
        count_query = count_query.filter(Vacancies.payment_type == command.payment_type)
    total = count_query.count()

    # Get paginated results dengan eager loading
    vacancies = query.order_by(Vacancies.created_at.desc()).offset(offset).limit(per_page).all()

    # Build response - skills sudah di-load via eager loading
    items = []
    for vacancy in vacancies:
        # Skills sudah eager-loaded, tidak perlu query tambahan
        skills = [
            SkillRequirement(
                skill_id=vs.skill_id,
                skill_name=vs.skill.name if vs.skill else "Unknown",
                is_mandatory=vs.is_mandatory if vs.is_mandatory else True,
            )
            for vs in vacancy.vacancy_skills
        ]

        company_info = CompanyInfo(
            id=vacancy.company.id,
            name=vacancy.company.name,
            industry=vacancy.company.industry,
            website_url=vacancy.company.website_url,
        )

        items.append(
            VacancyDetailResponse(
                id=vacancy.id,
                company=company_info,
                title=vacancy.title,
                description=vacancy.description,
                type=vacancy.type,
                open_date=vacancy.open_date,
                close_date=vacancy.close_date,
                location=vacancy.location,
                payment_type=vacancy.payment_type,
                compensation_min=vacancy.compensation_min,
                compensation_max=vacancy.compensation_max,
                compensation_note=vacancy.compensation_note,
                source_url=vacancy.source_url,
                is_scraped=vacancy.is_scraped if vacancy.is_scraped else False,
                is_auto_close=vacancy.is_auto_close if vacancy.is_auto_close else True,
                is_active=vacancy.is_active if vacancy.is_active else True,
                skills=skills,
                created_at=vacancy.created_at,
                updated_at=vacancy.updated_at,
            )
        )

    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    return SearchVacanciesResult(
        data=VacancyListResponse(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )
    )
