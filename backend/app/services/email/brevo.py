import logging
import httpx
from typing import Optional, Dict, Any
from backend.app.core.config import settings
from .base import BaseEmailService
from .templates import (
    render_verification_email,
    render_password_reset_email,
    render_security_alert_email,
)

logger = logging.getLogger(__name__)

class BrevoEmailService(BaseEmailService):
    """
    Official Brevo (formerly Sendinblue) REST API v3 Transactional Email Integration.
    Uses 'api-key' header authentication with timeout and error handling.
    """

    BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

    def __init__(
        self,
        api_key: Optional[str] = None,
        sender_email: Optional[str] = None,
        sender_name: Optional[str] = None,
        timeout_seconds: float = 8.0
    ):
        self.api_key = api_key or settings.BREVO_API_KEY
        self.sender_email = sender_email or settings.BREVO_SENDER_EMAIL
        self.sender_name = sender_name or settings.BREVO_SENDER_NAME
        self.timeout = timeout_seconds

    def _is_configured(self) -> bool:
        if not self.api_key or "your_" in self.api_key.lower() or "change_me" in self.api_key.lower():
            return False
        return len(self.api_key) > 10

    async def _send_smtp_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> bool:
        if not self._is_configured():
            logger.warning("[BrevoEmailService] BREVO_API_KEY is not configured or is a placeholder.")
            return False

        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "sender": {
                "name": self.sender_name,
                "email": self.sender_email
            },
            "to": [
                {
                    "email": to_email,
                    "name": to_name
                }
            ],
            "subject": subject,
            "htmlContent": html_content,
            "textContent": text_content
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(self.BREVO_API_URL, headers=headers, json=payload)
                if res.status_code in [200, 201, 202]:
                    resp_data = res.json()
                    msg_id = resp_data.get("messageId", "unknown")
                    logger.info(f"[BrevoEmailService] Transactional email sent successfully to {to_email}. Brevo MsgId: {msg_id}")
                    return True
                else:
                    logger.error(
                        f"[BrevoEmailService] Failed to send email to {to_email}. "
                        f"Status: {res.status_code}, Body: {res.text}"
                    )
                    return False
        except httpx.TimeoutException:
            logger.error(f"[BrevoEmailService] Timeout while connecting to Brevo API for recipient {to_email}")
            return False
        except Exception as e:
            logger.error(f"[BrevoEmailService] Unexpected error sending email to {to_email}: {str(e)}")
            return False

    async def send_verification_email(
        self,
        to_email: str,
        user_name: str,
        code: str,
        verification_url: str
    ) -> bool:
        subject = "Verify your NyayaSaathi AI Account (Email Verification Code)"
        text_body, html_body = render_verification_email(user_name, code, verification_url)
        return await self._send_smtp_email(to_email, user_name, subject, html_body, text_body)

    async def send_password_reset_email(
        self,
        to_email: str,
        user_name: str,
        reset_url: str
    ) -> bool:
        subject = "Reset your NyayaSaathi AI Password"
        text_body, html_body = render_password_reset_email(user_name, reset_url)
        return await self._send_smtp_email(to_email, user_name, subject, html_body, text_body)

    async def send_security_alert(
        self,
        to_email: str,
        user_name: str,
        alert_type: str,
        details: str
    ) -> bool:
        subject = f"Security Alert: {alert_type} on your NyayaSaathi AI Account"
        text_body, html_body = render_security_alert_email(user_name, alert_type, details)
        return await self._send_smtp_email(to_email, user_name, subject, html_body, text_body)

    async def send_mfa_otp(
        self,
        to_email: str,
        user_name: str,
        otp: str
    ) -> bool:
        subject = "NyayaSaathi AI — Two-Factor Authentication Login Code"
        text_body = f"Hello {user_name},\n\nYour login code is: {otp}\n\nIt expires in 5 minutes."
        html_body = f"<p>Hello {user_name},</p><p>Your login code is: <strong>{otp}</strong></p><p>Expires in 5 minutes.</p>"
        return await self._send_smtp_email(to_email, user_name, subject, html_body, text_body)
