"""
Tests — Test Gate Phase 6

1. Integration test: trigger generate report → PDF tersedia di URL
2. Test: generate report dengan placement yang belum berakhir harus return 400
3. Test: generate report tanpa log sama sekali harus return 400
4. Test: surat generator menghasilkan PDF dengan kop dan data mahasiswa yang benar
5. Test: auto_generated_report_url ter-update setelah task selesai
"""

from __future__ import annotations

import datetime
import os
import uuid
from unittest.mock import MagicMock, call, patch

import pytest

from tests.conftest import COMPANY_ID, STUDENT_USER_ID

PLACEMENT_ID = uuid.UUID("55555555-5555-5555-5555-555555555555")
REQUEST_ID   = uuid.UUID("66666666-6666-6666-6666-666666666666")

_GENERATE_HANDLER = "app_backend.routers.api.placement.generate_report_command_handler"
_GET_HANDLER      = "app_backend.routers.api.placement.get_report_command_handler"


# ══════════════════════════════════════════════════════════════════════════════
# 1. Integration: trigger generate report → PDF tersedia di URL
# ══════════════════════════════════════════════════════════════════════════════


def test_generate_report_trigger_returns_202_with_task_id(client_as_student):
    """POST /report/generate returns 202 Accepted with a Celery task_id."""
    with patch(_GENERATE_HANDLER) as mock:
        mock.return_value = MagicMock(
            got_error=lambda: False,
            error_code=400,
            task_id="celery-task-abc123",
            message="Pembuatan laporan sedang diproses.",
        )
        resp = client_as_student.post(
            f"/api/v1/placements/{PLACEMENT_ID}/report/generate"
        )

    assert resp.status_code == 202
    data = resp.json()
    assert data["task_id"] == "celery-task-abc123"
    assert "message" in data


def test_get_report_returns_url_when_ready(client_as_student):
    """GET /report returns status='generated' and a non-empty URL once complete."""
    expected_url = f"/uploads/reports/report_{PLACEMENT_ID}.pdf"
    with patch(_GET_HANDLER) as mock:
        mock.return_value = MagicMock(
            got_error=lambda: False,
            error_code=404,
            status="generated",
            report_url=expected_url,
            last_generated_at="2026-02-24T12:00:00",
        )
        resp = client_as_student.get(f"/api/v1/placements/{PLACEMENT_ID}/report")

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "generated"
    assert data["report_url"] == expected_url


def test_get_report_returns_not_generated_while_pending(client_as_student):
    """GET /report returns status='not_generated' before task completes."""
    with patch(_GET_HANDLER) as mock:
        mock.return_value = MagicMock(
            got_error=lambda: False,
            error_code=404,
            status="not_generated",
            report_url=None,
            last_generated_at=None,
        )
        resp = client_as_student.get(f"/api/v1/placements/{PLACEMENT_ID}/report")

    assert resp.status_code == 200
    assert resp.json()["status"] == "not_generated"
    assert resp.json()["report_url"] is None


# ══════════════════════════════════════════════════════════════════════════════
# 2. generate report dengan placement yang belum berakhir harus return 400
# ══════════════════════════════════════════════════════════════════════════════


def test_generate_report_placement_not_ended_returns_400_via_endpoint(client_as_student):
    """Endpoint propagates handler's 400 when placement has not ended."""
    with patch(_GENERATE_HANDLER) as mock:
        mock.return_value = MagicMock(
            got_error=lambda: True,
            error_code=400,
            error_message="Laporan hanya bisa digenerate setelah masa penempatan selesai",
        )
        resp = client_as_student.post(
            f"/api/v1/placements/{PLACEMENT_ID}/report/generate"
        )

    assert resp.status_code == 400
    assert "selesai" in resp.json()["detail"]


