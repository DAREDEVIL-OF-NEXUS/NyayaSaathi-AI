"""NyayaSaathi AI — Interactive Credential Setup & Validation CLI.

Allows secure, interactive configuration of production and development credentials:
- Google Gemini API Key
- OpenRouter API Key (Fallback)
- Brevo (Sendinblue) Transactional Email API Key
- Cryptographic SECRET_KEY and JWT salts
- PostgreSQL Database credentials
- Qdrant Vector Store configuration

Provides a non-destructive update mechanism and a --check mode for security audits.
"""

import os
import sys
import argparse
import getpass
import secrets
from pathlib import Path
from typing import Dict, Optional

ENV_PATH = Path(".env")
ENV_EXAMPLE_PATH = Path(".env.example")

KEY_PORTALS = {
    "GOOGLE_API_KEY": "https://aistudio.google.com/",
    "OPENROUTER_API_KEY": "https://openrouter.ai/keys",
    "BREVO_API_KEY": "https://app.brevo.com/settings/keys/api",
}

def load_existing_env(filepath: Path) -> Dict[str, str]:
    env_vars = {}
    if not filepath.exists():
        return env_vars
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                env_vars[key.strip()] = val.strip().strip("'\"")
    return env_vars

def write_env_file(filepath: Path, env_vars: Dict[str, str]):
    lines = [
        "# =====================================================================",
        "# NyayaSaathi AI — Production Environment Configuration",
        "# =====================================================================",
        "",
        "# Application",
        f"APP_ENV={env_vars.get('APP_ENV', 'development')}",
        f"LOG_LEVEL={env_vars.get('LOG_LEVEL', 'INFO')}",
        f"SECRET_KEY={env_vars.get('SECRET_KEY', secrets.token_urlsafe(32))}",
        f"BACKEND_CORS_ORIGINS={env_vars.get('BACKEND_CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000')}",
        "",
        "# Database (PostgreSQL / SQLite)",
        f"DATABASE_URL={env_vars.get('DATABASE_URL', 'sqlite:///./nyayasaathi.db')}",
        f"POSTGRES_USER={env_vars.get('POSTGRES_USER', 'nyayasaathi_user')}",
        f"POSTGRES_PASSWORD={env_vars.get('POSTGRES_PASSWORD', secrets.token_urlsafe(16))}",
        f"POSTGRES_DB={env_vars.get('POSTGRES_DB', 'nyayasaathi_db')}",
        f"POSTGRES_PORT={env_vars.get('POSTGRES_PORT', '5432')}",
        "",
        "# Vector Store (Qdrant)",
        f"QDRANT_HOST={env_vars.get('QDRANT_HOST', 'localhost')}",
        f"QDRANT_PORT={env_vars.get('QDRANT_PORT', '6333')}",
        f"QDRANT_COLLECTION={env_vars.get('QDRANT_COLLECTION', 'legal_chunks')}",
        "",
        "# LLM Providers",
        f"GOOGLE_API_KEY={env_vars.get('GOOGLE_API_KEY', '')}",
        f"GEMINI_MODEL={env_vars.get('GEMINI_MODEL', 'gemini-1.5-pro')}",
        f"OPENROUTER_API_KEY={env_vars.get('OPENROUTER_API_KEY', '')}",
        f"OPENROUTER_MODEL={env_vars.get('OPENROUTER_MODEL', 'meta-llama/llama-3.1-70b-instruct')}",
        "",
        "# Email Service (Brevo / Mock Fallback)",
        f"BREVO_API_KEY={env_vars.get('BREVO_API_KEY', '')}",
        f"BREVO_SENDER_EMAIL={env_vars.get('BREVO_SENDER_EMAIL', 'noreply@nyayasaathi.org')}",
        f"BREVO_SENDER_NAME={env_vars.get('BREVO_SENDER_NAME', 'NyayaSaathi AI')}",
        "",
        "# Embedding",
        f"EMBEDDING_MODEL_NAME={env_vars.get('EMBEDDING_MODEL_NAME', 'intfloat/multilingual-e5-small')}",
        "",
    ]
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def mask_val(val: Optional[str]) -> str:
    if not val:
        return "[NOT SET]"
    if len(val) <= 8:
        return "****"
    return f"{val[:4]}...{val[-4:]}"

