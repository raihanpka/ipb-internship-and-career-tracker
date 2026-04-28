"""
Document Tasks – Background tasks untuk generate surat pengantar (cover letter) mahasiswa.
Menggunakan ReportLab untuk render PDF dengan kop surat resmi IPB.
"""

import os
import uuid
from datetime import datetime
from typing import Dict

from celery import shared_task
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app_backend.shared.database import SessionLocal

UPLOAD_DIR = "uploads/documents"


def _build_cover_letter_pdf(
    student_full_name: str,
    nim: str,
    department_name: str,
    semester: int,
    purpose: str,
    vacancy_title: str | None,
    company_name: str | None,
    request_id: str,
    output_path: str,
) -> None:
    """Render PDF surat pengantar resmi dengan kop IPB."""
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
        fontSize=14, alignment=1, spaceAfter=2,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"],
        fontSize=11, alignment=1, spaceAfter=2,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=11, leading=18, spaceAfter=8,
    )
    label_style = ParagraphStyle(
        "Label", parent=styles["Normal"],
        fontSize=11, fontName="Helvetica-Bold",
    )

    story = []

    # ── Kop surat ──────────────────────────────────────────────────────────────
    story.append(Paragraph("INSTITUT PERTANIAN BOGOR", title_style))
    story.append(Paragraph("DIREKTORAT KEMAHASISWAAN DAN PENGEMBANGAN KARIR", subtitle_style))
    story.append(Paragraph("Jl. Raya Darmaga, Bogor 16680, Jawa Barat", subtitle_style))
    story.append(Paragraph("Telp. (0251) 8622642 | email: dkpk@apps.ipb.ac.id", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.darkgreen, spaceAfter=10))

    # ── Nomor surat & tanggal ──────────────────────────────────────────────────
    story.append(Spacer(1, 0.3 * cm))
    generated_date = datetime.utcnow().strftime("%d %B %Y")
    ref_number = f"No. {uuid.uuid4().hex[:6].upper()}/IPB/DKPK/{datetime.utcnow().strftime('%m/%Y')}"

    meta_data = [
        ["Nomor", f": {ref_number}"],
        ["Hal", ": Surat Pengantar Mahasiswa"],
        ["Tanggal", f": {generated_date}"],
    ]
    meta_table = Table(meta_data, colWidths=[4 * cm, 12 * cm])
    meta_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Tujuan surat ───────────────────────────────────────────────────────────
    story.append(Paragraph("Kepada Yth.", body_style))
    if company_name:
        story.append(Paragraph(f"HRD / Pimpinan {company_name}", body_style))
    else:
        story.append(Paragraph("Pimpinan Perusahaan / Instansi", body_style))
    story.append(Paragraph("Di tempat", body_style))
    story.append(Spacer(1, 0.4 * cm))

    # ── Salam pembuka ──────────────────────────────────────────────────────────
    story.append(Paragraph("Dengan hormat,", body_style))

    # ── Isi surat ──────────────────────────────────────────────────────────────
    intro = (
        "Sehubungan dengan permohonan yang diajukan oleh mahasiswa kami, bersama ini kami "
        "sampaikan bahwa:"
    )
    story.append(Paragraph(intro, body_style))

    student_data = [
        ["Nama Lengkap", f": {student_full_name}"],
        ["NIM", f": {nim}"],
        ["Program Studi", f": {department_name}"],
        ["Semester", f": {semester}"],
    ]
    if vacancy_title:
        student_data.append(["Posisi Dilamar", f": {vacancy_title}"])

    student_table = Table(student_data, colWidths=[4 * cm, 12 * cm])
    student_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f2f8f2")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(student_table)
    story.append(Spacer(1, 0.4 * cm))

    purpose_text = (
        f"adalah benar mahasiswa aktif Institut Pertanian Bogor. "
        f"Mahasiswa tersebut bermaksud untuk {purpose}."
    )
    story.append(Paragraph(purpose_text, body_style))

    endorsement = (
        "Kami mendukung penuh niat dan tujuan mahasiswa tersebut dan berharap Bapak/Ibu "
        "dapat memberikan kesempatan kepada yang bersangkutan. Atas perhatian dan kerja "
        "sama Bapak/Ibu, kami ucapkan terima kasih."
    )
    story.append(Paragraph(endorsement, body_style))
    story.append(Spacer(1, 0.8 * cm))

    # ── Blok tanda tangan ──────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 0.3 * cm))

    sig_data = [
        [f"Bogor, {generated_date}", ""],
        ["Direktur Kemahasiswaan dan Pengembangan Karir", "Mahasiswa,"],
        ["Institut Pertanian Bogor", ""],
        ["", ""],
        ["", ""],
        ["(_________________________)", student_full_name],
        ["NIP. -", f"NIM. {nim}"],
    ]
    sig_table = Table(sig_data, colWidths=[9 * cm, 7 * cm])
    sig_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 5), (-1, 5), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (0, 2), "Helvetica-Bold"),
        ("FONTNAME", (1, 1), (1, 1), "Helvetica-Bold"),
    ]))
    story.append(sig_table)

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        f"* Surat ini digenerate otomatis oleh Sistem IPB Career Tracker. "
        f"ID Permohonan: {request_id}. "
        f"Dokumen ini sah tanpa tanda tangan basah sesuai Peraturan Rektor IPB No. 12/2022.",
        ParagraphStyle("footer", fontSize=7, textColor=colors.grey, alignment=1),
    ))

    doc.build(story)


