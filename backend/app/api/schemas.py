from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


# ── Resume ────────────────────────────────────────────────────────────────────

class ResumeUploadResponse(BaseModel):
    candidate_id: UUID
    name: str
    email: str
    parsed_data: dict


# ── Interview ─────────────────────────────────────────────────────────────────

class StartInterviewRequest(BaseModel):
    candidate_id: UUID
    role: str = Field(..., examples=["AI/ML Engineer", "Backend Engineer"])


class StartInterviewResponse(BaseModel):
    session_id: UUID
    candidate_id: UUID
    role: str
    status: str


class QuestionResponse(BaseModel):
    question_id: UUID
    session_id: UUID
    question_text: str
    order_index: int
    difficulty: str
    total_questions: int
    is_last: bool


class SubmitAnswerRequest(BaseModel):
    session_id: UUID
    question_id: UUID
    answer_text: str = Field(..., min_length=1, max_length=8000)


class SubmitAnswerResponse(BaseModel):
    answer_id: UUID
    question_id: UUID
    submitted_at: datetime


# ── Report ────────────────────────────────────────────────────────────────────

class QAPair(BaseModel):
    question: str
    answer: str
    quality_score: Optional[float] = None


class ReportResponse(BaseModel):
    report_id: UUID
    session_id: UUID
    role: str
    candidate_name: str
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    overall_score: Optional[float]
    recommendation: str
    qa_pairs: list[QAPair]
    generated_at: datetime
