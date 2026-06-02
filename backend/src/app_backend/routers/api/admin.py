import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, File, Query, UploadFile
from sqlalchemy.orm import joinedload

from app_backend.domain.user import User as DomainUser
from app_backend.features.admin import (
    ListUsersCommand,
    ToggleUserActiveCommand,
    list_users_command_handler,
    toggle_user_active_command_handler,
)
from app_backend.features.admin.master_data_service import MasterDataService
from app_backend.features.application import (
    ListPendingVerificationCommand,
    RejectApplicationProofCommand,
    VerifyApplicationCommand,
    list_pending_verification_command_handler,
    reject_application_proof_command_handler,
    verify_application_command_handler,
)
from app_backend.features.placement import ListAdminPlacementsCommand, list_admin_placements_command_handler
from app_backend.models.profiles_admin import ProfilesAdmin
from app_backend.models.vacancies import Vacancies
from app_backend.schemas.admin import (
    AdminProfileResponse,
    AdminProfileUpdate,
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
    SkillCreate,
    SkillResponse,
    SkillUpdate,
)
from app_backend.schemas.application import (
    ApplicationRejectPayload,
    ApplicationResponse,
    ApplicationVerifyPayload,
    AdminApplicationResponse,
    ApplicationAdminNotesPayload,
)
from app_backend.schemas.placement import PlacementResponse
from app_backend.schemas.user import UserResponse
from app_backend.schemas.vacancy import (
    CompanyInfo,
    VacancyListResponse,
    VacancyScrapeRequest,
    VacancyScrapeResponse,
    VacancySummaryResponse,
)
from app_backend.shared.auth_dependencies import require_admin
from app_backend.shared.database import get_session
from app_backend.shared.dependencies import get_master_data_service
from app_backend.shared.tasks.vacancy_tasks import scrape_vacancies

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
)


def queue_scrape_vacancies(source_urls: List[str], default_close_days: int):
    return scrape_vacancies.delay(source_urls, default_close_days=default_close_days)

# User Account Activation (Section 1.2)


@router.patch(
    "/users/{user_id}/toggle-active",
    response_model=UserResponse,
    summary="Toggle aktif/nonaktif akun user",
)
async def toggle_user_active(
    user_id: uuid.UUID,
    session=Depends(get_session),
    _: DomainUser = Depends(require_admin),
) -> UserResponse:
    # Admin menonaktifkan atau mengaktifkan kembali akun user.
    # Toggle: is_active = True, False, dan sebaliknya.
    result = toggle_user_active_command_handler(
        command=ToggleUserActiveCommand(user_id=user_id),
        session=session,
    )
    if result.got_error():
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=result.error_message)
    return result.user


@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="Daftar semua user (mahasiswa/admin)",
)
async def list_users(
    role: Optional[str] = None,
    session=Depends(get_session),
    _: DomainUser = Depends(require_admin),
) -> List[UserResponse]:
    # Daftar semua user di sistem. Bisa difilter berdasarkan role.
    result = list_users_command_handler(
        command=ListUsersCommand(role=role),
        session=session,
    )
    if result.got_error():
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=result.error_message)
    return result.items


# Admin Profile (Section 2.3)


@router.get(
    "/profile/me",
    response_model=AdminProfileResponse,
    summary="Profil admin yang sedang login",
)
async def get_admin_profile(
    session=Depends(get_session),
    current_user: DomainUser = Depends(require_admin),
) -> AdminProfileResponse:
    # Kembalikan data profil admin berdasarkan JWT access token.
    profile = session.query(ProfilesAdmin).filter(ProfilesAdmin.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Profil admin tidak ditemukan",
        )
    return AdminProfileResponse(
        user_id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        full_name=profile.full_name,
        unit_name=profile.unit_name,
        nip=profile.nip,
        last_login_at=current_user.last_login_at,
        updated_at=profile.updated_at,
    )


@router.patch(
    "/profile/me",
    response_model=AdminProfileResponse,
    summary="Update profil admin",
)
async def update_admin_profile(
    payload: AdminProfileUpdate,
    session=Depends(get_session),
    current_user: DomainUser = Depends(require_admin),
) -> AdminProfileResponse:
    # Update nama, unit kerja, atau NIP admin yang sedang login.
    from sqlalchemy.exc import IntegrityError

    profile = session.query(ProfilesAdmin).filter(ProfilesAdmin.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Profil admin tidak ditemukan")

    try:
        if payload.full_name is not None:
            profile.full_name = payload.full_name
        if payload.unit_name is not None:
            profile.unit_name = payload.unit_name
        if payload.nip is not None:
            profile.nip = payload.nip
        profile.updated_at = datetime.now(timezone.utc)
        session.commit()
        session.refresh(profile)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"NIP '{payload.nip}' sudah digunakan oleh admin lain",
        )

    return AdminProfileResponse(
        user_id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        full_name=profile.full_name,
        unit_name=profile.unit_name,
        nip=profile.nip,
        last_login_at=current_user.last_login_at,
        updated_at=profile.updated_at,
    )


