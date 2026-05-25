import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class RawRecord(Base):
    __tablename__ = "raw_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    raw_upload_id = Column(String(36), ForeignKey("raw_uploads.id", ondelete="CASCADE"), nullable=False)
    row_index = Column(Integer, nullable=False)  # Row number in source file/payload
    raw_payload = Column(JSON, nullable=False)   # Store complete raw row as key-value
    status = Column(String(50), default="pending")  # "pending", "processed", "failed"
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    upload = relationship("RawUpload", back_populates="raw_records")
    emission_record = relationship("NormalizedEmissionRecord", back_populates="raw_record", uselist=False, cascade="all, delete-orphan")
