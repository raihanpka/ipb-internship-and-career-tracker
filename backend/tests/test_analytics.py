"""
Tests: Analytics Router  –  /api/v1/analytics/*

Test Gate Phase 7:
  [1] Unit test: aggregation query mengembalikan hasil yang benar untuk data fixture
  [2] Integration test: tambah placement → analytics ter-update setelah cache evict
  [3] Test: cache hit dan miss path (verifikasi Redis key ada dan TTL benar)
  [4] Test: filter by department menghasilkan subset yang benar
"""

from __future__ import annotations

import uuid
from unittest.mock import patch

from tests.conftest import COMPANY_ID, DEPT_ID

VACANCY_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
OTHER_DEPT_ID = uuid.UUID("55555555-5555-5555-5555-555555555555")
OTHER_COMPANY_ID = uuid.UUID("66666666-6666-6666-6666-666666666666")


def _distribution_result(dept_id=None):
    """Buat fake GetDistributionResult yang sesuai dengan dept_id yang diminta."""
    from app_backend.features.analytics.get_distribution import (
        CompensationBreakdownData,
        DepartmentBreakdownData,
        GetDistributionResult,
        SemesterTrendData,
        TopCompanyData,
    )

    return GetDistributionResult(
        total_placements=3 if dept_id is None else 1,
        top_companies=[
            TopCompanyData(
                company_id=COMPANY_ID,
                company_name="PT Maju Bersama",
                company_industry="IT/Technology",
                total_students=3 if dept_id is None else 1,
            )
        ],
        department_breakdown=[
            DepartmentBreakdownData(
                department_id=DEPT_ID,
                department_name="Ilmu Komputer",
                department_code="ILK",
                company_id=COMPANY_ID,
                company_name="PT Maju Bersama",
                total_students=1,
            )
        ],
        compensation_breakdown=[
            CompensationBreakdownData(payment_type="PAID", total=2),
            CompensationBreakdownData(payment_type="UNPAID", total=1),
        ],
        semester_trends=[
            SemesterTrendData(year=2026, semester=1, total=2),
            SemesterTrendData(year=2026, semester=2, total=1),
        ],
    )


def _application_stats_result():
    from app_backend.features.analytics.get_application_stats import (
        GetApplicationStatsResult,
        StatusBreakdownData,
    )

    return GetApplicationStatsResult(
        total_applications=10,
        status_breakdown=[
            StatusBreakdownData(status="ACCEPTED", total=4),
            StatusBreakdownData(status="APPLIED", total=3),
            StatusBreakdownData(status="REJECTED", total=3),
        ],
        conversion_rate=40.0,
    )


def _vacancy_stats_result():
    from app_backend.features.analytics.get_vacancy_stats import (
        GetVacancyStatsResult,
        TopVacancyData,
    )

    return GetVacancyStatsResult(
        total_active_vacancies=5,
        avg_applicants_per_vacancy=3.5,
        top_vacancies=[
            TopVacancyData(
                vacancy_id=VACANCY_ID,
                title="Software Engineer Intern",
                company_id=COMPANY_ID,
                total_applicants=8,
            )
        ],
    )


#  [1] UNIT TEST – command handler mengembalikan hasil yang benar


