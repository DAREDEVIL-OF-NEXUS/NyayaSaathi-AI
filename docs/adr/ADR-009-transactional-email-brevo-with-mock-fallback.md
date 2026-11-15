# ADR-009: Transactional Email Infrastructure via Brevo with Mock Fallback

## Status
Accepted

## Context
Transactional notifications are required for 6-digit email verification OTPs, password reset links, security alerts on login from new devices, and MFA enablement confirmations. However, in local offline development and automated CI testing environments, external SMTP or API connections may be unavailable or cost-prohibitive.

## Decision
Implement a layered email service architecture with Brevo (Sendinblue) REST API v3:
1. `BrevoEmailService` using `httpx` asynchronous client calling `https://api.brevo.com/v3/smtp/email` with header `api-key`.
2. Responsive HTML email templates with plain-text fallback, legal disclaimers, and clear CTA buttons.
3. Automated fallback to `MockEmailService` whenever `BREVO_API_KEY` is absent or set to development placeholders:
   - Logs formatted simulation payloads to stdout for manual OTP copy/paste during development.
   - Prevents CI pipeline breakage and enables zero-cost testing.

## Consequences
- **Positive:** Reliable, high-deliverability transactional emails in production.
- **Positive:** Frictionless local developer experience without requiring live API keys.
