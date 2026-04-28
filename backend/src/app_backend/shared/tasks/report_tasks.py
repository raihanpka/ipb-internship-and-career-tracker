"""
Report Tasks – Background tasks untuk generate laporan akhir magang.
Menggunakan Pandas untuk agregasi dan ReportLab untuk render PDF.
"""

import os
import uuid
from datetime import date, datetime
from typing import Dict, Optional

import pandas as pd
from celery import shared_task
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)

from app_backend.shared.database import SessionLocal

UPLOAD_DIR = "uploads/reports"


def _build_pdf(placement, logs_df: pd.DataFrame, output_path: str) -> None:
    """Render PDF laporan akhir magang dengan format PPKI IPB."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=3 * cm,
        rightMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", parent=styles["Heading1"],
        fontSize=14, alignment=1, spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"],
        fontSize=11, alignment=1, spaceAfter=2,
    )
    header_style = ParagraphStyle(
        "SectionHeader", parent=styles["Heading2"],
        fontSize=11, spaceBefore=12, spaceAfter=6,
    )
    normal = styles["Normal"]
    normal.fontSize = 10

    story = []

    # ── Kop surat ──────────────────────────────────────────────────────────────
    story.append(Paragraph("INSTITUT PERTANIAN BOGOR", title_style))
    story.append(Paragraph("DIREKTORAT KEMAHASISWAAN DAN PENGEMBANGAN KARIR", subtitle_style))
    story.append(Paragraph("Jl. Raya Darmaga, Bogor 16680, Jawa Barat", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.darkgreen, spaceAfter=10))

    # ── Judul laporan ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("LAPORAN AKHIR MAGANG", title_style))
    story.append(Paragraph("(Dokumen Otomatis – Sistem IPB Career Tracker)", subtitle_style))
    story.append(Spacer(1, 0.5 * cm))

    # ── Informasi penempatan ───────────────────────────────────────────────────
    story.append(Paragraph("I. INFORMASI PENEMPATAN", header_style))
    info_data = [
        ["ID Penempatan", str(placement.id)],
        ["Perusahaan", str(placement.company_id)],
        ["Tanggal Mulai", placement.start_date.strftime("%d %B %Y")],
        ["Tanggal Selesai", placement.end_date.strftime("%d %B %Y")],
        ["Status", placement.status or "-"],
        ["Supervisor Eksternal", placement.external_supervisor_name or "-"],
    ]
    info_table = Table(info_data, colWidths=[5 * cm, 11 * cm])
    info_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
        ("ROWBACKGROUNDS", (1, 0), (1, -1), [colors.white, colors.HexColor("#f7f7f7")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(info_table)

    if logs_df.empty:
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph("Tidak ada log aktivitas yang ditemukan untuk penempatan ini.", normal))
    else:
        # ── Ringkasan keseluruhan ──────────────────────────────────────────────
        story.append(Paragraph("II. RINGKASAN KESELURUHAN", header_style))
        total_hours = float(logs_df["duration_hours"].sum())
        total_days = logs_df["activity_date"].nunique()
        total_entries = len(logs_df)
        duration_days = (placement.end_date - placement.start_date).days + 1

        summary_data = [
            ["Total Entri Log", str(total_entries)],
            ["Total Hari Aktif", str(total_days)],
            ["Total Jam Kerja", f"{total_hours:.2f} jam"],
            ["Rata-rata Jam/Hari", f"{(total_hours / total_days):.2f} jam" if total_days else "-"],
            ["Durasi Penempatan", f"{duration_days} hari"],
        ]
        summary_table = Table(summary_data, colWidths=[6 * cm, 10 * cm])
        summary_table.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(summary_table)

        # ── Ringkasan per minggu ───────────────────────────────────────────────
        story.append(Paragraph("III. RINGKASAN PER MINGGU", header_style))

        logs_df["week"] = logs_df["activity_date"].dt.isocalendar().week
        logs_df["year"] = logs_df["activity_date"].dt.isocalendar().year
        logs_df["week_label"] = logs_df["activity_date"].apply(
            lambda d: f"Minggu {d.isocalendar().week} ({d.strftime('%d %b %Y')})"
        )

        weekly = (
            logs_df.groupby(["year", "week"])
            .agg(
                label=("week_label", "first"),
                total_hours=("duration_hours", "sum"),
                total_days=("activity_date", "nunique"),
                total_entries=("id", "count"),
            )
            .reset_index()
            .sort_values(["year", "week"])
        )

        week_header = [["Minggu", "Hari Aktif", "Entri Log", "Total Jam"]]
        week_rows = [
            [row["label"], str(int(row["total_days"])), str(int(row["total_entries"])), f"{float(row['total_hours']):.2f}"]
            for _, row in weekly.iterrows()
        ]
        week_data = week_header + week_rows
        week_table = Table(week_data, colWidths=[7 * cm, 3 * cm, 3 * cm, 3 * cm])
        week_table.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eaf4ea")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(week_table)

        # ── Log aktivitas lengkap ──────────────────────────────────────────────
        story.append(Paragraph("IV. LOG AKTIVITAS LENGKAP", header_style))
        log_header = [["Tanggal", "Durasi (jam)", "Deskripsi Kegiatan"]]
        log_rows = [
            [
                row["activity_date"].strftime("%d/%m/%Y"),
                f"{float(row['duration_hours']):.2f}",
                Paragraph(str(row["description_raw"]), ParagraphStyle("cell", fontSize=8, leading=11)),
            ]
            for _, row in logs_df.sort_values("activity_date").iterrows()
        ]
        log_data = log_header + log_rows
        log_table = Table(log_data, colWidths=[2.8 * cm, 2.8 * cm, 10.4 * cm])
        log_table.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eaf4ea")]),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("ALIGN", (0, 0), (1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(KeepTogether(log_table) if len(log_rows) <= 10 else log_table)

    # ── Blok tanda tangan ──────────────────────────────────────────────────────
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 0.4 * cm))

    generated_at = datetime.utcnow().strftime("%d %B %Y, %H:%M UTC")
    sig_data = [
        [f"Bogor, {generated_at}", ""],
        ["Koordinator Magang", "Mahasiswa"],
        ["", ""],
        ["", ""],
        ["(_________________________)", f"(ID: {placement.student_id})"],
    ]
    sig_table = Table(sig_data, colWidths=[8 * cm, 8 * cm])
    sig_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    story.append(sig_table)

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "* Laporan ini digenerate secara otomatis oleh Sistem IPB Career Tracker. "
        "Dokumen ini sah tanpa tanda tangan basah sesuai Peraturan Rektor IPB No. 12/2022.",
        ParagraphStyle("footer", fontSize=7, textColor=colors.grey, alignment=1),
    ))

    doc.build(story)


@shared_task(bind=True, max_retries=2, default_retry_delay=30, name="report_tasks.generate_final_report")
def generate_final_report(self, placement_id: str) -> Dict:
    """
    Task: Generate laporan akhir magang dalam format PDF.
    Fetch semua activity_logs, agregasi dengan Pandas, render ke PDF dengan ReportLab,
    lalu simpan URL ke placements.auto_generated_report_url.
    """
    from app_backend.models.placements import Placements
    from app_backend.models.activity_logs import ActivityLogs

    session = SessionLocal()
    try:
        placement = session.query(Placements).filter_by(id=uuid.UUID(placement_id)).first()
        if not placement:
            return {"success": False, "error": "Placement tidak ditemukan"}

        logs = (
            session.query(ActivityLogs)
            .filter_by(placement_id=placement.id)
            .order_by(ActivityLogs.activity_date.asc())
            .all()
        )

        if logs:
            logs_df = pd.DataFrame([
                {
                    "id": str(log.id),
                    "activity_date": pd.Timestamp(log.activity_date),
                    "duration_hours": float(log.duration_hours),
                    "description_raw": log.description_raw,
                }
                for log in logs
            ])
        else:
            logs_df = pd.DataFrame(columns=["id", "activity_date", "duration_hours", "description_raw"])

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = f"report_{placement_id}_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(UPLOAD_DIR, filename)

        _build_pdf(placement, logs_df, output_path)

        report_url = f"/uploads/reports/{filename}"
        placement.auto_generated_report_url = report_url
        placement.last_report_generated_at = datetime.utcnow()
        session.commit()

        return {"success": True, "report_url": report_url, "placement_id": placement_id}

    except Exception as exc:
        session.rollback()
        raise self.retry(exc=exc)
    finally:
        session.close()
