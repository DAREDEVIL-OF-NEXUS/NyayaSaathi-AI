import os
import io
import pyotp
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.core.database import Base, engine, get_db
from backend.app.models.entities import (
    User, EmailVerificationToken, PasswordResetToken, MFAConfiguration, BackupCode
)

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def db_session():
    with Session(engine) as session:
        yield session

def test_full_auth_and_mfa_lifecycle(client: TestClient, db_session: Session):
    # 1. Sign Up
    email = "test.user@nyayasaathi.org"
    password = "StrongPassword123!"
    full_name = "Aditi Sharma"

    # Cleanup if previously existed
    user = db_session.query(User).filter(User.email == email).first()
    if user:
        db_session.delete(user)
        db_session.commit()

    signup_res = client.post("/api/v1/auth/signup", json={
        "email": email,
        "password": password,
        "full_name": full_name
    })
    assert signup_res.status_code == 201, signup_res.text
    signup_data = signup_res.json()
    assert signup_data["user"]["email"] == email
    user_id = signup_data["user"]["id"]

    # 2. Verify Email via token from DB
    verif_record = db_session.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == user_id
    ).first()
    assert verif_record is not None
    
    # We can activate directly or test verification endpoint with code/token
    # Since tokens are hashed, let's mark user verified for test continuity
    db_user = db_session.query(User).filter(User.id == user_id).first()
    db_user.is_verified = True
    db_session.commit()

    # 3. Sign In (Without MFA yet)
    signin_res = client.post("/api/v1/auth/signin", json={
        "email": email,
        "password": password
    })
    assert signin_res.status_code == 200, signin_res.text
    signin_data = signin_res.json()
    assert signin_data["mfa_required"] is False
    access_token = signin_data["access_token"]
    assert access_token is not None
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # 4. Check Current User
    me_res = client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email
    assert me_res.json()["mfa_enabled"] is False

    # 5. Setup TOTP MFA
    mfa_setup_res = client.post("/api/v1/auth/mfa/setup", headers=auth_headers)
    assert mfa_setup_res.status_code == 200
    mfa_setup_data = mfa_setup_res.json()
    totp_secret = mfa_setup_data["secret"]
    assert "otpauth://" in mfa_setup_data["provisioning_uri"]
    assert mfa_setup_data["qr_code_data_uri"].startswith("data:image/png;base64,")

    # Generate valid TOTP code
    totp = pyotp.TOTP(totp_secret)
    valid_code = totp.now()

    # 6. Verify MFA & Activate
    mfa_verify_res = client.post("/api/v1/auth/mfa/verify", headers=auth_headers, json={
        "secret": totp_secret,
        "code": valid_code
    })
    assert mfa_verify_res.status_code == 200
    mfa_verify_data = mfa_verify_res.json()
    backup_codes = mfa_verify_data["backup_codes"]
    assert len(backup_codes) == 10

    # 7. Sign in with MFA enabled -> Expect mfa_required=True
    signin_mfa_res = client.post("/api/v1/auth/signin", json={
        "email": email,
        "password": password
    })
    assert signin_mfa_res.status_code == 200
    signin_mfa_data = signin_mfa_res.json()
    assert signin_mfa_data["mfa_required"] is True
    mfa_temp_token = signin_mfa_data["mfa_temp_token"]
    assert mfa_temp_token is not None

    # 8. Complete MFA Challenge using TOTP
    challenge_res = client.post("/api/v1/auth/mfa/challenge", json={
        "mfa_temp_token": mfa_temp_token,
        "code": totp.now()
    })
    assert challenge_res.status_code == 200
    assert challenge_res.json()["access_token"] is not None

    # 9. Complete MFA Challenge using Backup Code
    # Request another MFA token
    signin_mfa_res2 = client.post("/api/v1/auth/signin", json={
        "email": email,
        "password": password
    })
    mfa_temp_token2 = signin_mfa_res2.json()["mfa_temp_token"]
    used_backup_code = backup_codes[0]

    backup_challenge_res = client.post("/api/v1/auth/mfa/challenge", json={
        "mfa_temp_token": mfa_temp_token2,
        "code": used_backup_code
    })
    assert backup_challenge_res.status_code == 200

    # 10. Attempt reuse of same backup code -> Must fail (401 Unauthorized or 400 Bad Request)
    signin_mfa_res3 = client.post("/api/v1/auth/signin", json={
        "email": email,
        "password": password
    })
    mfa_temp_token3 = signin_mfa_res3.json()["mfa_temp_token"]
    reuse_res = client.post("/api/v1/auth/mfa/challenge", json={
        "mfa_temp_token": mfa_temp_token3,
        "code": used_backup_code
    })
    assert reuse_res.status_code in (400, 401)


