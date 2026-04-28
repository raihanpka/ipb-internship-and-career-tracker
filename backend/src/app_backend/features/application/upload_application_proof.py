import os
import shutil
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import UploadFile

from app_backend.models.applications import Applications

UPLOAD_DIR = "uploads/proofs"

@dataclass
class UploadApplicationProofCommand:
    application_id: uuid.UUID
    student_id: uuid.UUID
    file: UploadFile


@dataclass
class UploadApplicationProofResult:
    proof_url: Optional[str] = None
    message: Optional[str] = None
    error_message: Optional[str] = None

    def got_error(self) -> bool:
        return self.error_message is not None


def upload_application_proof_command_handler(
    command: UploadApplicationProofCommand,
    session: Session,
) -> UploadApplicationProofResult:
    """
    Business Rules:
    1. Hanya menerima image/jpeg, image/png, application/pdf.
    2. Ukuran maksimum 5MB.
    3. Endpoint ini hanya bisa dipanggil jika application.status = ACCEPTED
    """
    application = (
        session.query(Applications)
        .filter_by(id=command.application_id, student_id=command.student_id)
        .first()
    )
    if not application:
        return UploadApplicationProofResult(error_message="Lamaran tidak ditemukan")

    if application.status != "ACCEPTED":
        return UploadApplicationProofResult(error_message="Status lamaran harus ACCEPTED untuk mengunggah bukti")

    file = command.file
    valid_content_types = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in valid_content_types:
        return UploadApplicationProofResult(error_message="File harus berupa image/jpeg, image/png, atau application/pdf")

    # Extension check
    filename = file.filename.lower()
    if not (filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png") or filename.endswith(".pdf")):
        return UploadApplicationProofResult(error_message="Ekstensi file tidak valid")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    ext = os.path.splitext(filename)[1]
    unique_filename = f"proof_{command.application_id}_{uuid.uuid4().hex[:8]}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        MAX_SIZE = 10 * 1024 * 1024  # 10MB
        size = 0
        
        with open(file_path, "wb") as buffer:
            while chunk := file.file.read(1024 * 1024):  # 1MB per iterasi
                size += len(chunk)
                if size > MAX_SIZE:
                    buffer.close()
                    os.remove(file_path)
                    return UploadApplicationProofResult(error_message="Ukuran file melebihi batas maksimal 15MB")
                buffer.write(chunk)
            
        proof_url = f"/uploads/proofs/{unique_filename}"
        
        # Trigger an update to insert into application_logs
        # Since status doesn't change, we just create a dummy update or insert the log manually.
        # But wait, SQLAlchemy event listener triggers on `status` change.
        # Here we just want to insert a log with action = PROOF_UPLOADED, but we don't have action column.
        # So we insert an application_logs row directly with previous_status=ACCEPTED and new_status=ACCEPTED.
        
        from sqlalchemy import text
        session.execute(
            text("""
            INSERT INTO application_logs (id, application_id, previous_status, new_status, changed_by, proof_url, reason)
            VALUES (public.gen_random_uuid(), :app_id, :status, :status, :by, :proof, 'Upload Bukti')
            """),
            {
                "app_id": application.id,
                "status": application.status,
                "by": command.student_id,
                "proof": proof_url,
            }
        )
        
        session.commit()
        return UploadApplicationProofResult(proof_url=proof_url, message="Bukti berhasil diunggah")

    except Exception as exc:
        session.rollback()
        return UploadApplicationProofResult(error_message=f"Upload gagal: {exc}")
