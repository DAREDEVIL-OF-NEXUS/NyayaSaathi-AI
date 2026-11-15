import uuid
import datetime
import secrets
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import (
    hash_password,
    verify_password,
    hash_token,
    create_access_token,
    create_refresh_token,
    create_mfa_pending_token,
    decode_token,
    generate_totp_secret,
    get_totp_uri,
    generate_qr_code_data_uri,
    verify_totp_code,
    generate_backup_codes,
)
from backend.app.models.entities import (
    User,
    UserSession,
    MFAConfiguration,
    BackupCode,
    EmailVerificationToken,
    PasswordResetToken,
)
from backend.app.schemas.auth import (
    UserSignUpRequest,
    UserSignInRequest,
    AuthResponse,
    UserProfile,
    VerifyEmailRequest,
    ResendVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    MFASetupResponse,
    MFAVerifySetupRequest,
    MFASetupCompleteResponse,
    MFAChallengeRequest,
    ChangePasswordRequest,
    SessionItem,
)
from backend.app.api.deps import get_current_user, log_audit_event
from backend.app.services.email.service import get_email_service

router = APIRouter(prefix="/auth", tags=["Authentication & Security"])

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def set_auth_cookies(response: Response, access_token: str, refresh_token: Optional[str] = None):
    # Set HttpOnly, secure, SameSite cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.SECURE_COOKIES,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )
    if refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=settings.SECURE_COOKIES,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
            path="/"
        )


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED, summary="Register a new consumer account")
async def signup(req: UserSignUpRequest, request: Request, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email.lower()).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An account with this email already exists.")

    new_user = User(
        id=str(uuid.uuid4()),
        email=req.email.lower(),
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        is_active=True,
        is_verified=False,
        created_at=datetime.datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate 6-digit numeric verification OTP
    code = f"{secrets.randbelow(900000) + 100000}"
    raw_token = secrets.token_urlsafe(32)
    token_rec = EmailVerificationToken(
        id=str(uuid.uuid4()),
        user_id=new_user.id,
        token_hash=hash_token(raw_token),
        code_hash=hash_token(code),
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.EMAIL_VERIFICATION_EXPIRE_MINUTES)
    )
    db.add(token_rec)
    db.commit()

    # Dispatch verification email via Brevo
    email_service = get_email_service()
    verification_url = f"{settings.FRONTEND_URL}/verify-email?email={new_user.email}&code={code}"
    await email_service.send_verification_email(
        to_email=new_user.email,
        user_name=new_user.full_name,
        code=code,
        verification_url=verification_url
    )

    log_audit_event(db, "AUTH_SIGNUP", user_id=new_user.id, ip_address=get_client_ip(request))

    return AuthResponse(
        user=UserProfile(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            is_verified=new_user.is_verified,
            mfa_enabled=False,
            created_at=new_user.created_at
        ),
        message="Account created successfully. Please check your email for verification instructions."
    )


@router.post("/verify-email", response_model=AuthResponse, summary="Verify email using 6-digit code")
async def verify_email(req: VerifyEmailRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification request.")

    if user.is_verified:
        return AuthResponse(message="Email is already verified.")

    code_hashed = hash_token(req.code)
    token_rec = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == user.id,
        EmailVerificationToken.code_hash == code_hashed,
        EmailVerificationToken.is_used == False,
        EmailVerificationToken.expires_at > datetime.datetime.utcnow()
    ).order_by(EmailVerificationToken.created_at.desc()).first()

    if not token_rec:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification code.")

    token_rec.is_used = True
    user.is_verified = True
    db.commit()

    # Issue initial access and refresh tokens
    access_token = create_access_token(user.id, user.email)
    raw_refresh, refresh_hash, refresh_exp = create_refresh_token(user.id)

    session = UserSession(
        user_id=user.id,
        refresh_token_hash=refresh_hash,
        user_agent=request.headers.get("User-Agent"),
        ip_address=get_client_ip(request),
        expires_at=refresh_exp
    )
    db.add(session)
    db.commit()

    set_auth_cookies(response, access_token, raw_refresh)
    log_audit_event(db, "AUTH_EMAIL_VERIFIED", user_id=user.id, ip_address=get_client_ip(request))

    return AuthResponse(
        access_token=access_token,
        refresh_token=raw_refresh,
        user=UserProfile(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_verified=user.is_verified,
            mfa_enabled=False,
            created_at=user.created_at
        ),
        message="Email verified successfully."
    )


