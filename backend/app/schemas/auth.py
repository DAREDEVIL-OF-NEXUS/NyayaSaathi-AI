import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field

class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    is_verified: bool
    mfa_enabled: bool
    created_at: datetime.datetime

class UserSignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters password")
    full_name: str = Field(..., min_length=2, max_length=100)

class UserSignInRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional[UserProfile] = None
    mfa_required: bool = False
    mfa_temp_token: Optional[str] = None
    message: Optional[str] = None

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class MFASetupResponse(BaseModel):
    secret: str
    qr_code_data_uri: str
    provisioning_uri: str

class MFAVerifySetupRequest(BaseModel):
    secret: str
    code: str = Field(..., min_length=6, max_length=6)

class MFASetupCompleteResponse(BaseModel):
    status: str
    message: str
    backup_codes: List[str]

class MFAChallengeRequest(BaseModel):
    mfa_temp_token: str
    code: str = Field(..., min_length=6, max_length=32, description="6-digit TOTP code or Backup Recovery Code")

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

class SessionItem(BaseModel):
    id: str
    user_agent: Optional[str]
    ip_address: Optional[str]
    is_revoked: bool
    created_at: datetime.datetime
    expires_at: datetime.datetime
    is_current: bool = False
