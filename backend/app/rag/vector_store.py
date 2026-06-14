"""
ChromaDB wrapper.

Each role gets its own collection, e.g. `role_kb_ai_ml_engineer`.
We use persistent local ChromaDB (no separate server needed for dev).
In production, swap to chromadb.HttpClient.
"""
from functools import lru_cache
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.utils.config import settings
from app.utils.logger import get_logger

log = get_logger(__name__)

_CHROMA_PERSIST_DIR = Path(__file__).resolve().parent.parent.parent / "chroma_db"


@lru_cache(maxsize=1)
def get_chroma_client() -> chromadb.PersistentClient:
    _CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(_CHROMA_PERSIST_DIR),
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def _collection_name(role: str) -> str:
    return f"{settings.chroma_collection_prefix}_{role.lower().replace(' ', '_').replace('/', '_')}"


def get_or_create_collection(role: str) -> chromadb.Collection:
    client = get_chroma_client()
    name = _collection_name(role)
    return client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})


def upsert_chunks(role: str, chunks: list[str], embeddings: list[list[float]], ids: list[str]) -> None:
    col = get_or_create_collection(role)
    col.upsert(documents=chunks, embeddings=embeddings, ids=ids)
    log.info(f"Upserted {len(chunks)} chunks into collection '{_collection_name(role)}'")


def query_collection(role: str, query_embedding: list[float], top_k: int = 5) -> list[str]:
    col = get_or_create_collection(role)
    results = col.query(query_embeddings=[query_embedding], n_results=top_k)
    docs = results.get("documents", [[]])[0]
    return docs
