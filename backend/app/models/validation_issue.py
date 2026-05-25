import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class ValidationIssue(Base):
    __tablename__ = "validation_issues"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    emission_record_id = Column(String(36), ForeignKey("emission_records.id", ondelete="CASCADE"), nullable=False)
    issue_type = Column(String(50), nullable=False)  # "duplicate", "negative_value", "overlapping_cycle", etc.
    field = Column(String(50), nullable=True)        # The column/field name having issue
    message = Column(String(255), nullable=False)    # Explanatory message for analyst
    severity = Column(String(20), default="warning") # "warning" (flagged), "error" (failed ingestion/calculation)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    emission_record = relationship("NormalizedEmissionRecord", back_populates="validation_issues")
