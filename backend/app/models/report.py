from sqlalchemy import Column, Text, ForeignKey, DateTime, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone

from app.database.base import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, unique=True)
    summary = Column(Text, nullable=False)
    strengths = Column(Text, nullable=True)   # JSON list
    weaknesses = Column(Text, nullable=True)  # JSON list
    overall_score = Column(Float, nullable=True)  # 0–100
    recommendation = Column(String(64), nullable=True)  # "Hire" | "Maybe" | "Reject"
    generated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    session = relationship("InterviewSession", back_populates="report")
