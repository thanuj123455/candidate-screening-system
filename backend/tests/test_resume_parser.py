"""
Basic smoke tests for resume parser helpers.
Run with: pytest tests/
"""
import pytest
from app.resume_parser.schemas import ParsedResume


def test_to_summary_empty():
    r = ParsedResume()
    assert r.to_summary() == ""


def test_to_summary_populated():
    r = ParsedResume(
        name="Jane Smith",
        education="B.Tech AI, IIT 2023",
        programming_languages=["Python", "Go"],
        frameworks=["FastAPI"],
        skills=["Machine Learning"],
        projects=["Forest Fire Detection"],
    )
    summary = r.to_summary()
    assert "Jane Smith" in summary
    assert "Python" in summary
    assert "FastAPI" in summary
    assert "Forest Fire Detection" in summary


def test_parsed_resume_defaults():
    r = ParsedResume()
    assert r.skills == []
    assert r.frameworks == []
    assert r.raw_text == ""
