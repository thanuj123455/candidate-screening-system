from app.rag.embeddings import embed_query
from app.rag.vector_store import query_collection
from app.resume_parser.schemas import ParsedResume
from app.utils.config import settings
from app.utils.logger import get_logger

log = get_logger(__name__)


def _build_search_query(resume: ParsedResume, role: str) -> str:
    """
    Combine resume signals and target role into a retrieval query.
    Prioritise the most discriminative terms.
    """
    terms: list[str] = []
    terms.extend(resume.programming_languages[:5])
    terms.extend(resume.frameworks[:5])
    terms.extend(resume.skills[:8])
    terms.append(role)
    return ", ".join(t for t in terms if t)


def retrieve_context(resume: ParsedResume, role: str, top_k: int | None = None) -> list[str]:
    k = top_k or settings.top_k_chunks
    query = _build_search_query(resume, role)
    log.debug(f"RAG query: {query!r}")
    embedding = embed_query(query)
    chunks = query_collection(role, embedding, top_k=k)
    log.info(f"Retrieved {len(chunks)} chunks for role '{role}'")
    return chunks
