from typing import List

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app_backend.features.document_request import (
    CreateDocumentRequestCommand,
    create_document_request_command_handler,
    GetDocumentRequestCommand,
    get_document_request_command_handler,
    ListDocumentRequestsCommand,
    list_document_requests_command_handler,
)
from app_backend.schemas.document_request import (
    DocumentRequestCreate,
    DocumentRequestResponse,
    DocumentRequestSubmitResponse,
)
from app_backend.shared.database import get_session
from app_backend.shared.dependencies import require_student

router = APIRouter(prefix="/api/v1/document-requests", tags=["document-requests"])


@router.post(
    "",
    response_model=DocumentRequestSubmitResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Mahasiswa mengajukan permohonan surat pengantar",
)
def create_document_request(
    payload: DocumentRequestCreate,
    current_user=Depends(require_student),
    session: Session = Depends(get_session),
):
    result = create_document_request_command_handler(
        command=CreateDocumentRequestCommand(
            student_id=current_user.id,
            purpose=payload.purpose,
            vacancy_id=payload.vacancy_id,
        ),
        session=session,
    )
    if result.got_error():
        raise HTTPException(status_code=result.error_code, detail=result.error_message)
    return DocumentRequestSubmitResponse(
        request_id=result.request_id,
        task_id=result.task_id,
        message=result.message,
    )


@router.get(
    "",
    response_model=List[DocumentRequestResponse],
    summary="Riwayat semua permohonan surat mahasiswa yang sedang login",
)
def list_document_requests(
    current_user=Depends(require_student),
    session: Session = Depends(get_session),
):
    result = list_document_requests_command_handler(
        command=ListDocumentRequestsCommand(student_id=current_user.id),
        session=session,
    )
    if result.got_error():
        raise HTTPException(status_code=result.error_code, detail=result.error_message)
    return result.requests


@router.get(
    "/{request_id}",
    response_model=DocumentRequestResponse,
    summary="Status permohonan surat dan URL dokumen jika sudah siap",
)
def get_document_request(
    request_id: uuid.UUID,
    current_user=Depends(require_student),
    session: Session = Depends(get_session),
):
    result = get_document_request_command_handler(
        command=GetDocumentRequestCommand(
            request_id=request_id,
            student_id=current_user.id,
        ),
        session=session,
    )
    if result.got_error():
        raise HTTPException(status_code=result.error_code, detail=result.error_message)
    return result.request
