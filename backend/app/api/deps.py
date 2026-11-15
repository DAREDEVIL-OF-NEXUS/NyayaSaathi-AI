import datetime
from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import decode_token
from backend.app.models.entities import User, AuditLog

security_bearer = HTTPBearer(auto_error=False)

def log_audit_event(
    db: Session,
    action: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[dict] = None
):
    audit = AuditLog(
        user_id=user_id,
        action=action,
        ip_address=ip_address,
        details=details or {},
        created_at=datetime.datetime.utcnow()
    )
    db.add(audit)
    db.commit()

async def get_current_user(
    request: Request,
    token_bearer: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> User:
    token = None
    if token_bearer and token_bearer.credentials:
        token = token_bearer.credentials
    elif "access_token" in request.cookies:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Missing access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account.")

    return user

async def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email address not verified. Please verify your email to access this resource."
        )
    return current_user

async def get_optional_current_user(
    request: Request,
    token_bearer: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> Optional[User]:
    token = None
    if token_bearer and token_bearer.credentials:
        token = token_bearer.credentials
    elif "access_token" in request.cookies:
        token = request.cookies.get("access_token")

    if not token:
        return None

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        return None

    return user