# Manage Departments (Section 2.1)


@router.get(
    "/departments",
    response_model=List[DepartmentResponse],
    summary="Daftar semua Program Studi",
)
async def list_departments(
    master_data_service: MasterDataService = Depends(get_master_data_service),
    _: DomainUser = Depends(require_admin),
) -> List[DepartmentResponse]:
    return master_data_service.list_departments()


@router.post(
    "/departments",
    response_model=DepartmentResponse,
    status_code=HTTPStatus.CREATED,
    summary="Tambah Program Studi baru",
)
async def create_department(
    payload: DepartmentCreate,
    master_data_service: MasterDataService = Depends(get_master_data_service),
    _: DomainUser = Depends(require_admin),
) -> DepartmentResponse:
    try:
        return master_data_service.create_department(payload)
    except Exception as exc:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(exc))


@router.patch(
    "/departments/{dept_id}",
    response_model=DepartmentResponse,
    summary="Update Program Studi",
)
async def update_department(
    dept_id: uuid.UUID,
    payload: DepartmentUpdate,
    master_data_service: MasterDataService = Depends(get_master_data_service),
    _: DomainUser = Depends(require_admin),
) -> DepartmentResponse:
    try:
        return master_data_service.update_department(dept_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(exc))


@router.delete(
    "/departments/{dept_id}",
    status_code=HTTPStatus.NO_CONTENT,
    summary="Hapus Program Studi",
)
async def delete_department(
    dept_id: uuid.UUID,
    master_data_service: MasterDataService = Depends(get_master_data_service),
    _: DomainUser = Depends(require_admin),
) -> None:
    try:
        master_data_service.delete_department(dept_id)
    except ValueError as exc:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(exc))


# Manage Skills (Section 2.1)


@router.get(
    "/skills",
    response_model=List[SkillResponse],
    summary="Daftar semua Master Skill",
)
async def list_skills(
    master_data_service: MasterDataService = Depends(get_master_data_service),
    _: DomainUser = Depends(require_admin),
) -> List[SkillResponse]:
    return master_data_service.list_skills()


@router.post(
    "/skills",
    response_model=SkillResponse,
    status_code=HTTPStatus.CREATED,
    summary="Tambah skill baru",
)
async def create_skill(
    payload: SkillCreate,
    master_data_service: MasterDataService = Depends(get_master_data_service),
    _: DomainUser = Depends(require_admin),
) -> SkillResponse:
    try:
        return master_data_service.create_skill(payload)
    except Exception as exc:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(exc))


@router.patch(
    "/skills/{skill_id}",
    response_model=SkillResponse,
    summary="Update skill",
)
async def update_skill(
    skill_id: uuid.UUID,
    payload: SkillUpdate,
    master_data_service: MasterDataService = Depends(get_master_data_service),
    _: DomainUser = Depends(require_admin),
) -> SkillResponse:
    try:
        return master_data_service.update_skill(skill_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(exc))


@router.delete(
    "/skills/{skill_id}",
    status_code=HTTPStatus.NO_CONTENT,
    summary="Hapus skill",
)
async def delete_skill(
    skill_id: uuid.UUID,
    master_data_service: MasterDataService = Depends(get_master_data_service),
    _: DomainUser = Depends(require_admin),
) -> None:
    try:
        master_data_service.delete_skill(skill_id)
    except ValueError as exc:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(exc))


# Manage External Companies (Section 2.1)


@router.get(
    "/companies",
    response_model=List[CompanyResponse],
    summary="Daftar semua perusahaan eksternal",
)
async def list_companies(
    master_data_service: MasterDataService = Depends(get_master_data_service),
    _: DomainUser = Depends(require_admin),
) -> List[CompanyResponse]:
    return master_data_service.list_companies()


@router.post(
    "/companies",
    response_model=CompanyResponse,
    status_code=HTTPStatus.CREATED,
    summary="Tambah perusahaan eksternal baru",
)
async def create_company(
    payload: CompanyCreate,
    master_data_service: MasterDataService = Depends(get_master_data_service),
    _: DomainUser = Depends(require_admin),
) -> CompanyResponse:
    try:
        return master_data_service.create_company(payload)
    except Exception as exc:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(exc))


