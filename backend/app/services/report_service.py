import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.interview import generate_report
from app.models import InterviewSession, Report, Candidate, Question
from app.models.answer import Answer
from app.resume_parser.schemas import ParsedResume
from app.utils.logger import get_logger

log = get_logger(__name__)


async def get_or_generate_report(db: AsyncSession, session_id: UUID) -> Report:
    # Check if report already exists
    result = await db.execute(select(Report).where(Report.session_id == session_id))
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    # Load session with questions + answers
    s_result = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.id == session_id)
        .options(
            selectinload(InterviewSession.questions).selectinload(Question.answer),
            selectinload(InterviewSession.candidate),
        )
    )
    session = s_result.scalar_one()

    parsed_resume = ParsedResume.model_validate_json(session.candidate.parsed_resume or "{}")

    qa_pairs = [
        {"question": q.question_text, "answer": q.answer.answer_text if q.answer else "(no answer)"}
        for q in session.questions
    ]

    report_data = await generate_report(
        role=session.selected_role,
        resume=parsed_resume,
        qa_pairs=qa_pairs,
    )

    # Persist per-question scores back to answer rows
    for i, score_item in enumerate(report_data.get("per_question_scores", [])):
        if i < len(session.questions) and session.questions[i].answer:
            session.questions[i].answer.quality_score = score_item.get("score", 0) / 10.0

    report = Report(
        session_id=session_id,
        summary=report_data.get("summary", ""),
        strengths=json.dumps(report_data.get("strengths", [])),
        weaknesses=json.dumps(report_data.get("weaknesses", [])),
        overall_score=report_data.get("overall_score"),
        recommendation=report_data.get("recommendation", "Maybe"),
    )
    db.add(report)
    await db.flush()
    await db.refresh(report)
    log.info(f"Generated report for session {session_id}")
    return report
