# ADR-008: Multi-Factor Authentication (MFA) with RFC 6238 TOTP & Hashed Backup Codes

## Status
Accepted

## Context
Consumer grievance portals handle sensitive personal grievance data, transaction receipts, bank statements, and legal drafts. Strong authentication with second-factor verification is essential to prevent unauthorized access.

## Decision
Implement a zero-trust authentication architecture:
1. Passwords hashed using Bcrypt with 12 work rounds.
2. Two-Factor Authentication via standard RFC 6238 Time-based One-Time Password (TOTP):
   - Compatible with Google Authenticator, Microsoft Authenticator, Authy, and 1Password.
   - Base64 QR code and `otpauth://` provisioning URI generation.
3. 10 cryptographically random, single-use backup recovery codes:
   - Generated during MFA enrollment.
   - Stored in the database as SHA-256 hashes (`code_hash`), never in plaintext.
   - Burn-on-use: Marked `is_used = True` upon successful recovery sign-in.
4. Stateless JWT access tokens (15-minute lifetime) paired with revokable database-backed refresh tokens (7-day lifetime) and httpOnly cookies.

## Consequences
- **Positive:** Enterprise-grade account security without external identity provider vendor lock-in.
- **Positive:** Consumers retain access via backup codes even if their authenticator device is lost.