@router.post("/resend-verification", summary="Resend email verification code")
async def resend_verification(req: ResendVerificationRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user or user.is_verified:
        return {"status": "success", "message": "If an unverified account exists, a new verification code was sent."}

    # Generate new code
    code = f"{secrets.randbelow(900000) + 100000}"
    raw_token = secrets.token_urlsafe(32)
    token_rec = EmailVerificationToken(
        id=str(uuid.uuid4()),
        user_id=user.id,
        token_hash=hash_token(raw_token),
        code_hash=hash_token(code),
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.EMAIL_VERIFICATION_EXPIRE_MINUTES)
    )
    db.add(token_rec)
    db.commit()

    email_service = get_email_service()
    verification_url = f"{settings.FRONTEND_URL}/verify-email?email={user.email}&code={code}"
    await email_service.send_verification_email(user.email, user.full_name, code, verification_url)
    log_audit_event(db, "AUTH_VERIFICATION_RESENT", user_id=user.id, ip_address=get_client_ip(request))

    return {"status": "success", "message": "If an unverified account exists, a new verification code was sent."}


@router.post("/signin", response_model=AuthResponse, summary="Sign in with email and password")
async def signin(req: UserSignInRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user or not verify_password(req.password, user.hashed_password):
        log_audit_event(db, "AUTH_LOGIN_FAILED", ip_address=get_client_ip(request), details={"email": req.email})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled. Please contact support.")

    # Check MFA requirement
    mfa_config = db.query(MFAConfiguration).filter(MFAConfiguration.user_id == user.id, MFAConfiguration.is_enabled == True).first()
    if mfa_config:
        mfa_temp_token = create_mfa_pending_token(user.id, user.email)
        log_audit_event(db, "AUTH_MFA_CHALLENGE_ISSUED", user_id=user.id, ip_address=get_client_ip(request))
        return AuthResponse(
            mfa_required=True,
            mfa_temp_token=mfa_temp_token,
            message="Two-Factor Authentication code required."
        )

    # Issue access and refresh tokens
    access_token = create_access_token(user.id, user.email)
    raw_refresh, refresh_hash, refresh_exp = create_refresh_token(user.id)

    session = UserSession(
        user_id=user.id,
        refresh_token_hash=refresh_hash,
        user_agent=request.headers.get("User-Agent"),
        ip_address=get_client_ip(request),
        expires_at=refresh_exp
    )
    db.add(session)
    db.commit()

    set_auth_cookies(response, access_token, raw_refresh)
    log_audit_event(db, "AUTH_LOGIN_SUCCESS", user_id=user.id, ip_address=get_client_ip(request))

    return AuthResponse(
        access_token=access_token,
        refresh_token=raw_refresh,
        user=UserProfile(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_verified=user.is_verified,
            mfa_enabled=False,
            created_at=user.created_at
        ),
        message="Sign in successful."
    )


@router.post("/mfa/challenge", response_model=AuthResponse, summary="Complete sign in via TOTP or Backup Code")
async def mfa_challenge(req: MFAChallengeRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    payload = decode_token(req.mfa_temp_token)
    if not payload or payload.get("type") != "mfa_pending":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired MFA challenge token.")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account invalid.")

    mfa_config = db.query(MFAConfiguration).filter(MFAConfiguration.user_id == user.id, MFAConfiguration.is_enabled == True).first()
    if not mfa_config:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is not enabled for this user.")

    # 1. Try TOTP code
    is_valid = verify_totp_code(mfa_config.totp_secret, req.code)

    # 2. If not valid TOTP, try Backup Recovery Code
    if not is_valid:
        backup_hash = hash_token(req.code.strip().upper())
        backup_rec = db.query(BackupCode).filter(
            BackupCode.user_id == user.id,
            BackupCode.code_hash == backup_hash,
            BackupCode.is_used == False
        ).first()

        if backup_rec:
            backup_rec.is_used = True
            backup_rec.used_at = datetime.datetime.utcnow()
            db.commit()
            is_valid = True
            log_audit_event(db, "AUTH_MFA_BACKUP_CODE_USED", user_id=user.id, ip_address=get_client_ip(request))

    if not is_valid:
        log_audit_event(db, "AUTH_MFA_FAILED", user_id=user.id, ip_address=get_client_ip(request))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TOTP or recovery code.")

    # Success: issue session and tokens
    access_token = create_access_token(user.id, user.email)
    raw_refresh, refresh_hash, refresh_exp = create_refresh_token(user.id)

    session = UserSession(
        user_id=user.id,
        refresh_token_hash=refresh_hash,
        user_agent=request.headers.get("User-Agent"),
        ip_address=get_client_ip(request),
        expires_at=refresh_exp
    )
    db.add(session)
    db.commit()

    set_auth_cookies(response, access_token, raw_refresh)
    log_audit_event(db, "AUTH_MFA_SUCCESS", user_id=user.id, ip_address=get_client_ip(request))

    return AuthResponse(
        access_token=access_token,
        refresh_token=raw_refresh,
        user=UserProfile(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_verified=user.is_verified,
            mfa_enabled=True,
            created_at=user.created_at
        ),
        message="Two-Factor Authentication verified successfully."
    )


@router.post("/mfa/setup", response_model=MFASetupResponse, summary="Initialize TOTP Two-Factor Authentication setup")
def mfa_setup(current_user: User = Depends(get_current_user)):
    secret = generate_totp_secret()
    provisioning_uri = get_totp_uri(secret, current_user.email)
    qr_data_uri = generate_qr_code_data_uri(provisioning_uri)

    return MFASetupResponse(
        secret=secret,
        qr_code_data_uri=qr_data_uri,
        provisioning_uri=provisioning_uri
    )


@router.post("/mfa/verify", response_model=MFASetupCompleteResponse, summary="Verify and enable TOTP Two-Factor Authentication")
async def mfa_verify_and_enable(
    req: MFAVerifySetupRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_totp_code(req.secret, req.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code. Could not enable MFA.")

    # Save or update MFA configuration
    mfa_config = db.query(MFAConfiguration).filter(MFAConfiguration.user_id == current_user.id).first()
    if not mfa_config:
        mfa_config = MFAConfiguration(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            totp_secret=req.secret,
            is_enabled=True
        )
        db.add(mfa_config)
    else:
        mfa_config.totp_secret = req.secret
        mfa_config.is_enabled = True

    # Generate 10 single-use recovery backup codes
    raw_codes, hashed_codes = generate_backup_codes(10)
    # Remove older backup codes if any
    db.query(BackupCode).filter(BackupCode.user_id == current_user.id).delete()

    for h_code in hashed_codes:
        db.add(BackupCode(user_id=current_user.id, code_hash=h_code, is_used=False))

    db.commit()

    # Send security notification
    email_service = get_email_service()
    await email_service.send_security_alert(
        current_user.email,
        current_user.full_name,
        "Two-Factor Authentication Enabled",
        f"TOTP Two-Factor Authentication was enabled from IP address {get_client_ip(request)}."
    )

    log_audit_event(db, "AUTH_MFA_ENABLED", user_id=current_user.id, ip_address=get_client_ip(request))

    return MFASetupCompleteResponse(
        status="success",
        message="Two-Factor Authentication has been successfully enabled. Save these backup recovery codes in a secure location.",
        backup_codes=raw_codes
    )


@router.post("/mfa/disable", summary="Disable Two-Factor Authentication")
async def mfa_disable(
    password: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password verification.")

    mfa_config = db.query(MFAConfiguration).filter(MFAConfiguration.user_id == current_user.id).first()
    if mfa_config:
        mfa_config.is_enabled = False
        db.query(BackupCode).filter(BackupCode.user_id == current_user.id).delete()
        db.commit()

    email_service = get_email_service()
    await email_service.send_security_alert(
        current_user.email,
        current_user.full_name,
        "Two-Factor Authentication Disabled",
        f"Two-Factor Authentication was disabled from IP {get_client_ip(request)}."
    )

    log_audit_event(db, "AUTH_MFA_DISABLED", user_id=current_user.id, ip_address=get_client_ip(request))
    return {"status": "success", "message": "Two-Factor Authentication has been disabled."}


@router.post("/forgot-password", summary="Request password reset token")
async def forgot_password(req: ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if user:
        raw_token = secrets.token_urlsafe(32)
        reset_rec = PasswordResetToken(
            id=str(uuid.uuid4()),
            user_id=user.id,
            token_hash=hash_token(raw_token),
            expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES)
        )
        db.add(reset_rec)
        db.commit()

        email_service = get_email_service()
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"
        await email_service.send_password_reset_email(user.email, user.full_name, reset_url)
        log_audit_event(db, "AUTH_PASSWORD_RESET_REQUESTED", user_id=user.id, ip_address=get_client_ip(request))

    # Always return consistent message to prevent account enumeration
    return {"status": "success", "message": "If an account exists with that email, a password reset link has been dispatched."}


@router.post("/reset-password", summary="Reset password using token")
async def reset_password(req: ResetPasswordRequest, request: Request, db: Session = Depends(get_db)):
    token_hashed = hash_token(req.token)
    reset_rec = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hashed,
        PasswordResetToken.is_used == False,
        PasswordResetToken.expires_at > datetime.datetime.utcnow()
    ).first()

    if not reset_rec:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired password reset link.")

    user = db.query(User).filter(User.id == reset_rec.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found.")

    user.hashed_password = hash_password(req.new_password)
    reset_rec.is_used = True

    # Invalidate all existing sessions upon password reset
    db.query(UserSession).filter(UserSession.user_id == user.id).update({"is_revoked": True})
    db.commit()

    email_service = get_email_service()
    await email_service.send_security_alert(
        user.email,
        user.full_name,
        "Password Successfully Changed",
        f"Your password was changed from IP {get_client_ip(request)}. All active sessions have been signed out."
    )

    log_audit_event(db, "AUTH_PASSWORD_RESET_COMPLETED", user_id=user.id, ip_address=get_client_ip(request))
    return {"status": "success", "message": "Password reset successful. Please sign in with your new password."}


@router.post("/refresh", response_model=AuthResponse, summary="Refresh access token using rotating refresh token")
def refresh_token(request: Request, response: Response, refresh_token_body: Optional[str] = None, db: Session = Depends(get_db)):
    raw_refresh = refresh_token_body or request.cookies.get("refresh_token")
    if not raw_refresh:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token.")

    token_hash = hash_token(raw_refresh)
    session = db.query(UserSession).filter(
        UserSession.refresh_token_hash == token_hash,
        UserSession.is_revoked == False,
        UserSession.expires_at > datetime.datetime.utcnow()
    ).first()

    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session. Please sign in again.")

    user = db.query(User).filter(User.id == session.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User invalid or deactivated.")

    # Rotate refresh token: revoke current and issue new
    session.is_revoked = True

    new_raw_refresh, new_refresh_hash, new_refresh_exp = create_refresh_token(user.id)
    new_session = UserSession(
        user_id=user.id,
        refresh_token_hash=new_refresh_hash,
        user_agent=request.headers.get("User-Agent"),
        ip_address=get_client_ip(request),
        expires_at=new_refresh_exp
    )
    db.add(new_session)
    db.commit()

    new_access_token = create_access_token(user.id, user.email)
    set_auth_cookies(response, new_access_token, new_raw_refresh)

    mfa_config = db.query(MFAConfiguration).filter(MFAConfiguration.user_id == user.id, MFAConfiguration.is_enabled == True).first()

    return AuthResponse(
        access_token=new_access_token,
        refresh_token=new_raw_refresh,
        user=UserProfile(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_verified=user.is_verified,
            mfa_enabled=bool(mfa_config),
            created_at=user.created_at
        ),
        message="Session refreshed."
    )


@router.post("/signout", summary="Sign out and revoke active session")
def signout(request: Request, response: Response, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    raw_refresh = request.cookies.get("refresh_token")
    if raw_refresh:
        token_hash = hash_token(raw_refresh)
        db.query(UserSession).filter(UserSession.refresh_token_hash == token_hash).update({"is_revoked": True})
        db.commit()

    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    log_audit_event(db, "AUTH_LOGOUT", user_id=current_user.id, ip_address=get_client_ip(request))
    return {"status": "success", "message": "Signed out successfully."}


@router.get("/me", response_model=UserProfile, summary="Get current authenticated user profile")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    mfa_config = db.query(MFAConfiguration).filter(MFAConfiguration.user_id == current_user.id, MFAConfiguration.is_enabled == True).first()
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_verified=current_user.is_verified,
        mfa_enabled=bool(mfa_config),
        created_at=current_user.created_at
    )


@router.get("/sessions", response_model=List[SessionItem], summary="List all active user sessions and devices")
def list_sessions(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_refresh = request.cookies.get("refresh_token")
    current_hash = hash_token(current_refresh) if current_refresh else None

    sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_revoked == False,
        UserSession.expires_at > datetime.datetime.utcnow()
    ).order_by(UserSession.created_at.desc()).all()

    return [
        SessionItem(
            id=s.id,
            user_agent=s.user_agent,
            ip_address=s.ip_address,
            is_revoked=s.is_revoked,
            created_at=s.created_at,
            expires_at=s.expires_at,
            is_current=(s.refresh_token_hash == current_hash)
        )
        for s in sessions
    ]


@router.delete("/sessions/{session_id}", summary="Revoke a specific session")
def revoke_session(session_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(UserSession).filter(UserSession.id == session_id, UserSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    session.is_revoked = True
    db.commit()
    return {"status": "success", "message": "Session revoked."}


@router.post("/change-password", summary="Change password for authenticated user")
async def change_password(
    req: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(req.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password incorrect.")

    current_user.hashed_password = hash_password(req.new_password)
    # Revoke other sessions
    db.query(UserSession).filter(UserSession.user_id == current_user.id).update({"is_revoked": True})
    db.commit()

    email_service = get_email_service()
    await email_service.send_security_alert(
        current_user.email,
        current_user.full_name,
        "Password Changed",
        f"Your account password was updated from IP {get_client_ip(request)}."
    )

    log_audit_event(db, "AUTH_PASSWORD_CHANGED", user_id=current_user.id, ip_address=get_client_ip(request))
    return {"status": "success", "message": "Password changed successfully."}
