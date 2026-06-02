import uuid
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app_backend.features.application import UploadApplicationProofCommand, upload_application_proof_command_handler
from app_backend.features.application.application_service import ApplicationService
from app_backend.schemas.application import (
    ApplicationCreate,
    ApplicationLogResponse,
    ApplicationResponse,
    ApplicationUpdateStatus,
    ApplicationStudentReplyPayload,
    ApplicationDetailResponse,
)
from app_backend.shared.auth_dependencies import require_student
from app_backend.shared.database import get_session
from app_backend.shared.dependencies import get_application_service

router = APIRouter(prefix="/api/v1/applications", tags=["applications"])


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def initialize_apply(
    payload: ApplicationCreate,
    current_user=Depends(require_student),
    app_service: ApplicationService = Depends(get_application_service),
):
    try:
        return app_service.apply(current_user.id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal melamar lowongan: {exc}",
        )


@router.get("/my", response_model=List[ApplicationDetailResponse], summary="Daftar lamaran mahasiswa saat ini")
def get_my_applications(
    current_user=Depends(require_student),
    app_service: ApplicationService = Depends(get_application_service),
):
    try:
        return app_service.get_my_applications(current_user.id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil daftar lamaran: {exc}",
        )


@router.patch(
    "/{application_id}/status",
    response_model=ApplicationResponse,
    summary="Mahasiswa memperbarui status lamaran",
)
def update_application_status(
    application_id: uuid.UUID,
    payload: ApplicationUpdateStatus,
    current_user=Depends(require_student),
    app_service: ApplicationService = Depends(get_application_service),
):
    try:
        return app_service.update_status(application_id, current_user.id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal memperbarui status: {exc}",
        )


@router.post("/{application_id}/proof", summary="Upload bukti screenshot LoA")
def upload_application_proof(
    application_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user=Depends(require_student),
    session: Session = Depends(get_session),  # Proof upload involves S3, leaving as is for now or moving to service later
):
    result = upload_application_proof_command_handler(
        command=UploadApplicationProofCommand(
            application_id=application_id,
            student_id=current_user.id,
            file=file,
        ),
        session=session,
    )

    if result.got_error():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.error_message)

    return {"message": result.message, "proof_url": result.proof_url}


@router.get(
    "/{application_id}/history",
    response_model=List[ApplicationLogResponse],
    summary="Riwayat seluruh perubahan status lamaran",
)
def get_application_history(
    application_id: uuid.UUID,
    current_user=Depends(require_student),
    app_service: ApplicationService = Depends(get_application_service),
):
    try:
        return app_service.get_history(application_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil riwayat: {exc}",
        )


@router.patch(
    "/{application_id}/reply",
    response_model=ApplicationDetailResponse,
    summary="Student replies to admin notes"
)
def student_reply_notes(
    application_id: uuid.UUID,
    payload: ApplicationStudentReplyPayload,
    current_user=Depends(require_student),
    session=Depends(get_session),
):
    from app_backend.models.applications import Applications
    app = session.query(Applications).filter_by(id=application_id, student_id=current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Lamaran tidak ditemukan")
    
    app.student_reply = payload.student_reply
    session.commit()
    session.refresh(app)
    return app

