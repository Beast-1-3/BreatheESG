import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)         # "upload_data", "approve_record", "reject_record", "comment_record", etc.
    target_type = Column(String(50), nullable=False)      # "raw_upload", "emission_record", "user", etc.
    target_id = Column(String(36), nullable=False)        # ID of the target resource
    before_state = Column(JSON, nullable=True)            # State before change
    after_state = Column(JSON, nullable=True)             # State after change
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
