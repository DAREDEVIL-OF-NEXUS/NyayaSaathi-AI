import logging
from typing import List, Dict, Any, Optional
from backend.app.core.config import settings
from .base import BaseEmailService
from .brevo import BrevoEmailService

logger = logging.getLogger(__name__)

class MockEmailService(BaseEmailService):
    """
    Mock Email Service for local development and offline unit testing.
    Records delivered messages in-memory.
    """

    def __init__(self):
        self.sent_emails: List[Dict[str, Any]] = []

    async def send_verification_email(
        self,
        to_email: str,
        user_name: str,
        code: str,
        verification_url: str
    ) -> bool:
        self.sent_emails.append({
            "type": "verification",
            "to_email": to_email,
            "user_name": user_name,
            "code": code,
            "verification_url": verification_url
        })
        logger.info(f"[MockEmailService] Verification email generated for {to_email}. Code: [REDACTED_OTP]")
        return True

    async def send_password_reset_email(
        self,
        to_email: str,
        user_name: str,
        reset_url: str
    ) -> bool:
        self.sent_emails.append({
            "type": "password_reset",
            "to_email": to_email,
            "user_name": user_name,
            "reset_url": reset_url
        })
        logger.info(f"[MockEmailService] Password reset email generated for {to_email}.")
        return True

    async def send_security_alert(
        self,
        to_email: str,
        user_name: str,
        alert_type: str,
        details: str
    ) -> bool:
        self.sent_emails.append({
            "type": "security_alert",
            "to_email": to_email,
            "user_name": user_name,
            "alert_type": alert_type,
            "details": details
        })
        logger.info(f"[MockEmailService] Security alert generated for {to_email}: {alert_type}")
        return True

    async def send_mfa_otp(
        self,
        to_email: str,
        user_name: str,
        otp: str
    ) -> bool:
        self.sent_emails.append({
            "type": "mfa_otp",
            "to_email": to_email,
            "user_name": user_name,
            "otp": otp
        })
        logger.info(f"[MockEmailService] MFA OTP generated for {to_email}.")
        return True


_global_email_service = None

def get_email_service() -> BaseEmailService:
    global _global_email_service
    if _global_email_service is None:
        if settings.BREVO_API_KEY and len(settings.BREVO_API_KEY) > 10 and not settings.BREVO_API_KEY.startswith("your_"):
            _global_email_service = BrevoEmailService()
        else:
            logger.info("[EmailService] Brevo API Key not configured. Initializing MockEmailService for offline/dev operation.")
            _global_email_service = MockEmailService()
    return _global_email_service
