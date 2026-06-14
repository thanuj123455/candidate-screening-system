from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    StartInterviewRequest,
    StartInterviewResponse,
    QuestionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.database import get_db
from app.services import start_interview, get_next_question, submit_answer, end_session
from app.utils.config import settings

router = APIRouter(prefix="/interview", tags=["Interview"])

SUPPORTED_ROLES = [
    "AI/ML Engineer",
    "Backend Engineer",
    "Frontend Engineer",
    "Full Stack Engineer",
    "DevOps Engineer",
    "Data Scientist",
]


@router.post("/start", response_model=StartInterviewResponse)
async def start(body: StartInterviewRequest, db: AsyncSession = Depends(get_db)):
    if body.role not in SUPPORTED_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported role. Choose from: {', '.join(SUPPORTED_ROLES)}",
        )
    session = await start_interview(db, body.candidate_id, body.role)
    return StartInterviewResponse(
        session_id=session.id,
        candidate_id=session.candidate_id,
        role=session.selected_role,
        status=session.status.value,
    )


@router.get("/question/{session_id}", response_model=QuestionResponse)
async def get_question(session_id: UUID, db: AsyncSession = Depends(get_db)):
    question = await get_next_question(db, session_id)
    if question is None:
        raise HTTPException(status_code=404, detail="No more questions or session not active.")

    # Count answered questions in the session to determine progress
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models import InterviewSession, Question as QModel

    result = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.id == session_id)
        .options(selectinload(InterviewSession.questions).selectinload(QModel.answer))
    )
    session = result.scalar_one()
    answered = sum(1 for q in session.questions if q.answer is not None)
    is_last = (answered + 1) >= settings.questions_per_session

    return QuestionResponse(
        question_id=question.id,
        session_id=session_id,
        question_text=question.question_text,
        order_index=question.order_index,
        difficulty=question.difficulty.value,
        total_questions=settings.questions_per_session,
        is_last=is_last,
    )


@router.post("/answer", response_model=SubmitAnswerResponse)
async def answer(body: SubmitAnswerRequest, db: AsyncSession = Depends(get_db)):
    try:
        ans = await submit_answer(db, body.session_id, body.question_id, body.answer_text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return SubmitAnswerResponse(
        answer_id=ans.id,
        question_id=ans.question_id,
        submitted_at=ans.submitted_at,
    )


@router.post("/end/{session_id}")
async def end(session_id: UUID, db: AsyncSession = Depends(get_db)):
    session = await end_session(db, session_id)
    return {"session_id": session_id, "status": session.status.value}
