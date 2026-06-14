from functools import lru_cache
from sentence_transformers import SentenceTransformer
from app.utils.config import settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Singleton — loaded once, reused across requests."""
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    return model.encode(texts, convert_to_numpy=True).tolist()


def embed_query(query: str) -> list[float]:
    model = get_embedding_model()
    return model.encode([query], convert_to_numpy=True)[0].tolist()
