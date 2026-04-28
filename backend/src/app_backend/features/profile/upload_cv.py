"""
Upload CV Feature – Command Handler.
Upload file CV PDF dan simpan URL ke database.
"""

from __future__ import annotations

import os
import shutil
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import UploadFile

from app_backend.models.profiles_student import ProfilesStudent

UPLOAD_DIR = "uploads/cv"

@dataclass
class UploadCVCommand:
    user_id: uuid.UUID
    file: UploadFile


@dataclass
class UploadCVResult:
    cv_url: Optional[str] = None
    message: Optional[str] = None
    error_message: Optional[str] = None

    def got_error(self) -> bool:
        return self.error_message is not None


def upload_cv_command_handler(
    command: UploadCVCommand,
    session: Session,
) -> UploadCVResult:
    """
    Business Rules:
    1. Profil mahasiswa harus ada.
    2. File harus PDF.
    3. File size limit (ditangani oleh fastapi tapi baiknya double check, max 5MB).
    """
    profile = (
        session.query(ProfilesStudent)
        .filter(ProfilesStudent.user_id == command.user_id)
        .first()
    )
    if not profile:
        return UploadCVResult(error_message="Profil mahasiswa tidak ditemukan")

    file = command.file
    if file.content_type != "application/pdf":
        return UploadCVResult(error_message="File harus berformat PDF")

    if not (command.file.filename and command.file.filename.lower().endswith(".pdf")):
        return UploadCVResult(error_message="Ekstensi file tidak diizinkan, harus .pdf")

    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    file_ext = ".pdf"
    unique_filename = f"{command.user_id}_{uuid.uuid4().hex[:8]}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        MAX_SIZE = 10 * 1024 * 1024  # 10MB
        size = 0
        
        with open(file_path, "wb") as buffer:
            while chunk := command.file.file.read(1024 * 1024):  # Batching 1MB per iterasi
                size += len(chunk)
                if size > MAX_SIZE:
                    buffer.close()
                    os.remove(file_path)
                    return UploadCVResult(error_message="Ukuran file melebihi batas maksimal 15MB")
                buffer.write(chunk)
            
        cv_url = f"/uploads/cv/{unique_filename}"
        profile.cv_url = cv_url
        profile.updated_at = datetime.now(timezone.utc)
        
        session.commit()
        return UploadCVResult(cv_url=cv_url, message="CV berhasil diupload")

    except Exception as exc:
        session.rollback()
        return UploadCVResult(error_message=f"Upload gagal: {exc}")
