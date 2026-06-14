import asyncio
import json
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.interview import generate_question, generate_follow_up
from app.models import Candidate, InterviewSession, Question, Answer
from app.models.session import SessionStatus
from app.models.question import DifficultyLevel
from app.rag import retrieve_context
from app.resume_parser.schemas import ParsedResume
from app.utils.config import settings
from app.utils.logger import get_logger

log = get_logger(__name__)


async def start_interview(db: AsyncSession, candidate_id: UUID, role: str) -> InterviewSession:
    session = InterviewSession(
        candidate_id=candidate_id,
        selected_role=role,
        status=SessionStatus.active,
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)
    log.info(f"Started interview session {session.id} for candidate {candidate_id}")
    return session


async def get_next_question(db: AsyncSession, session_id: UUID) -> Question | None:
    session = await _load_session(db, session_id)
    if session is None or session.status != SessionStatus.active:
        return None

    answered_count = sum(1 for q in session.questions if q.answer is not None)
    if answered_count >= settings.questions_per_session:
        return None

    # Return existing unanswered question if one was already generated
    for q in session.questions:
        if q.answer is None:
            return q

    # Generate a new question
    candidate = await _load_candidate(db, session.candidate_id)
    parsed_resume = ParsedResume.model_validate_json(candidate.parsed_resume or "{}")

    chunks = await asyncio.to_thread(retrieve_context, parsed_resume, session.selected_role)
    asked = [q.question_text for q in session.questions]

    q_text, context = await generate_question(
        role=session.selected_role,
        resume=parsed_resume,
        context_chunks=chunks,
        asked_questions=asked,
        question_index=len(session.questions),
    )

    difficulty_cycle = ["easy", "medium", "medium", "hard", "hard", "hard", "medium", "hard"]
    idx = len(session.questions)
    diff = difficulty_cycle[min(idx, len(difficulty_cycle) - 1)]

    question = Question(
        session_id=session_id,
        question_text=q_text,
        source_context=context,
        order_index=idx,
        difficulty=DifficultyLevel(diff),
    )
    db.add(question)
    await db.flush()
    await db.refresh(question)
    return question


async def submit_answer(
    db: AsyncSession,
    session_id: UUID,
    question_id: UUID,
    answer_text: str,
) -> Answer:
    question = await db.get(Question, question_id)
    if question is None or question.session_id != session_id:
        raise ValueError("Question not found for this session")

    answer = Answer(question_id=question_id, answer_text=answer_text)
    db.add(answer)
    await db.flush()
    await db.refresh(answer)
    return answer


async def end_session(db: AsyncSession, session_id: UUID) -> InterviewSession:
    session = await db.get(InterviewSession, session_id)
    session.status = SessionStatus.completed
    session.end_time = datetime.now(timezone.utc)
    await db.flush()
    return session


# ── helpers ──────────────────────────────────────────────────────────────────

async def _load_session(db: AsyncSession, session_id: UUID) -> InterviewSession | None:
    result = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.id == session_id)
        .options(selectinload(InterviewSession.questions).selectinload(Question.answer))
    )
    return result.scalar_one_or_none()


async def _load_candidate(db: AsyncSession, candidate_id: UUID) -> Candidate:
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    return result.scalar_one()
