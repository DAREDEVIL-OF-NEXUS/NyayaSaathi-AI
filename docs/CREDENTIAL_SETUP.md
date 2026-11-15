# NyayaSaathi AI — Credential Setup & Security Audit Guide

This document provides instructions for obtaining, configuring, and verifying all production and development credentials for **NyayaSaathi AI (न्यायसाथी AI)**.

---

## 1. Credentials Architecture & Official Portals

NyayaSaathi AI relies on isolated services for retrieval, generation, transactional notifications, and authentication:

| Service / Credential | Purpose | Official Portal Link | Format / Example |
| :--- | :--- | :--- | :--- |
| **Google Gemini API** (`GOOGLE_API_KEY`) | Primary LLM provider for hybrid CRAG generation, structured analysis, and complaint drafting | [Google AI Studio](https://aistudio.google.com/) | Starts with `AIza...` |
| **OpenRouter API** (`OPENROUTER_API_KEY`) | Automatic fallback provider when Gemini rate limits or capacity errors occur | [OpenRouter Keys](https://openrouter.ai/keys) | Starts with `sk-or-v1-...` |
| **Brevo API Key** (`BREVO_API_KEY`) | Transactional email provider for 6-digit OTP verification, password resets, and MFA recovery | [Brevo (Sendinblue) API Settings](https://app.brevo.com/settings/keys/api) | Starts with `xkeysib-...` |
| **Application Secret** (`SECRET_KEY`) | High-entropy cryptographic secret for signing HS256 JWT access and session tokens | Generated automatically by CLI | 32+ character Base64/URL-safe string |
| **PostgreSQL Credentials** (`POSTGRES_PASSWORD`) | Relational database authentication for users, sessions, MFA, complaints, and audit logs | Generated automatically or custom | Alphanumeric password |
| **Qdrant Vector DB** (`QDRANT_HOST`, `QDRANT_PORT`) | Isolated vector database storing official Indian legal chunks & embeddings | Local/Docker or Qdrant Cloud | `localhost:6333` |

---

## 2. Interactive Setup CLI

An interactive CLI script is provided in [`scripts/setup_credentials.py`](file:///C:/Users/Lakshay/OneDrive/Desktop/PROJECTS/NyayaSathi-AI/scripts/setup_credentials.py) to configure your `.env` file safely with masked input.

### Running Setup

```bash
uv run python scripts/setup_credentials.py
```

### CLI Features:
1. **Masked Inputs**: API keys and passwords are masked using `getpass` to prevent screen exposure.
2. **Preservation of Existing Values**: Hitting `[Enter]` retains currently configured values.
3. **Automatic Cryptographic Key Generation**: Generates 256-bit cryptographically secure strings for `SECRET_KEY` and `POSTGRES_PASSWORD` using Python's `secrets` module.
4. **Mock Email Fallback**: If `BREVO_API_KEY` is not provided, the platform automatically engages `MockEmailService`, which logs simulated verification and reset emails directly to standard output without failing.

---

## 3. Auditing Environment Health (`--check`)

To inspect environment health and credential validity without leaking secret values:

```bash
uv run python scripts/setup_credentials.py --check
```

Example audit output:
```text
=======================================================
   NyayaSaathi AI — Credential & Environment Audit     
=======================================================

[1] Security & Auth:
  ✅ SECRET_KEY: Set securely (53 chars)

[2] LLM Providers:
  ✅ GOOGLE_API_KEY: Configured (AIza...9Q1z)
  ℹ️  OPENROUTER_API_KEY: Set (sk-o...a3d1)

[3] Transactional Email (Brevo):
  ✅ BREVO_API_KEY: Configured (xkey...4e2a)

[4] Data & Storage:
  ℹ️  DATABASE_URL: sqlite:///./data/nyayasaathi.db
  ℹ️  QDRANT_HOST: localhost:6333

-------------------------------------------------------
Status: System environment ready.
-------------------------------------------------------
```

---

## 4. Production Security Principles

1. **Zero Secret Commits**:
   `.env` is strictly ignored in `.gitignore`. Never commit `.env` or paste actual API keys in Git history or issue trackers.
2. **Docker Isolation**:
   In `docker-compose.yml`, PostgreSQL and Qdrant communicate over the internal Docker network `nyayasaathi_internal` and are not exposed directly to the public host.
3. **Key Rotation**:
   To rotate API keys or regenerate `SECRET_KEY`:
   1. Update `.env` via `python scripts/setup_credentials.py`.
   2. Restart containers: `docker compose restart backend`.
   3. Note: Rotating `SECRET_KEY` invalidates active user sessions gracefully, requiring users to log in again.
