"""
Job Matching Feature – Command Handler.
Menghitung persentase kecocokan profil mahasiswa dengan prasyarat lowongan.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload, selectinload

from app_backend.models.profiles_student import ProfilesStudent
from app_backend.models.student_skills import StudentSkills
from app_backend.models.vacancies import Vacancies
from app_backend.models.vacancy_skills import VacancySkills
from app_backend.schemas.vacancy import JobMatchResult


class JobMatchingException(Exception):
    pass


@dataclass
class JobMatchCommand:
    """Command untuk matching single vacancy dengan student."""
    student_id: uuid.UUID
    vacancy_id: uuid.UUID


@dataclass
class JobMatchResult:
    result: Optional[JobMatchResult] = None
    error_message: Optional[str] = None

    def got_error(self) -> bool:
        return self.error_message is not None


@dataclass
class JobMatchListCommand:
    """Command untuk matching semua vacancy aktif dengan student."""
    student_id: uuid.UUID
    page: int = 1
    per_page: int = 10
    min_match_percentage: float = 0.0  # Filter minimum match


@dataclass
class JobMatchListResult:
    items: List[JobMatchResult] = None
    total: int = 0
    page: int = 1
    per_page: int = 10
    total_pages: int = 1
    error_message: Optional[str] = None

    def got_error(self) -> bool:
        return self.error_message is not None


def _calculate_match(
    student_skill_ids: set[uuid.UUID],
    vacancy_skills: list[VacancySkills],
) -> dict:
    """
    Hitung kecocokan antara skill student dengan requirement vacancy.

    Algoritma:
    1. Mandatory skills wajib ada -> jika tidak ada, match_percentage berkurang signifikan
    2. Optional skills menambah nilai match
    3. Formula: (matched_mandatory * 2 + matched_optional) / (total_mandatory * 2 + total_optional) * 100
    """
    if not vacancy_skills:
        # Tidak ada skill requirement -> 100% match
        return {
            "match_percentage": 100.0,
            "matched_skills": [],
            "missing_mandatory_skills": [],
            "total_required_skills": 0,
            "total_matched_skills": 0,
        }

    mandatory_skills = []
    optional_skills = []
    matched_mandatory = []
    matched_optional = []
    missing_mandatory = []

    for vs in vacancy_skills:
        skill_name = vs.skill.name if vs.skill else "Unknown"

        if vs.is_mandatory:
            mandatory_skills.append((vs.skill_id, skill_name))
            if vs.skill_id in student_skill_ids:
                matched_mandatory.append(skill_name)
            else:
                missing_mandatory.append(skill_name)
        else:
            optional_skills.append((vs.skill_id, skill_name))
            if vs.skill_id in student_skill_ids:
                matched_optional.append(skill_name)

    # Calculate weighted score
    # Mandatory skills have 2x weight
    total_weight = len(mandatory_skills) * 2 + len(optional_skills)
    matched_weight = len(matched_mandatory) * 2 + len(matched_optional)

    if total_weight == 0:
        match_percentage = 100.0
    else:
        match_percentage = round((matched_weight / total_weight) * 100, 1)

    return {
        "match_percentage": match_percentage,
        "matched_skills": matched_mandatory + matched_optional,
        "missing_mandatory_skills": missing_mandatory,
        "total_required_skills": len(mandatory_skills) + len(optional_skills),
        "total_matched_skills": len(matched_mandatory) + len(matched_optional),
    }


def job_match_command_handler(
    command: JobMatchCommand,
    session: Session,
) -> JobMatchResult:
    """
    Hitung kecocokan single vacancy dengan profil student.
    """
    # Get student skills
    student = (
        session.query(ProfilesStudent)
        .options(selectinload(ProfilesStudent.student_skills))
        .filter(ProfilesStudent.user_id == command.student_id)
        .first()
    )
    if not student:
        return JobMatchResult(error_message="Profil mahasiswa tidak ditemukan")

    student_skill_ids = {ss.skill_id for ss in student.student_skills}

    # Get vacancy with skills
    vacancy = (
        session.query(Vacancies)
        .options(
            joinedload(Vacancies.company),
            selectinload(Vacancies.vacancy_skills).joinedload(VacancySkills.skill),
        )
        .filter(Vacancies.id == command.vacancy_id)
        .first()
    )
    if not vacancy:
        return JobMatchResult(error_message="Lowongan tidak ditemukan")

    if not vacancy.is_active:
        return JobMatchResult(error_message="Lowongan sudah tidak aktif")

    # Calculate match
    match_data = _calculate_match(student_skill_ids, vacancy.vacancy_skills)

    from app_backend.schemas.vacancy import JobMatchResult as JobMatchResultSchema

    return JobMatchResult(
        result=JobMatchResultSchema(
            vacancy_id=vacancy.id,
            vacancy_title=vacancy.title,
            company_name=vacancy.company.name,
            match_percentage=match_data["match_percentage"],
            matched_skills=match_data["matched_skills"],
            missing_mandatory_skills=match_data["missing_mandatory_skills"],
            total_required_skills=match_data["total_required_skills"],
            total_matched_skills=match_data["total_matched_skills"],
        )
    )


def job_match_list_command_handler(
    command: JobMatchListCommand,
    session: Session,
) -> JobMatchListResult:
    """
    Hitung kecocokan semua vacancy aktif dengan profil student.
    Diurutkan berdasarkan match_percentage tertinggi.
    """
    # Get student skills
    student = (
        session.query(ProfilesStudent)
        .options(selectinload(ProfilesStudent.student_skills))
        .filter(ProfilesStudent.user_id == command.student_id)
        .first()
    )
    if not student:
        return JobMatchListResult(error_message="Profil mahasiswa tidak ditemukan")

    student_skill_ids = {ss.skill_id for ss in student.student_skills}

    # Get all active vacancies with skills (eager loading)
    vacancies = (
        session.query(Vacancies)
        .options(
            joinedload(Vacancies.company),
            selectinload(Vacancies.vacancy_skills).joinedload(VacancySkills.skill),
        )
        .filter(Vacancies.is_active == True)
        .all()
    )

    # Calculate match for each vacancy
    from app_backend.schemas.vacancy import JobMatchResult as JobMatchResultSchema

    results = []
    for vacancy in vacancies:
        match_data = _calculate_match(student_skill_ids, vacancy.vacancy_skills)

        # Filter by minimum match percentage
        if match_data["match_percentage"] >= command.min_match_percentage:
            results.append(
                JobMatchResultSchema(
                    vacancy_id=vacancy.id,
                    vacancy_title=vacancy.title,
                    company_name=vacancy.company.name,
                    match_percentage=match_data["match_percentage"],
                    matched_skills=match_data["matched_skills"],
                    missing_mandatory_skills=match_data["missing_mandatory_skills"],
                    total_required_skills=match_data["total_required_skills"],
                    total_matched_skills=match_data["total_matched_skills"],
                )
            )

    # Sort by match_percentage descending
    results.sort(key=lambda x: x.match_percentage, reverse=True)

    # Pagination
    total = len(results)
    page = max(1, command.page)
    per_page = min(max(1, command.per_page), 100)
    offset = (page - 1) * per_page
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    paginated_results = results[offset : offset + per_page]

    return JobMatchListResult(
        items=paginated_results,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )
