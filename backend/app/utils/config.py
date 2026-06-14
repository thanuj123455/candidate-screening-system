from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "AI Candidate Screening System"
    debug: bool = False
    api_prefix: str = "/api/v1"
    allowed_origins: list[str] = ["http://localhost:3000"]

    # PostgreSQL — use asyncpg driver
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/candidate_screening"

    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_collection_prefix: str = "role_kb"

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"

    # LLM — Groq (OpenAI-compatible)
    llm_api_key: str = ""
    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1024

    # Interview settings
    questions_per_session: int = 8
    top_k_chunks: int = 5
    upload_dir: str = "uploads"

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
