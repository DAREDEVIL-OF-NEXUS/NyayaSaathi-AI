# ADR-010: Multi-Tenant Data Isolation & Secure Upload Sandboxing

## Status
Accepted

## Context
In a multi-tenant legal assistant, consumers upload invoices, warranty cards, credit card statements, and communication screenshots. Cross-tenant leakage of complaint drafts or uploaded documents constitutes a severe privacy and legal violation. Furthermore, arbitrary file uploads introduce security risks (malware, path traversal).

## Decision
Enforce multi-tenant data isolation and upload sandboxing:
1. **Tenant Ownership Validation:**
   - Every `Conversation`, `ComplaintDraft`, and `DocumentUpload` entity stores `user_id` foreign key referencing `users.id`.
   - All retrieval and modification endpoints (`GET /complaints/{id}`, `GET /documents/{id}`, `DELETE /documents/{id}`, `GET /chat/history/{id}`) verify `entity.user_id == current_user.id`. Violations raise `403 Forbidden`.
2. **Magic Byte Verification:**
   - Ingestion validates true file format via magic byte inspection (`%PDF` header bytes `b"%PDF"`). Discrepancies between file extension and content are rejected (`400 Bad Request`).
3. **Path Traversal & Storage Sandboxing:**
   - Uploaded files are stripped of directory traversal sequences (`..`, `/`, `\`) using `os.path.basename`.
   - Files are stored in per-user sandboxes (`data/uploads/<user_id>/<sanitized_filename>`).
   - File size is capped at 10 MB.

## Consequences
- **Positive:** Complete cross-tenant privacy guaranteed by automated integration test suite.
- **Positive:** Immune to file extension spoofing and path traversal attacks.
