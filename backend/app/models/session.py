from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime, timezone

from app.database.base import Base


class SessionStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    completed = "completed"
    aborted = "aborted"


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    selected_role = Column(String(128), nullable=False)
    status = Column(SAEnum(SessionStatus), default=SessionStatus.pending, nullable=False)
    start_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    end_time = Column(DateTime(timezone=True), nullable=True)
    current_question_index = Column(String(8), default="0")

    candidate = relationship("Candidate", back_populates="sessions")
    questions = relationship("Question", back_populates="session", cascade="all, delete-orphan", order_by="Question.order_index")
    report = relationship("Report", back_populates="session", uselist=False, cascade="all, delete-orphan")