def run_check():
    print("\n=======================================================")
    print("   NyayaSaathi AI — Credential & Environment Audit     ")
    print("=======================================================\n")
    if not ENV_PATH.exists():
        print(f"❌ Error: {ENV_PATH} not found. Run setup without --check to configure.")
        sys.exit(1)

    env = load_existing_env(ENV_PATH)
    all_ok = True

    # Check Core Keys
    print("[1] Security & Auth:")
    sec_key = env.get("SECRET_KEY")
    if sec_key and len(sec_key) >= 32 and sec_key != "supersecretkey_replace_in_production":
        print(f"  ✅ SECRET_KEY: Set securely ({len(sec_key)} chars)")
    else:
        print("  ⚠️  SECRET_KEY: Insecure or using default template value")
        all_ok = False

    print("\n[2] LLM Providers:")
    gkey = env.get("GOOGLE_API_KEY")
    if gkey and gkey.startswith("AIza"):
        print(f"  ✅ GOOGLE_API_KEY: Configured ({mask_val(gkey)})")
    elif gkey:
        print(f"  ⚠️  GOOGLE_API_KEY: Set ({mask_val(gkey)}), check AI Studio format")
    else:
        print(f"  ❌ GOOGLE_API_KEY: Missing! Get key at {KEY_PORTALS['GOOGLE_API_KEY']}")
        all_ok = False

    okey = env.get("OPENROUTER_API_KEY")
    if okey and okey.startswith("sk-or-"):
        print(f"  ✅ OPENROUTER_API_KEY: Configured ({mask_val(okey)})")
    elif okey:
        print(f"  ℹ️  OPENROUTER_API_KEY: Set ({mask_val(okey)})")
    else:
        print(f"  ℹ️  OPENROUTER_API_KEY: Not set (optional fallback)")

    print("\n[3] Transactional Email (Brevo):")
    bkey = env.get("BREVO_API_KEY")
    if bkey and bkey.startswith("xkeysib-"):
        print(f"  ✅ BREVO_API_KEY: Configured ({mask_val(bkey)})")
    elif bkey:
        print(f"  ⚠️  BREVO_API_KEY: Set ({mask_val(bkey)})")
    else:
        print(f"  ℹ️  BREVO_API_KEY: Not set (MockEmailService fallback active)")

    print("\n[4] Data & Storage:")
    db_url = env.get("DATABASE_URL", "sqlite:///./nyayasaathi.db")
    print(f"  ℹ️  DATABASE_URL: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    print(f"  ℹ️  QDRANT_HOST: {env.get('QDRANT_HOST', 'localhost')}:{env.get('QDRANT_PORT', '6333')}")

    print("\n-------------------------------------------------------")
    if all_ok:
        print("Status: System environment ready.")
    else:
        print("Status: Some credentials require attention.")
    print("-------------------------------------------------------\n")

def run_interactive():
    print("\n=======================================================")
    print("      NyayaSaathi AI — Interactive Credential Setup     ")
    print("=======================================================\n")
    print("This utility configures your local environment (.env) safely.")
    print("Existing values will be preserved if you press [Enter].\n")

    env = load_existing_env(ENV_PATH)

    # 1. Google Gemini
    print(f"[1] Google Gemini API Key")
    print(f"    Portal: {KEY_PORTALS['GOOGLE_API_KEY']}")
    current_g = env.get("GOOGLE_API_KEY", "")
    prompt_g = f"    Enter key [{mask_val(current_g)}]: "
    new_g = getpass.getpass(prompt_g).strip()
    if new_g:
        env["GOOGLE_API_KEY"] = new_g

    # 2. OpenRouter API Key
    print(f"\n[2] OpenRouter API Key (Optional Fallback)")
    print(f"    Portal: {KEY_PORTALS['OPENROUTER_API_KEY']}")
    current_o = env.get("OPENROUTER_API_KEY", "")
    prompt_o = f"    Enter key [{mask_val(current_o)}]: "
    new_o = getpass.getpass(prompt_o).strip()
    if new_o:
        env["OPENROUTER_API_KEY"] = new_o

    # 3. Brevo Transactional Email
    print(f"\n[3] Brevo (Sendinblue) API Key (Transactional Email)")
    print(f"    Portal: {KEY_PORTALS['BREVO_API_KEY']}")
    current_b = env.get("BREVO_API_KEY", "")
    prompt_b = f"    Enter key [{mask_val(current_b)}]: "
    new_b = getpass.getpass(prompt_b).strip()
    if new_b:
        env["BREVO_API_KEY"] = new_b

    # Brevo Sender
    current_sender = env.get("BREVO_SENDER_EMAIL", "noreply@nyayasaathi.org")
    new_sender = input(f"    Sender Email [{current_sender}]: ").strip()
    if new_sender:
        env["BREVO_SENDER_EMAIL"] = new_sender

    # 4. Generate Security Keys if missing
    if not env.get("SECRET_KEY") or env.get("SECRET_KEY") == "supersecretkey_replace_in_production":
        env["SECRET_KEY"] = secrets.token_urlsafe(32)
        print("\n[4] Security: Generated strong random SECRET_KEY.")

    if not env.get("POSTGRES_PASSWORD") or env.get("POSTGRES_PASSWORD") == "password":
        env["POSTGRES_PASSWORD"] = secrets.token_urlsafe(16)
        print("    Database: Generated strong random POSTGRES_PASSWORD.")

    write_env_file(ENV_PATH, env)
    print(f"\n✅ Configuration saved successfully to {ENV_PATH.resolve()}.\n")
    run_check()

def main():
    parser = argparse.ArgumentParser(description="NyayaSaathi AI Credential Setup CLI")
    parser.add_argument("--check", action="store_true", help="Audit and validate configured credentials without modifying")
    args = parser.parse_args()

    if args.check:
        run_check()
    else:
        run_interactive()

if __name__ == "__main__":
    main()
