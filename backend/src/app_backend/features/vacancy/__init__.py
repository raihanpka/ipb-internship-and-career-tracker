"""
Vacancy Feature Package – Command Handlers untuk vacancy management.
"""

from dataclasses import dataclass
from typing import Optional

# Vacancy management commands
from app_backend.features.vacancy.create_vacancy import (
    CreateVacancyCommand,
    CreateVacancyResult,
    create_vacancy_command_handler,
)
from app_backend.features.vacancy.delete_vacancy import (
    DeleteVacancyCommand,
    DeleteVacancyResult,
    delete_vacancy_command_handler,
)
from app_backend.features.vacancy.get_vacancy import (
    GetVacancyCommand,
    GetVacancyResult,
    get_vacancy_command_handler,
)
from app_backend.features.vacancy.list_vacancies import (
    ListVacanciesCommand,
    ListVacanciesResult,
    list_vacancies_command_handler,
)
from app_backend.features.vacancy.search_vacancies import (
    SearchVacanciesCommand,
    SearchVacanciesResult,
    search_vacancies_command_handler,
)
from app_backend.features.vacancy.update_vacancy import (
    UpdateVacancyCommand,
    UpdateVacancyResult,
    update_vacancy_command_handler,
)
from app_backend.features.vacancy.job_matching import (
    JobMatchCommand,
    JobMatchResult,
    JobMatchListCommand,
    JobMatchListResult,
    job_match_command_handler,
    job_match_list_command_handler,
)

__all__ = [
    # Commands
    "CreateVacancyCommand",
    "UpdateVacancyCommand",
    "DeleteVacancyCommand",
    "GetVacancyCommand",
    "ListVacanciesCommand",
    "SearchVacanciesCommand",
    "JobMatchCommand",
    "JobMatchListCommand",
    # Results
    "CreateVacancyResult",
    "UpdateVacancyResult",
    "DeleteVacancyResult",
    "GetVacancyResult",
    "ListVacanciesResult",
    "SearchVacanciesResult",
    "JobMatchResult",
    "JobMatchListResult",
    # Handlers
    "create_vacancy_command_handler",
    "update_vacancy_command_handler",
    "delete_vacancy_command_handler",
    "get_vacancy_command_handler",
    "list_vacancies_command_handler",
    "search_vacancies_command_handler",
    "job_match_command_handler",
    "job_match_list_command_handler",
]
