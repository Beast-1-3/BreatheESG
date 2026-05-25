import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class DataSource(Base):
    __tablename__ = "datasources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    source_type = Column(String(50), nullable=False)  # "sap", "utility", "travel"
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    connection_config = Column(JSON, nullable=True)  # Store API keys or config metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="datasources")
    uploads = relationship("RawUpload", back_populates="datasource", cascade="all, delete-orphan")
