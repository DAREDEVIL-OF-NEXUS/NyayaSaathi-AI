from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class BaseEmailService(ABC):
    """
    Abstract interface for transactional email delivery.
    """

    @abstractmethod
    async def send_verification_email(
        self,
        to_email: str,
        user_name: str,
        code: str,
        verification_url: str
    ) -> bool:
        pass

    @abstractmethod
    async def send_password_reset_email(
        self,
        to_email: str,
        user_name: str,
        reset_url: str
    ) -> bool:
        pass

    @abstractmethod
    async def send_security_alert(
        self,
        to_email: str,
        user_name: str,
        alert_type: str,
        details: str
    ) -> bool:
        pass

    @abstractmethod
    async def send_mfa_otp(
        self,
        to_email: str,
        user_name: str,
        otp: str
    ) -> bool:
        pass