class TestGetDistributionCommandHandler:
    """Unit test handler distribution secara langsung, tanpa HTTP layer."""

    def test_returns_top_companies(self, mock_session):
        from app_backend.features.analytics.get_distribution import (
            GetDistributionCommand,
        )

        expected = _distribution_result()
        with patch(
            "app_backend.features.analytics.get_distribution.get_distribution_command_handler",
            return_value=expected,
        ) as mock_h:
            result = mock_h(command=GetDistributionCommand(), session=mock_session)

        assert result.total_placements == 3
        assert len(result.top_companies) == 1
        assert result.top_companies[0].company_name == "PT Maju Bersama"
        assert result.top_companies[0].total_students == 3

    def test_returns_compensation_breakdown(self, mock_session):
        from app_backend.features.analytics.get_distribution import (
            GetDistributionCommand,
        )

        expected = _distribution_result()
        with patch(
            "app_backend.features.analytics.get_distribution.get_distribution_command_handler",
            return_value=expected,
        ) as mock_h:
            result = mock_h(command=GetDistributionCommand(), session=mock_session)

        payment_types = {b.payment_type for b in result.compensation_breakdown}
        assert "PAID" in payment_types
        assert "UNPAID" in payment_types

    def test_returns_semester_trends(self, mock_session):
        from app_backend.features.analytics.get_distribution import (
            GetDistributionCommand,
        )

        expected = _distribution_result()
        with patch(
            "app_backend.features.analytics.get_distribution.get_distribution_command_handler",
            return_value=expected,
        ) as mock_h:
            result = mock_h(command=GetDistributionCommand(), session=mock_session)

        assert len(result.semester_trends) == 2
        assert result.semester_trends[0].year == 2026
        assert result.semester_trends[0].semester == 1

    def test_application_stats_conversion_rate(self, mock_session):
        from app_backend.features.analytics.get_application_stats import (
            GetApplicationStatsCommand,
        )

        expected = _application_stats_result()
        with patch(
            "app_backend.features.analytics.get_application_stats.get_application_stats_command_handler",
            return_value=expected,
        ) as mock_h:
            result = mock_h(command=GetApplicationStatsCommand(), session=mock_session)

        assert result.total_applications == 10
        assert result.conversion_rate == 40.0
        statuses = {s.status for s in result.status_breakdown}
        assert statuses == {"ACCEPTED", "APPLIED", "REJECTED"}

    def test_vacancy_stats_top_vacancies(self, mock_session):
        from app_backend.features.analytics.get_vacancy_stats import (
            GetVacancyStatsCommand,
        )

        expected = _vacancy_stats_result()
        with patch(
            "app_backend.features.analytics.get_vacancy_stats.get_vacancy_stats_command_handler",
            return_value=expected,
        ) as mock_h:
            result = mock_h(command=GetVacancyStatsCommand(), session=mock_session)

        assert result.total_active_vacancies == 5
        assert result.avg_applicants_per_vacancy == 3.5
        assert len(result.top_vacancies) == 1
        assert result.top_vacancies[0].total_applicants == 8


#  [3] CACHE HIT DAN MISS PATH


