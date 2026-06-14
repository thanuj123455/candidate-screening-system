import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.schemas import ReportResponse, QAPair
from app.database import get_db
from app.models import InterviewSession, Question
from app.models.session import SessionStatus
from app.services import get_or_generate_report, end_session

router = APIRouter(prefix="/report", tags=["Report"])


@router.get("/{session_id}", response_model=ReportResponse)
async def get_report(session_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.id == session_id)
        .options(
            selectinload(InterviewSession.candidate),
            selectinload(InterviewSession.questions).selectinload(Question.answer),
        )
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Auto-close if still active
    if session.status == SessionStatus.active:
        await end_session(db, session_id)

    report = await get_or_generate_report(db, session_id)

    qa_pairs = [
        QAPair(
            question=q.question_text,
            answer=q.answer.answer_text if q.answer else "(no answer)",
            quality_score=q.answer.quality_score if q.answer else None,
        )
        for q in session.questions
    ]

    return ReportResponse(
        report_id=report.id,
        session_id=session_id,
        role=session.selected_role,
        candidate_name=session.candidate.name,
        summary=report.summary,
        strengths=json.loads(report.strengths or "[]"),
        weaknesses=json.loads(report.weaknesses or "[]"),
        overall_score=report.overall_score,
        recommendation=report.recommendation or "Maybe",
        qa_pairs=qa_pairs,
        generated_at=report.generated_at,
    )
