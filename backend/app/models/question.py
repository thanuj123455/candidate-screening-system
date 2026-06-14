from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.database.base import Base


class DifficultyLevel(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    source_context = Column(Text, nullable=True)  # RAG chunk used to generate this question
    topic_area = Column(String(256), nullable=True)
    difficulty = Column(SAEnum(DifficultyLevel), default=DifficultyLevel.medium)
    order_index = Column(Integer, nullable=False, default=0)
    is_follow_up = Column(String(1), default="0")  # "1" if follow-up to previous

    session = relationship("InterviewSession", back_populates="questions")
    answer = relationship("Answer", back_populates="question", uselist=False, cascade="all, delete-orphan")