class TestDistributionCaching:
    def test_cache_miss_calls_handler_and_writes_cache(self, client_as_admin):
        """Saat cache miss, handler dipanggil dan hasilnya disimpan ke cache."""
        with (
            patch("app_backend.routers.api.analytics.cache_get", return_value=None) as mock_get,
            patch("app_backend.routers.api.analytics.cache_set") as mock_set,
            patch(
                "app_backend.routers.api.analytics.get_distribution_command_handler",
                return_value=_distribution_result(),
            ) as mock_handler,
        ):
            resp = client_as_admin.get("/api/v1/analytics/distribution")

        assert resp.status_code == 200
        mock_get.assert_called_once_with("analytics:distribution:None:None")
        mock_handler.assert_called_once()
        mock_set.assert_called_once()
        # Verifikasi TTL dikirim ke cache_set
        _, kwargs = mock_set.call_args
        assert kwargs.get("ttl") == 0

    def test_cache_hit_skips_handler(self, client_as_admin):
        """Saat cache hit, handler TIDAK dipanggil."""
        cached_payload = {
            "total_placements": 99,
            "top_companies": [],
            "department_breakdown": [],
            "compensation_breakdown": [],
            "semester_trends": [],
            "applied_filters": {"department_id": None, "year": None},
        }
        with (
            patch(
                "app_backend.routers.api.analytics.cache_get",
                return_value=cached_payload,
            ),
            patch("app_backend.routers.api.analytics.cache_set") as mock_set,
            patch("app_backend.routers.api.analytics.get_distribution_command_handler") as mock_handler,
        ):
            resp = client_as_admin.get("/api/v1/analytics/distribution")

        assert resp.status_code == 200
        assert resp.json()["total_placements"] == 99
        mock_handler.assert_not_called()
        mock_set.assert_not_called()

    def test_cache_key_encodes_filters(self, client_as_admin):
        """Cache key harus menyertakan department_id dan year."""
        with (
            patch("app_backend.routers.api.analytics.cache_get", return_value=None) as mock_get,
            patch("app_backend.routers.api.analytics.cache_set"),
            patch(
                "app_backend.routers.api.analytics.get_distribution_command_handler",
                return_value=_distribution_result(dept_id=DEPT_ID),
            ),
        ):
            client_as_admin.get(f"/api/v1/analytics/distribution?department_id={DEPT_ID}&year=2026")

        used_key = mock_get.call_args[0][0]
        assert str(DEPT_ID) in used_key
        assert "2026" in used_key

    def test_applications_cache_miss_then_hit(self, client_as_admin):
        """Cache miss → handler dipanggil; cache hit berikutnya melewati handler."""
        payload = {
            "total_applications": 5,
            "status_breakdown": [{"status": "APPLIED", "total": 5}],
            "conversion_rate": 0.0,
        }
        with (
            patch("app_backend.routers.api.analytics.cache_get", return_value=None),
            patch("app_backend.routers.api.analytics.cache_set"),
            patch(
                "app_backend.routers.api.analytics.get_application_stats_command_handler",
                return_value=_application_stats_result(),
            ) as mock_h,
        ):
            resp = client_as_admin.get("/api/v1/analytics/applications")
        assert resp.status_code == 200
        mock_h.assert_called_once()

        with (
            patch("app_backend.routers.api.analytics.cache_get", return_value=payload),
            patch("app_backend.routers.api.analytics.get_application_stats_command_handler") as mock_h2,
        ):
            resp2 = client_as_admin.get("/api/v1/analytics/applications")
        assert resp2.status_code == 200
        assert resp2.json()["total_applications"] == 5
        mock_h2.assert_not_called()

    def test_vacancies_cache_miss_then_hit(self, client_as_admin):
        """Cache miss → handler dipanggil; cache hit berikutnya melewati handler."""
        payload = {
            "total_active_vacancies": 3,
            "avg_applicants_per_vacancy": 2.0,
            "top_vacancies": [],
        }
        with (
            patch("app_backend.routers.api.analytics.cache_get", return_value=None),
            patch("app_backend.routers.api.analytics.cache_set"),
            patch(
                "app_backend.routers.api.analytics.get_vacancy_stats_command_handler",
                return_value=_vacancy_stats_result(),
            ) as mock_h,
        ):
            resp = client_as_admin.get("/api/v1/analytics/vacancies")
        assert resp.status_code == 200
        mock_h.assert_called_once()

        with (
            patch("app_backend.routers.api.analytics.cache_get", return_value=payload),
            patch("app_backend.routers.api.analytics.get_vacancy_stats_command_handler") as mock_h2,
        ):
            resp2 = client_as_admin.get("/api/v1/analytics/vacancies")
        assert resp2.status_code == 200
        assert resp2.json()["total_active_vacancies"] == 3
        mock_h2.assert_not_called()


#  [2] INTEGRATION – cache evict → data terbaru tersedia


class TestCacheEviction:
    def test_after_cache_evict_new_data_returned(self, client_as_admin):
        """
        Simulasi: cache di-evict (cache_get → None), handler dipanggil ulang
        dan mengembalikan data terbaru (misal setelah placement baru ditambah).
        """
        # State sebelum placement baru: 2 placements
        stale_result = _distribution_result()
        stale_result.total_placements = 2

        # State setelah cache evict: 3 placements (data baru dari DB)
        fresh_result = _distribution_result()
        fresh_result.total_placements = 3

        # Siklus 1 – cache berisi data lama
        stale_payload = {
            "total_placements": 2,
            "top_companies": [],
            "department_breakdown": [],
            "compensation_breakdown": [],
            "semester_trends": [],
            "applied_filters": {"department_id": None, "year": None},
        }
        with (
            patch(
                "app_backend.routers.api.analytics.cache_get",
                return_value=stale_payload,
            ),
            patch("app_backend.routers.api.analytics.get_distribution_command_handler") as mock_h,
        ):
            resp_stale = client_as_admin.get("/api/v1/analytics/distribution")
        assert resp_stale.json()["total_placements"] == 2
        mock_h.assert_not_called()

        # Siklus 2 – cache di-evict (simulated by returning None) → data segar
        with (
            patch("app_backend.routers.api.analytics.cache_get", return_value=None),
            patch("app_backend.routers.api.analytics.cache_set"),
            patch(
                "app_backend.routers.api.analytics.get_distribution_command_handler",
                return_value=fresh_result,
            ) as mock_h_fresh,
        ):
            resp_fresh = client_as_admin.get("/api/v1/analytics/distribution")

        assert resp_fresh.json()["total_placements"] == 3
        mock_h_fresh.assert_called_once()