def test_generate_report_handler_rejects_future_placement(mock_session):
    """Handler returns 400 when placement.end_date is in the future."""
    from app_backend.features.placement.generate_report import (
        GenerateReportCommand,
        generate_report_command_handler,
    )

    mock_placement = MagicMock()
    mock_placement.id = PLACEMENT_ID
    mock_placement.student_id = STUDENT_USER_ID
    mock_placement.end_date = datetime.date(2099, 12, 31)  # far future

    mock_session.query.return_value.filter_by.return_value.first.return_value = (
        mock_placement
    )

    result = generate_report_command_handler(
        command=GenerateReportCommand(
            placement_id=PLACEMENT_ID,
            student_id=STUDENT_USER_ID,
        ),
        session=mock_session,
    )

    assert result.got_error()
    assert result.error_code == 400
    assert "selesai" in result.error_message


# ══════════════════════════════════════════════════════════════════════════════
# 3. generate report tanpa log sama sekali harus return 400
# ══════════════════════════════════════════════════════════════════════════════


def test_generate_report_no_logs_returns_400_via_endpoint(client_as_student):
    """Endpoint propagates handler's 400 when placement has no activity logs."""
    with patch(_GENERATE_HANDLER) as mock:
        mock.return_value = MagicMock(
            got_error=lambda: True,
            error_code=400,
            error_message="Tidak ada log aktivitas. Tambahkan log terlebih dahulu sebelum generate laporan.",
        )
        resp = client_as_student.post(
            f"/api/v1/placements/{PLACEMENT_ID}/report/generate"
        )

    assert resp.status_code == 400
    assert "log" in resp.json()["detail"].lower()


def test_generate_report_handler_rejects_empty_logs(mock_session):
    """Handler returns 400 when placement is ended but has zero activity logs."""
    from app_backend.features.placement.generate_report import (
        GenerateReportCommand,
        generate_report_command_handler,
    )

    mock_placement = MagicMock()
    mock_placement.id = PLACEMENT_ID
    mock_placement.student_id = STUDENT_USER_ID
    mock_placement.end_date = datetime.date(2026, 1, 1)  # already ended

    # First query(Placements).filter_by().first() → placement
    # Second query(ActivityLogs).filter_by().count() → 0
    query_mock = MagicMock()
    query_mock.filter_by.return_value.first.return_value = mock_placement
    query_mock.filter_by.return_value.count.return_value = 0
    mock_session.query.return_value = query_mock

    result = generate_report_command_handler(
        command=GenerateReportCommand(
            placement_id=PLACEMENT_ID,
            student_id=STUDENT_USER_ID,
        ),
        session=mock_session,
    )

    assert result.got_error()
    assert result.error_code == 400
    assert "log" in result.error_message.lower()


# ══════════════════════════════════════════════════════════════════════════════
# 4. Surat generator menghasilkan PDF dengan kop dan data mahasiswa yang benar
# ══════════════════════════════════════════════════════════════════════════════


def test_cover_letter_pdf_is_valid_and_contains_student_data(tmp_path):
    """_build_cover_letter_pdf creates a valid PDF with IPB kop and student data.

    ReportLab compresses content streams (ASCII85 + FlateDecode), so raw bytes
    cannot be grepped.  We spy on both Paragraph() and Table() to capture every
    string written into the story before the PDF is built.
    """
    import app_backend.shared.tasks.document_tasks as doc_tasks

    OriginalParagraph = doc_tasks.Paragraph
    OriginalTable = doc_tasks.Table

    para_texts: list[str] = []
    table_texts: list[str] = []

    def spy_paragraph(text, style, *args, **kwargs):
        para_texts.append(str(text))
        return OriginalParagraph(text, style, *args, **kwargs)

    def spy_table(data, *args, **kwargs):
        for row in data:
            for cell in row:
                if isinstance(cell, str):
                    table_texts.append(cell)
        return OriginalTable(data, *args, **kwargs)

    output = str(tmp_path / "cover_letter_test.pdf")

    with patch("app_backend.shared.tasks.document_tasks.Paragraph", side_effect=spy_paragraph), \
         patch("app_backend.shared.tasks.document_tasks.Table", side_effect=spy_table):
        doc_tasks._build_cover_letter_pdf(
            student_full_name="Budi Santoso",
            nim="G1234567890",
            department_name="Ilmu Komputer",
            semester=5,
            purpose="melamar magang sebagai software engineer",
            vacancy_title="Software Engineer Intern",
            company_name="Tokopedia",
            request_id=str(REQUEST_ID),
            output_path=output,
        )

    # File was created and is a valid PDF
    assert os.path.exists(output), "File PDF tidak dibuat"
    assert os.path.getsize(output) > 1_000, "PDF terlalu kecil"
    with open(output, "rb") as f:
        assert f.read(4) == b"%PDF", "File bukan PDF yang valid"

    # Verify kop surat dan data mahasiswa muncul dalam story (Paragraph + Table cells)
    all_text = " ".join(para_texts + table_texts)
    assert "INSTITUT PERTANIAN BOGOR" in all_text, \
        "Kop surat IPB tidak ditemukan dalam story PDF"
    assert "Budi Santoso" in all_text, \
        "Nama mahasiswa tidak ditemukan dalam story PDF"
    assert "G1234567890" in all_text, \
        "NIM mahasiswa tidak ditemukan dalam story PDF"
    assert "Tokopedia" in all_text, \
        "Nama perusahaan tidak ditemukan dalam story PDF"


