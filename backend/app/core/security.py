import hashlib
import secrets
import datetime
import io
import base64
from typing import Optional, Dict, Any, List, Tuple
import bcrypt
import jwt
import pyotp
import qrcode
from backend.app.core.config import settings

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def hash_token(token: str) -> str:
    """Returns SHA-256 hex digest of a token/OTP to store safely in DB."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def create_access_token(user_id: str, email: str, expires_delta: Optional[datetime.timedelta] = None) -> str:
    expire = datetime.datetime.utcnow() + (expires_delta or datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": user_id,
        "email": email,
        "type": "access",
        "exp": expire,
        "iat": datetime.datetime.utcnow(),
        "iss": "nyayasaathi-api"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> Tuple[str, str, datetime.datetime]:
    """Generates a cryptographically secure random token, its SHA-256 hash, and expiry."""
    raw_token = secrets.token_urlsafe(48)
    token_hash = hash_token(raw_token)
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return raw_token, token_hash, expires_at

def create_mfa_pending_token(user_id: str, email: str) -> str:
    """Short-lived 5-minute token issued during MFA challenge before 2nd factor verification."""
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.MFA_TEMP_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "email": email,
        "type": "mfa_pending",
        "exp": expire,
        "iat": datetime.datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# ===================== TWO-FACTOR AUTHENTICATION (TOTP & BACKUP CODES) =====================

def generate_totp_secret() -> str:
    return pyotp.random_base32()

def get_totp_uri(secret: str, email: str) -> str:
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name="NyayaSaathi AI")

def generate_qr_code_data_uri(totp_uri: str) -> str:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=3,
    )
    qr.add_data(totp_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_b64}"

def verify_totp_code(secret: str, code: str) -> bool:
    if not secret or not code:
        return False
    totp = pyotp.TOTP(secret)
    # Validates current code with window of 1 interval (30s tolerance)
    return totp.verify(code.strip(), valid_window=1)

def generate_backup_codes(count: int = 10) -> Tuple[List[str], List[str]]:
    """
    Generates single-use backup recovery codes.
    Returns (raw_codes_for_user, hashed_codes_for_db).
    """
    raw_codes = []
    hashed_codes = []
    for _ in range(count):
        code = f"{secrets.token_hex(4)}-{secrets.token_hex(4)}".upper()
        raw_codes.append(code)
        hashed_codes.append(hash_token(code))
    return raw_codes, hashed_codes