@router.patch(
    "/companies/{company_id}",
    response_model=CompanyResponse,
    summary="Update perusahaan eksternal",
)
async def update_company(
    company_id: uuid.UUID,
    payload: CompanyUpdate,
    master_data_service: MasterDataService = Depends(get_master_data_service),
    _: DomainUser = Depends(require_admin),
) -> CompanyResponse:
    try:
        return master_data_service.update_company(company_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(exc))


@router.delete(
    "/companies/{company_id}",
    status_code=HTTPStatus.NO_CONTENT,
    summary="Hapus perusahaan eksternal",
)
async def delete_company(
    company_id: uuid.UUID,
    master_data_service: MasterDataService = Depends(get_master_data_service),
    _: DomainUser = Depends(require_admin),
) -> None:
    try:
        master_data_service.delete_company(company_id)
    except ValueError as exc:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post(
    "/companies/upload-logo",
    status_code=HTTPStatus.OK,
    summary="Upload logo perusahaan ke storage S3/Lokal",
)
async def upload_company_logo(
    file: UploadFile = File(...),
    _: DomainUser = Depends(require_admin),
) -> dict:
    # Unggah file logo perusahaan (JPEG/PNG/WEBP, max 10MB).
    # Mengembalikan URL publik file yang diunggah.
    import os
    from app_backend.conf.settings import settings
    from app_backend.shared.s3_storage import get_s3_client, upload_fileobj

    valid_content_types = ["image/jpeg", "image/png", "image/jpg", "image/gif", "image/webp"]
    if file.content_type not in valid_content_types:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="File harus berupa gambar (JPEG, PNG, WEBP, GIF)")

    # Extension check
    filename = file.filename.lower()
    ext = os.path.splitext(filename)[1]
    if ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Ekstensi file tidak valid")

    # Size check
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    MAX_SIZE = 10 * 1024 * 1024  # 10MB
    if file_size > MAX_SIZE:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Ukuran logo melebihi batas maksimal 10MB")

    unique_filename = f"logo_{uuid.uuid4().hex[:12]}{ext}"
    s3_key = f"companies-logo/{unique_filename}"

    try:
        if settings.storage_type == "s3":
            s3_client = get_s3_client()
            success = upload_fileobj(s3_client, file.file, settings.s3_bucket, s3_key, content_type=file.content_type)
            if not success:
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Gagal mengunggah logo ke S3")

            # Construct public URL (for Supabase Storage S3 gateway)
            if "storage.supabase.co/storage/v1/s3" in settings.s3_endpoint:
                public_endpoint = settings.s3_endpoint.replace("/storage/v1/s3", "/storage/v1/object/public")
                logo_url = f"{public_endpoint}/{settings.s3_bucket}/{s3_key}"
            else:
                logo_url = f"{settings.s3_endpoint}/{settings.s3_bucket}/{s3_key}"
        else:
            # Fallback local
            os.makedirs("uploads/companies-logo", exist_ok=True)
            file_path = os.path.join("uploads/companies-logo", unique_filename)
            with open(file_path, "wb") as buffer:
                buffer.write(file.file.read())
            logo_url = f"/uploads/companies-logo/{unique_filename}"

        return {"logo_url": logo_url}
    except Exception as exc:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Gagal mengunggah logo: {exc}")


# Manage Applications (Section 4)


@router.get(
    "/vacancies",
    response_model=VacancyListResponse,
    summary="Daftar semua lowongan untuk admin",
)
async def list_admin_vacancies(
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    session=Depends(get_session),
    _: DomainUser = Depends(require_admin),
) -> VacancyListResponse:
    query = session.query(Vacancies).options(joinedload(Vacancies.company))
    if is_active is not None:
        query = query.filter(Vacancies.is_active.is_(is_active))

    total = query.count()
    vacancies = query.order_by(Vacancies.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    items = [
        VacancySummaryResponse(
            id=vacancy.id,
            company=CompanyInfo(
                id=vacancy.company.id,
                name=vacancy.company.name,
                industry=vacancy.company.industry,
                website_url=vacancy.company.website_url,
                logo_url=vacancy.company.logo_url,
            ),
            title=vacancy.title,
            type=vacancy.type,
            open_date=vacancy.open_date,
            close_date=vacancy.close_date,
            location=vacancy.location,
            payment_type=vacancy.payment_type,
            compensation_min=vacancy.compensation_min,
            compensation_max=vacancy.compensation_max,
            compensation_note=vacancy.compensation_note,
            source_url=vacancy.source_url,
            is_scraped=vacancy.is_scraped if vacancy.is_scraped is not None else False,
            is_auto_close=vacancy.is_auto_close if vacancy.is_auto_close is not None else True,
            is_active=vacancy.is_active if vacancy.is_active is not None else True,
            created_by=vacancy.created_by,
            created_at=vacancy.created_at,
            updated_at=vacancy.updated_at,
        )
        for vacancy in vacancies
    ]

    return VacancyListResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page if total > 0 else 1,
    )


