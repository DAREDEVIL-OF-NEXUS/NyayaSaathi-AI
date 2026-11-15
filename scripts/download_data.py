import os
import sys
import json
import hashlib
import time
from pathlib import Path
import urllib.request
import urllib.error
import ssl

MANIFEST_PATH = Path("data/manifest/sources.json")
RAW_DATA_DIR = Path("data/raw")
REPORT_PATH = Path("data/manifest/MISSING_DOCUMENTS_REPORT.md")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def download_source(source: dict) -> tuple[bool, str, dict]:
    doc_id = source["document_id"]
    target_filename = source["target_filename"]
    dest_path = RAW_DATA_DIR / target_filename
    url = source.get("direct_download_url") or source.get("official_source_url")

    # If already downloaded and non-empty, check integrity
    if dest_path.exists() and dest_path.stat().st_size > 1024:
        sha256 = compute_sha256(dest_path)
        print(f"[{doc_id}] Already present: {dest_path.name} (SHA256: {sha256[:12]}..., Size: {dest_path.stat().st_size} bytes)")
        return True, "Already exists", {"sha256": sha256, "size": dest_path.stat().st_size}

    if not url:
        return False, "No download URL specified in manifest", {}

    print(f"[{doc_id}] Attempting download from: {url}")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
            status_code = response.getcode()
            if status_code != 200:
                return False, f"HTTP Status {status_code}", {}
            
            content = response.read()
            if len(content) < 512:
                return False, f"Downloaded content too small ({len(content)} bytes) - possibly block page or redirect", {}
            
            # Write to raw storage
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                f.write(content)
            
            sha256 = compute_sha256(dest_path)
            print(f"[{doc_id}] Successfully downloaded: {dest_path.name} ({len(content)} bytes, SHA256: {sha256[:12]}...)")
            return True, "Downloaded successfully", {"sha256": sha256, "size": len(content)}
    except Exception as e:
        return False, f"Download failed: {str(e)}", {}

def generate_missing_report(missing_sources: list[dict]):
    if not missing_sources:
        if REPORT_PATH.exists():
            REPORT_PATH.unlink()
        print("\nAll manifest documents are present and accounted for.")
        return

    lines = [
        "# Official Legal Knowledge Base — Missing Documents Report",
        "",
        f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
        "",
        "The following official Indian consumer protection documents could not be automatically downloaded",
        "due to government server downtime, strict captcha, or network policy restrictions.",
        "",
        "## Required Manual Download Action Plan",
        "",
    ]

    for item in missing_sources:
        doc = item["source"]
        reason = item["reason"]
        lines.extend([
            f"### Document: {doc['title']}",
            f"- **Document ID**: `{doc['document_id']}`",
            f"- **Failure Reason**: `{reason}`",
            f"- **Official Portal**: [{doc['official_source_url']}]({doc['official_source_url']})",
            f"- **Direct Download Link**: [{doc.get('direct_download_url', 'N/A')}]({doc.get('direct_download_url', 'N/A')})",
            f"- **Target Destination**: `data/raw/{doc['target_filename']}`",
            "- **Instructions**:",
            f"  1. Visit the portal link in your browser.",
            f"  2. Save the official document as `{doc['target_filename']}`.",
            f"  3. Place it in `data/raw/{doc['target_filename']}`.",
            "",
        ])

    lines.extend([
        "## Resuming Ingestion",
        "Once files are placed into `data/raw/`, re-run:",
        "```bash",
        "python scripts/download_data.py",
        "python scripts/ingest_data.py",
        "```"
    ])

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nReport generated at {REPORT_PATH}")

def main():
    if not MANIFEST_PATH.exists():
        print(f"Error: Manifest not found at {MANIFEST_PATH}")
        sys.exit(1)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    sources = manifest.get("sources", [])
    print(f"Checking {len(sources)} official source documents...")

    missing = []
    updated_sources = []

    for src in sources:
        success, msg, meta = download_source(src)
        if success:
            src_copy = dict(src)
            src_copy["sha256_hash"] = meta.get("sha256")
            src_copy["file_size_bytes"] = meta.get("size")
            src_copy["download_timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            updated_sources.append(src_copy)
        else:
            missing.append({"source": src, "reason": msg})
            updated_sources.append(src)

    # Update manifest with checksums
    manifest["sources"] = updated_sources
    manifest["last_download_run"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)

    generate_missing_report(missing)
    print("\nDownload execution completed.")

if __name__ == "__main__":
    main()