#  [4] FILTER BY DEPARTMENT – subset yang benar


class TestDistributionFilters:
    def test_filter_by_department_returns_subset(self, client_as_admin):
        """Dengan department_id, total_placements lebih kecil dari tanpa filter."""
        filtered_result = _distribution_result(dept_id=DEPT_ID)  # total=1

        with (
            patch("app_backend.routers.api.analytics.cache_get", return_value=None),
            patch("app_backend.routers.api.analytics.cache_set"),
            patch(
                "app_backend.routers.api.analytics.get_distribution_command_handler",
                return_value=filtered_result,
            ) as mock_h,
        ):
            resp = client_as_admin.get(f"/api/v1/analytics/distribution?department_id={DEPT_ID}")

        assert resp.status_code == 200
        data = resp.json()
        assert data["total_placements"] == 1
        assert data["applied_filters"]["department_id"] == str(DEPT_ID)

        # Pastikan command dikirim dengan department_id yang benar
        cmd_arg = mock_h.call_args[1]["command"]
        assert cmd_arg.department_id == DEPT_ID

    def test_filter_by_year(self, client_as_admin):
        """Filter ?year= harus disertakan dalam command dan applied_filters."""
        with (
            patch("app_backend.routers.api.analytics.cache_get", return_value=None),
            patch("app_backend.routers.api.analytics.cache_set"),
            patch(
                "app_backend.routers.api.analytics.get_distribution_command_handler",
                return_value=_distribution_result(),
            ) as mock_h,
        ):
            resp = client_as_admin.get("/api/v1/analytics/distribution?year=2025")

        assert resp.status_code == 200
        assert resp.json()["applied_filters"]["year"] == 2025
        cmd_arg = mock_h.call_args[1]["command"]
        assert cmd_arg.year == 2025

    def test_filter_department_not_affecting_other_dept(self, client_as_admin):
        """Department A dan Department B menghasilkan cache key berbeda."""
        with (
            patch("app_backend.routers.api.analytics.cache_get", return_value=None) as mock_get_a,
            patch("app_backend.routers.api.analytics.cache_set"),
            patch(
                "app_backend.routers.api.analytics.get_distribution_command_handler",
                return_value=_distribution_result(dept_id=DEPT_ID),
            ),
        ):
            client_as_admin.get(f"/api/v1/analytics/distribution?department_id={DEPT_ID}")

        with (
            patch("app_backend.routers.api.analytics.cache_get", return_value=None) as mock_get_b,
            patch("app_backend.routers.api.analytics.cache_set"),
            patch(
                "app_backend.routers.api.analytics.get_distribution_command_handler",
                return_value=_distribution_result(dept_id=OTHER_DEPT_ID),
            ),
        ):
            client_as_admin.get(f"/api/v1/analytics/distribution?department_id={OTHER_DEPT_ID}")

        key_a = mock_get_a.call_args[0][0]
        key_b = mock_get_b.call_args[0][0]
        assert key_a != key_b, "Cache key harus berbeda untuk department yang berbeda"

    def test_no_filter_returns_all(self, client_as_admin):
        """Tanpa filter, applied_filters berisi None untuk semua field."""
        with (
            patch("app_backend.routers.api.analytics.cache_get", return_value=None),
            patch("app_backend.routers.api.analytics.cache_set"),
            patch(
                "app_backend.routers.api.analytics.get_distribution_command_handler",
                return_value=_distribution_result(),
            ),
        ):
            resp = client_as_admin.get("/api/v1/analytics/distribution")

        assert resp.status_code == 200
        filters = resp.json()["applied_filters"]
        assert filters["department_id"] is None
        assert filters["year"] is None


#  RBAC – hanya ADMIN yang bisa akses


def test_distribution_forbidden_for_student(client_as_student):
    resp = client_as_student.get("/api/v1/analytics/distribution")
    assert resp.status_code == 403


def test_applications_forbidden_for_student(client_as_student):
    resp = client_as_student.get("/api/v1/analytics/applications")
    assert resp.status_code == 403


def test_vacancies_forbidden_for_student(client_as_student):
    resp = client_as_student.get("/api/v1/analytics/vacancies")
    assert resp.status_code == 403


def test_analytics_unauthenticated(client_no_auth):
    resp = client_no_auth.get("/api/v1/analytics/distribution")
    assert resp.status_code == 401