@router.post(
    "/vacancies/scrape",
    response_model=VacancyScrapeResponse,
    summary="Scrape dan import lowongan dari URL eksternal",
)
async def scrape_admin_vacancies(
    payload: VacancyScrapeRequest,
    _: DomainUser = Depends(require_admin),
) -> VacancyScrapeResponse:
    async_result = queue_scrape_vacancies(
        [str(url) for url in payload.source_urls],
        default_close_days=payload.default_close_days,
    )
    return VacancyScrapeResponse(
        status="queued",
        message="Scraping berjalan di background. Hasil akan muncul di tab Hasil Scraping setelah task selesai.",
        task_id=str(async_result.id),
        total=len(payload.source_urls),
    )


@router.get(
    "/applications/pending-verification",
    response_model=List[AdminApplicationResponse],
    summary="Daftar lamaran pending verifikasi",
)
async def list_pending_verification(
    session=Depends(get_session),
    _: DomainUser = Depends(require_admin),
) -> List[AdminApplicationResponse]:
    result = list_pending_verification_command_handler(ListPendingVerificationCommand(), session)
    if result.got_error():
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=result.error_message)
    return result.items


@router.post(
    "/applications/{application_id}/verify",
    summary="Verifikasi dan buat placement",
)
async def verify_application(
    application_id: uuid.UUID,
    payload: ApplicationVerifyPayload,
    session=Depends(get_session),
    current_admin: DomainUser = Depends(require_admin),
):
    result = verify_application_command_handler(
        VerifyApplicationCommand(
            application_id=application_id,
            admin_id=current_admin.id,
            start_date=payload.start_date,
            end_date=payload.end_date,
        ),
        session,
    )
    if result.got_error():
        err_status = result.error_code if hasattr(result, "error_code") and result.error_code else HTTPStatus.BAD_REQUEST
        raise HTTPException(status_code=err_status, detail=result.error_message)
    return {"message": "Placement berhasil dibuat", "placement_id": result.placement.id}


@router.post(
    "/applications/{application_id}/reject-proof",
    response_model=ApplicationResponse,
    summary="Tolak bukti dan kembalikan ke OFFERED",
)
async def reject_application_proof(
    application_id: uuid.UUID,
    payload: ApplicationRejectPayload,
    session=Depends(get_session),
    current_admin: DomainUser = Depends(require_admin),
):
    result = reject_application_proof_command_handler(
        RejectApplicationProofCommand(
            application_id=application_id,
            admin_id=current_admin.id,
            reason=payload.reason,
        ),
        session,
    )
    if result.got_error():
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=result.error_message)
    return result.application


# Manage Placements (Section 5)


@router.get(
    "/placements",
    response_model=List[PlacementResponse],
    summary="Daftar semua penempatan",
)
async def list_admin_placements(
    session=Depends(get_session),
    _: DomainUser = Depends(require_admin),
) -> List[PlacementResponse]:
    result = list_admin_placements_command_handler(ListAdminPlacementsCommand(), session)
    if result.got_error():
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=result.error_message)
    return result.placements

@router.patch(
    "/applications/{application_id}/notes",
    response_model=AdminApplicationResponse,
    summary="Admin adds note/requests data for application"
)
def admin_add_notes(
    application_id: uuid.UUID,
    payload: ApplicationAdminNotesPayload,
    current_user: DomainUser = Depends(require_admin),
    session = Depends(get_session),
):
    from app_backend.models.applications import Applications
    from app_backend.models.notification_queue import NotificationQueue
    from sqlalchemy.orm import joinedload
    
    app = session.query(Applications).options(joinedload(Applications.vacancy)).filter_by(id=application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Lamaran tidak ditemukan")
    
    app.admin_notes = payload.admin_notes
    
    notif = NotificationQueue(
        title=f"Permintaan Data Tambahan: {app.vacancy.title}",
        message=f"Admin mengirim pesan: {payload.admin_notes}",
        user_id=app.student_id,
        channel="IN_APP",
        status="QUEUED",
    )
    session.add(notif)
    
    session.commit()
    session.refresh(app)
    return app
