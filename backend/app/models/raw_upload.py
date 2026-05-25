import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class RawUpload(Base):
    __tablename__ = "raw_uploads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    datasource_id = Column(String(36), ForeignKey("datasources.id", ondelete="CASCADE"), nullable=False)
    uploader_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    filename = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)  # in bytes
    status = Column(String(50), default="pending")  # "pending", "processed", "failed"
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="uploads")
    datasource = relationship("DataSource", back_populates="uploads")
    uploader = relationship("User", back_populates="uploads")
    raw_records = relationship("RawRecord", back_populates="upload", cascade="all, delete-orphan")
