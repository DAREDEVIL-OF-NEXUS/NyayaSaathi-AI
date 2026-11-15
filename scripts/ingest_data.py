import sys
import os
import json
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.core.config import settings
from backend.app.services.rag.extraction import DocumentExtractor, ExtractedDocument
from backend.app.services.rag.chunking import LegalChunker, LegalChunk
from backend.app.services.rag.embeddings import get_embedding_service
from backend.app.services.graph.builder import LegalGraphBuilder
from backend.app.services.graph.engine import get_graph_engine
from backend.app.services.rag.retrieval import QdrantVectorStore, BM25Retriever

STATE_FILE = Path("data/processed/ingested_state.json")
MANIFEST_FILE = Path("data/manifest/sources.json")

def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def load_manifest() -> Dict[str, Any]:
    if not MANIFEST_FILE.exists():
        return {"sources": []}
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_ingested_state() -> Dict[str, str]:
    if not STATE_FILE.exists():
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_ingested_state(state: Dict[str, str]):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

def run_ingestion(force_rebuild: bool = False):
    print("================================================================================")
    print("NyayaSaathi AI — Legal Knowledge Base & Graph Ingestion Pipeline")
    print("================================================================================")

    manifest_data = load_manifest()
    sources_meta = {s.get("relative_path", ""): s for s in manifest_data.get("sources", [])}
    # Also index by filename
    sources_by_fname = {Path(s.get("relative_path", "")).name: s for s in manifest_data.get("sources", [])}

    state = {} if force_rebuild else load_ingested_state()

    raw_base = Path(settings.RAW_DATA_DIR)
    supported_exts = {".pdf", ".html", ".htm", ".txt", ".md"}

    files_to_process = []
    for root, _, files in os.walk(raw_base):
        for f in files:
            fpath = Path(root) / f
            if fpath.suffix.lower() in supported_exts:
                files_to_process.append(fpath)

    print(f"Discovered {len(files_to_process)} raw source files across categories.")

    all_parent_chunks: List[LegalChunk] = []
    all_child_chunks: List[LegalChunk] = []
    processed_count = 0

    chunker = LegalChunker(
        target_chunk_tokens=settings.CHUNK_SIZE,
        max_chunk_tokens=settings.MAX_CHUNK_SIZE,
        overlap_tokens=settings.CHUNK_OVERLAP
    )

    for fpath in files_to_process:
        rel_str = str(fpath.relative_to(raw_base)).replace("\\", "/")
        current_hash = compute_sha256(fpath)

        if not force_rebuild and state.get(rel_str) == current_hash:
            print(f"[SKIP] Unchanged: {rel_str} (SHA256: {current_hash[:10]}...)")
            continue

        print(f"\n--> Ingesting: {rel_str} ({fpath.stat().st_size} bytes)")

        # Resolve metadata from manifest
        meta = sources_meta.get(rel_str) or sources_by_fname.get(fpath.name, {})
        category = fpath.parent.name if fpath.parent.name != "raw" else "unclassified"
        combined_meta = {
            **meta,
            "category": category,
            "document_id": meta.get("document_id", fpath.stem),
            "title": meta.get("title", fpath.stem),
            "verification_status": meta.get("verification_status", "unverified"),
            "is_authoritative_for_rag": meta.get("is_authoritative_for_rag", False)
        }

        # 1. Document Extraction
        extracted_doc = DocumentExtractor.extract(fpath, combined_meta)
        print(f"    Extracted {len(extracted_doc.pages)} pages / {len(extracted_doc.text)} characters.")

        # 2. Structural Legal Chunking
        parents, children = chunker.chunk_document(extracted_doc)
        print(f"    Generated {len(parents)} Parent Provisions and {len(children)} Child Chunks.")

        all_parent_chunks.extend(parents)
        all_child_chunks.extend(children)
        state[rel_str] = current_hash
        processed_count += 1

    if not all_child_chunks and not force_rebuild:
        print("\nAll documents are already indexed and up-to-date. Ingestion complete.")
        return

    # If force_rebuild or new chunks found, update indices
    print(f"\nTotal active child chunks to index: {len(all_child_chunks)}")

    # 3. Dense Vector Embeddings & Qdrant Upsert
    if all_child_chunks:
        emb_service = get_embedding_service()
        print(f"Generating multilingual-e5 embeddings for {len(all_child_chunks)} chunks...")
        texts_to_embed = [c.text for c in all_child_chunks]
        embeddings = emb_service.embed_passages(texts_to_embed, batch_size=32)

        vector_store = QdrantVectorStore()
        vector_store.upsert_chunks(all_child_chunks, embeddings)

        # 4. BM25 Lexical Index
        bm25_retriever = BM25Retriever()
        bm25_retriever.build_index(all_child_chunks)

        # 5. Legal Knowledge Graph Construction
        print("Extracting legal entities and statutory cross-reference relationships...")
        entities, relationships = LegalGraphBuilder.extract_from_chunks(all_parent_chunks, all_child_chunks)
        print(f"Extracted {len(entities)} Legal Entities and {len(relationships)} Relationships.")

        graph_engine = get_graph_engine()
        graph_engine.sync_to_db(entities, relationships)

    save_ingested_state(state)
    print("\n================================================================================")
    print(f"Ingestion successfully finished. Processed {processed_count} documents.")
    print("================================================================================")

if __name__ == "__main__":
    force = "--force" in sys.argv
    run_ingestion(force_rebuild=force)