@shared_task(bind=True, max_retries=2, default_retry_delay=30, name="document_tasks.generate_cover_letter")
def generate_cover_letter(self, request_id: str) -> Dict:
    """
    Task: Generate surat pengantar mahasiswa dalam format PDF.
    Fetch data mahasiswa dan tujuan permohonan, render ke PDF dengan kop IPB,
    lalu simpan URL ke document_requests.generated_url dan update status ke COMPLETED.
    """
    from app_backend.models.document_requests import DocumentRequests
    from app_backend.models.master_departments import MasterDepartments
    from app_backend.models.master_external_companies import MasterExternalCompanies
    from app_backend.models.profiles_student import ProfilesStudent
    from app_backend.models.vacancies import Vacancies

    session = SessionLocal()
    try:
        doc_request = session.query(DocumentRequests).filter_by(
            id=uuid.UUID(request_id)
        ).first()
        if not doc_request:
            return {"success": False, "error": "Document request tidak ditemukan"}

        doc_request.status = "PROCESSING"
        session.commit()

        student = session.query(ProfilesStudent).filter_by(
            user_id=doc_request.student_id
        ).first()
        if not student:
            doc_request.status = "FAILED"
            session.commit()
            return {"success": False, "error": "Data mahasiswa tidak ditemukan"}

        department_name = "Tidak Diketahui"
        if student.department_id:
            dept = session.query(MasterDepartments).filter_by(
                id=student.department_id
            ).first()
            if dept:
                department_name = dept.name

        vacancy_title = None
        company_name = None
        if doc_request.reference_vacancy_id:
            vacancy = session.query(Vacancies).filter_by(
                id=doc_request.reference_vacancy_id
            ).first()
            if vacancy:
                vacancy_title = vacancy.title
                company = session.query(MasterExternalCompanies).filter_by(
                    id=vacancy.company_id
                ).first()
                if company:
                    company_name = company.name

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = f"cover_letter_{request_id}_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(UPLOAD_DIR, filename)

        _build_cover_letter_pdf(
            student_full_name=student.full_name,
            nim=student.nim,
            department_name=department_name,
            semester=student.semester,
            purpose=doc_request.purpose or "melamar pekerjaan / magang",
            vacancy_title=vacancy_title,
            company_name=company_name,
            request_id=request_id,
            output_path=output_path,
        )

        generated_url = f"/uploads/documents/{filename}"
        doc_request.generated_url = generated_url
        doc_request.status = "COMPLETED"
        session.commit()

        return {"success": True, "generated_url": generated_url, "request_id": request_id}

    except Exception as exc:
        session.rollback()
        try:
            doc_request.status = "FAILED"
            session.commit()
        except Exception:
            session.rollback()
        raise self.retry(exc=exc)
    finally:
        session.close()