def test_cover_letter_pdf_without_vacancy(tmp_path):
    """_build_cover_letter_pdf works when vacancy_title and company_name are None."""
    from app_backend.shared.tasks.document_tasks import _build_cover_letter_pdf

    output = str(tmp_path / "cover_letter_no_vacancy.pdf")

    _build_cover_letter_pdf(
        student_full_name="Ani Rahayu",
        nim="H9876543210",
        department_name="Manajemen",
        semester=6,
        purpose="keperluan magang umum",
        vacancy_title=None,
        company_name=None,
        request_id=str(uuid.uuid4()),
        output_path=output,
    )

    assert os.path.exists(output)
    with open(output, "rb") as f:
        raw = f.read()
    assert raw[:4] == b"%PDF"


# ══════════════════════════════════════════════════════════════════════════════
# 5. auto_generated_report_url ter-update setelah task selesai
# ══════════════════════════════════════════════════════════════════════════════


def test_report_task_updates_placement_url_after_success():
    """generate_final_report sets placement.auto_generated_report_url after PDF is built."""
    from app_backend.shared.tasks.report_tasks import generate_final_report

    mock_placement = MagicMock()
    mock_placement.id = PLACEMENT_ID
    mock_placement.student_id = STUDENT_USER_ID
    mock_placement.company_id = COMPANY_ID
    mock_placement.start_date = datetime.date(2026, 1, 1)
    mock_placement.end_date = datetime.date(2026, 6, 30)
    mock_placement.status = "COMPLETED"
    mock_placement.external_supervisor_name = "Dr. Supervisor"
    mock_placement.auto_generated_report_url = None

    mock_session = MagicMock()

    def _query_side_effect(model):
        q = MagicMock()
        from app_backend.models.placements import Placements
        from app_backend.models.activity_logs import ActivityLogs
        if model is Placements:
            q.filter_by.return_value.first.return_value = mock_placement
        else:  # ActivityLogs
            q.filter_by.return_value.order_by.return_value.all.return_value = []
        return q

    mock_session.query.side_effect = _query_side_effect

    with patch("app_backend.shared.tasks.report_tasks.SessionLocal", return_value=mock_session):
        with patch("app_backend.shared.tasks.report_tasks._build_pdf") as mock_build:
            mock_build.return_value = None
            with patch("os.makedirs"):
                generate_final_report.apply(args=[str(PLACEMENT_ID)])

    # URL must have been set on the placement object
    assert mock_placement.auto_generated_report_url is not None
    assert "/uploads/reports/" in mock_placement.auto_generated_report_url
    assert str(PLACEMENT_ID) in mock_placement.auto_generated_report_url

    # Must have committed the session
    mock_session.commit.assert_called()


def test_report_task_marks_failed_when_placement_not_found():
    """generate_final_report returns failure dict when placement is missing."""
    from app_backend.shared.tasks.report_tasks import generate_final_report

    mock_session = MagicMock()
    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    with patch("app_backend.shared.tasks.report_tasks.SessionLocal", return_value=mock_session):
        result = generate_final_report.apply(args=[str(PLACEMENT_ID)]).get()

    assert result["success"] is False
    assert "ditemukan" in result["error"]
