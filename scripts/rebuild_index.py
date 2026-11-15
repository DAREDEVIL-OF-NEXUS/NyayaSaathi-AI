import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.ingest_data import run_ingestion

if __name__ == "__main__":
    print("[Rebuild Index] Initiating full index reconstruction from data/raw/...")
    run_ingestion(force_rebuild=True)
