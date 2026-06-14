"""
Knowledge base ingestion.

Run once (or when new PDFs are added):
    python -m app.rag.ingestion
"""
import hashlib
from pathlib import Path
from typing import Iterator

import pdfplumber

from app.rag.embeddings import embed_texts
from app.rag.vector_store import upsert_chunks
from app.utils.logger import get_logger

log = get_logger(__name__)

KNOWLEDGE_BASE_DIR = Path(__file__).resolve().parent.parent.parent / "knowledge_base"

# Map folder names inside knowledge_base/ to role identifiers
ROLE_FOLDER_MAP: dict[str, str] = {
    "ai_ml": "AI/ML Engineer",
    "backend": "Backend Engineer",
    "frontend": "Frontend Engineer",
    "fullstack": "Full Stack Engineer",
    "devops": "DevOps Engineer",
    "data_science": "Data Scientist",
}


def _chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> Iterator[str]:
    words = text.split()
    start = 0
    while start < len(words):
        end = start + chunk_size
        yield " ".join(words[start:end])
        start += chunk_size - overlap


def _stable_id(role: str, source: str, index: int) -> str:
    raw = f"{role}::{source}::{index}"
    return hashlib.md5(raw.encode()).hexdigest()


def ingest_role_documents(role_key: str) -> int:
    role = ROLE_FOLDER_MAP.get(role_key, role_key)
    folder = KNOWLEDGE_BASE_DIR / role_key
    if not folder.exists():
        log.warning(f"Knowledge base folder not found: {folder}")
        return 0

    all_chunks, all_ids = [], []
    for pdf_path in folder.glob("**/*.pdf"):
        log.info(f"Ingesting {pdf_path.name} for role '{role}'")
        with pdfplumber.open(str(pdf_path)) as pdf:
            full_text = "\n".join(p.extract_text() or "" for p in pdf.pages)
        for i, chunk in enumerate(_chunk_text(full_text)):
            all_chunks.append(chunk)
            all_ids.append(_stable_id(role, pdf_path.name, i))

    if not all_chunks:
        log.info(f"No chunks produced for role '{role}'")
        return 0

    # Batch embed to avoid OOM
    batch_size = 64
    embeddings: list[list[float]] = []
    for i in range(0, len(all_chunks), batch_size):
        embeddings.extend(embed_texts(all_chunks[i : i + batch_size]))

    upsert_chunks(role, all_chunks, embeddings, all_ids)
    log.info(f"Ingested {len(all_chunks)} chunks for role '{role}'")
    return len(all_chunks)


def ingest_all() -> None:
    for key in ROLE_FOLDER_MAP:
        ingest_role_documents(key)


if __name__ == "__main__":
    ingest_all()
