import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class ReviewDecision(Base):
    __tablename__ = "review_decisions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    emission_record_id = Column(String(36), ForeignKey("emission_records.id", ondelete="CASCADE"), nullable=False)
    analyst_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(50), nullable=False)  # "approve", "reject", "comment"
    comment_text = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    emission_record = relationship("NormalizedEmissionRecord", back_populates="reviews")
    analyst = relationship("User", back_populates="reviews")
