from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app_backend.domain.user import UserRole
from app_backend.models.profiles_student import ProfilesStudent
from app_backend.models.users import Users
from app_backend.schemas.user import StudentRegister, UserResponse
from app_backend.shared.security import hash_password


class RegisterStudentException(Exception):
    pass


@dataclass
class RegisterStudentCommand:
    payload: StudentRegister


@dataclass
class RegisterStudentResult:
    user: Optional[UserResponse] = None
    error_message: Optional[str] = None

    def got_error(self) -> bool:
        return self.error_message is not None


def register_student_command_handler(
    command: RegisterStudentCommand,
    session: Session,
) -> RegisterStudentResult:
    """
    Business Rules:
    1. Email harus unik (cek public.users).
    2. NIM harus unik (cek profiles_student).
    3. Role di-hardcode ke STUDENT, tidak bisa diubah dari client.
    4. user dan profile_student dibuat dalam satu transaksi atomik.
    """
    if session.query(Users).filter(Users.email == command.payload.email).first():
        return RegisterStudentResult(error_message="Email sudah terdaftar")

    if session.query(ProfilesStudent).filter(ProfilesStudent.nim == command.payload.nim).first():
        return RegisterStudentResult(error_message="NIM sudah terdaftar")

    try:
        now = datetime.now(timezone.utc)
        user_id = uuid.uuid4()

        base_username = command.payload.email.split("@")[0]
        username = base_username
        suffix = 1
        while session.query(Users).filter(Users.username == username).first():
            username = f"{base_username}{suffix}"
            suffix += 1

        user = Users(
            id=user_id,
            email=command.payload.email,
            username=username,
            password_hash=hash_password(command.payload.password),
            role=UserRole.STUDENT.value,
            is_active=False,  # AKUN TIDAK AKTIF SAMPAI DIVERIFIKASI
            created_at=now,
            updated_at=now,
        )

        profile = ProfilesStudent(
            user_id=user_id,
            nim=command.payload.nim,
            full_name=command.payload.full_name,
            semester=command.payload.semester,
            department_id=command.payload.department_id,
            is_mbkm_eligible=True,
            updated_at=now,
        )

        session.add(user)
        session.flush()
        session.add(profile)

        # Buat Token Verifikasi
        from app_backend.models.auth_action_tokens import AuthActionTokens
        from app_backend.shared.security import generate_secure_token, hash_token
        from datetime import timedelta

        raw_token = generate_secure_token()
        expires_at = now + timedelta(hours=24)

        verification_token = AuthActionTokens(
            user_id=user_id,
            token_hash=hash_token(raw_token),
            action_type="ACTIVATE_ACCOUNT",
            expires_at=expires_at,
            is_used=False,
        )
        session.add(verification_token)
        session.commit()
        session.refresh(user)

        # Kirim Email Verifikasi
        from app_backend.shared.mailer import send_direct_email
        from app_backend.conf.settings import settings

        subject = "Your LARAS verification token"
        body = f"""
A new registration attempt was made to create a LARAS account for <strong>{user.email}</strong>.
<br><br>
Was this you? Enter this verification token on the activation page:
<br><br>
<div id="headline" style="font-size: 26px; font-weight: bold; color: #111827;">
  {raw_token}
</div>
<br>
Or click the following link to verify your account directly:
<div class="raw-link" style="margin-top: 15px;">
  <a href="{settings.frontend_url}/verify-email?token={raw_token}">{settings.frontend_url}/verify-email?token={raw_token}</a>
</div>
<br>
This token is valid for 24 hours. If you did not make this request, please ignore this email.
"""
        import threading

        threading.Thread(
            target=send_direct_email,
            args=(user.email, subject, body),
            kwargs={"user_name": command.payload.full_name},
            daemon=True,
        ).start()

        return RegisterStudentResult(
            user=UserResponse(
                id=user.id,
                email=user.email,
                role=user.role,
                is_active=user.is_active if user.is_active is not None else True,
                last_login_at=user.last_login_at,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
        )

    except ValueError as exc:
        session.rollback()
        return RegisterStudentResult(error_message=str(exc))
    except Exception as exc:
        session.rollback()
        return RegisterStudentResult(error_message=f"Registrasi gagal: {exc}")
