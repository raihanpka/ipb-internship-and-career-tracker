import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app_backend.features.application.initialize_apply import (
    InitializeApplyCommand,
    initialize_apply_command_handler,
)
from app_backend.features.application.update_status import (
    UpdateApplicationStatusCommand,
    update_application_status_command_handler,
)
from app_backend.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationStatusUpdate,
    ApplicationStatusUpdateResponse,
)
from app_backend.shared.database import get_session
from app_backend.shared.dependencies import require_student

router = APIRouter(prefix="/api/v1/applications", tags=["applications"])


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def initialize_apply(
    payload: ApplicationCreate,
    current_user=Depends(require_student),
    session: Session = Depends(get_session),
):
    result = initialize_apply_command_handler(
        command=InitializeApplyCommand(
            payload=payload,
            student_id=current_user.id,
        ),
        session=session,
    )

    if result.error_message:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.error_message)

    return result.application


@router.patch(
    "/{application_id}/status",
    response_model=ApplicationStatusUpdateResponse,
    status_code=status.HTTP_200_OK,
)
def update_application_status(
    application_id: uuid.UUID,
    payload: ApplicationStatusUpdate,
    current_user=Depends(require_student),
    session: Session = Depends(get_session),
):
    result = update_application_status_command_handler(
        command=UpdateApplicationStatusCommand(
            application_id=application_id,
            student_id=current_user.id,
            new_status=payload.new_status,
            proof_url=payload.proof_url,
            reason=payload.reason,
            changed_by=current_user.id,
        ),
        session=session,
    )

    if result.error_message:
        raise HTTPException(
            status_code=result.error_status_code,
            detail=result.error_message,
        )

    return ApplicationStatusUpdateResponse(
        application=result.application,
        log=result.log,
    )