def test_cross_tenant_isolation(client: TestClient, db_session: Session):
    # Setup User A
    user_a_email = "tenant.a@nyayasaathi.org"
    user_b_email = "tenant.b@nyayasaathi.org"
    pwd = "SecureTenantPwd123!"

    for em in [user_a_email, user_b_email]:
        u = db_session.query(User).filter(User.email == em).first()
        if u:
            db_session.delete(u)
            db_session.commit()

    # Create User A
    client.post("/api/v1/auth/signup", json={"email": user_a_email, "password": pwd, "full_name": "Tenant A"})
    ua = db_session.query(User).filter(User.email == user_a_email).first()
    ua.is_verified = True
    db_session.commit()
    token_a = client.post("/api/v1/auth/signin", json={"email": user_a_email, "password": pwd}).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Create User B
    client.post("/api/v1/auth/signup", json={"email": user_b_email, "password": pwd, "full_name": "Tenant B"})
    ub = db_session.query(User).filter(User.email == user_b_email).first()
    ub.is_verified = True
    db_session.commit()
    token_b = client.post("/api/v1/auth/signin", json={"email": user_b_email, "password": pwd}).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 1. User A creates a complaint draft
    draft_res = client.post("/api/v1/complaints/draft", headers=headers_a, json={
        "complainant_name": "Tenant A User",
        "complainant_contact": "+91-9876543210",
        "complainant_address": "New Delhi",
        "opposite_party_name": "Defective Store",
        "opposite_party_address": "Mumbai",
        "transaction_amount": 15000.0,
        "transaction_date": "01-01-2024",
        "order_or_invoice_number": "INV-A-101",
        "facts_of_case": "Bought electronics that failed on arrival, refund denied.",
        "relief_sought": "Full refund of Rs 15,000."
    })
    assert draft_res.status_code == 200
    draft_id_a = draft_res.json()["id"]

    # User A can access draft
    assert client.get(f"/api/v1/complaints/{draft_id_a}", headers=headers_a).status_code == 200

    # User B CANNOT access User A's draft -> 403 Forbidden
    res_b_access = client.get(f"/api/v1/complaints/{draft_id_a}", headers=headers_b)
    assert res_b_access.status_code == 403, f"Expected 403, got {res_b_access.status_code}"

    # User B CANNOT export User A's complaint -> 403 Forbidden
    res_b_export = client.get(f"/api/v1/complaints/{draft_id_a}/export", headers=headers_b)
    assert res_b_export.status_code == 403

    # 2. User A uploads a valid PDF document
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\ntrailer\n<<\n>>\n%%EOF"
    upload_res = client.post(
        "/api/v1/documents/upload",
        headers=headers_a,
        files={"file": ("tenant_a_invoice.pdf", io.BytesIO(pdf_content), "application/pdf")},
        data={"document_type": "invoice"}
    )
    assert upload_res.status_code == 200
    doc_id_a = upload_res.json()["id"]

    # User A can get document details
    assert client.get(f"/api/v1/documents/{doc_id_a}", headers=headers_a).status_code == 200

    # User B CANNOT access User A's document details -> 403 Forbidden
    res_b_doc = client.get(f"/api/v1/documents/{doc_id_a}", headers=headers_b)
    assert res_b_doc.status_code == 403

    # User B CANNOT delete User A's document -> 403 Forbidden
    res_b_del = client.delete(f"/api/v1/documents/{doc_id_a}", headers=headers_b)
    assert res_b_del.status_code == 403

    # 3. Document Upload Security Checks
    # Non-PDF rejection (magic bytes check)
    fake_pdf = b"This is not a real PDF file despite name"
    fake_res = client.post(
        "/api/v1/documents/upload",
        headers=headers_a,
        files={"file": ("malicious.pdf", io.BytesIO(fake_pdf), "application/pdf")},
        data={"document_type": "invoice"}
    )
    assert fake_res.status_code == 400
    assert "Invalid file content" in fake_res.json()["detail"] or "PDF" in fake_res.json()["detail"]


def test_database_alembic_migrations():
    import alembic.config
    from alembic import command
    alembic_cfg = alembic.config.Config("alembic.ini")
    
    # Verify current revision can be inspected or upgraded cleanly
    try:
        command.current(alembic_cfg)
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        pytest.fail(f"Alembic migration failed: {e}")

