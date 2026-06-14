"""
Tests for the RAG retriever's query-building logic.
Embedding + ChromaDB calls are mocked to keep tests fast and offline.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.resume_parser.schemas import ParsedResume
from app.rag.retriever import _build_search_query, retrieve_context


def test_build_search_query_uses_top_terms():
    resume = ParsedResume(
        programming_languages=["Python", "Go"],
        frameworks=["FastAPI", "TensorFlow"],
        skills=["MLOps", "Docker"],
    )
    query = _build_search_query(resume, "AI/ML Engineer")
    assert "Python" in query
    assert "FastAPI" in query
    assert "AI/ML Engineer" in query


def test_build_search_query_empty_resume():
    resume = ParsedResume()
    query = _build_search_query(resume, "Backend Engineer")
    assert "Backend Engineer" in query


@patch("app.rag.retriever.query_collection", return_value=["chunk1", "chunk2"])
@patch("app.rag.retriever.embed_query", return_value=[0.1] * 384)
def test_retrieve_context_returns_chunks(mock_embed, mock_query):
    resume = ParsedResume(programming_languages=["Python"])
    chunks = retrieve_context(resume, "AI/ML Engineer", top_k=2)
    assert chunks == ["chunk1", "chunk2"]
    mock_embed.assert_called_once()
    mock_query.assert_called_once()
