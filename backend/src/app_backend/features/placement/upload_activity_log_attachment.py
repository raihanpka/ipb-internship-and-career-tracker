import os
import uuid
from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app_backend.models.activity_logs import ActivityLogs
from app_backend.models.placements import Placements

UPLOAD_DIR = "uploads/activity_logs"

@dataclass
class UploadActivityLogAttachmentCommand:
    placement_id: uuid.UUID
    log_id: uuid.UUID
    student_id: uuid.UUID
    file: UploadFile

@dataclass
class UploadActivityLogAttachmentResult:
    attachment_url: Optional[str] = None
    message: Optional[str] = None
    error_message: Optional[str] = None

    def got_error(self) -> bool:
        return self.error_message is not None

def upload_activity_log_attachment_command_handler(
    command: UploadActivityLogAttachmentCommand,
    session: Session,
) -> UploadActivityLogAttachmentResult:
    # Validasi placement exists & belongs to student
    placement = session.query(Placements).filter_by(id=command.placement_id, student_id=command.student_id).first()
    if not placement:
        return UploadActivityLogAttachmentResult(error_message="Placement tidak ditemukan")

    # Validasi log exists
    log = session.query(ActivityLogs).filter_by(id=command.log_id, placement_id=placement.id).first()
    if not log:
        return UploadActivityLogAttachmentResult(error_message="Activity log tidak ditemukan")

    file = command.file
    valid_content_types = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in valid_content_types:
        return UploadActivityLogAttachmentResult(error_message="File harus berupa image/jpeg, image/png, atau application/pdf")

    filename = file.filename.lower()
    if not (filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png") or filename.endswith(".pdf")):
        return UploadActivityLogAttachmentResult(error_message="Ekstensi file tidak valid")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    ext = os.path.splitext(filename)[1]
    unique_filename = f"log_{command.log_id}_{uuid.uuid4().hex[:8]}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        MAX_SIZE = 15 * 1024 * 1024  # 15MB
        size = 0
        
        with open(file_path, "wb") as buffer:
            while chunk := file.file.read(1024 * 1024):  # 1MB iterasi
                size += len(chunk)
                if size > MAX_SIZE:
                    buffer.close()
                    os.remove(file_path)
                    return UploadActivityLogAttachmentResult(error_message="Ukuran file melebihi batas maksimal 15MB")
                buffer.write(chunk)
            
        attachment_url = f"/uploads/activity_logs/{unique_filename}"
        
        log.attachment_url = attachment_url
        session.commit()
        
        return UploadActivityLogAttachmentResult(attachment_url=attachment_url, message="Lampiran berhasil diunggah")

    except Exception as exc:
        session.rollback()
        return UploadActivityLogAttachmentResult(error_message=f"Upload gagal: {exc}")
