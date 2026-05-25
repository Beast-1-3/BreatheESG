import uuid
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class Organization(Base):
    __tablename__ = "organizations"

    # Use String for UUID representation to support both SQLite and PostgreSQL easily
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    datasources = relationship("DataSource", back_populates="organization", cascade="all, delete-orphan")
    uploads = relationship("RawUpload", back_populates="organization", cascade="all, delete-orphan")
    records = relationship("NormalizedEmissionRecord", back_populates="organization", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="organization", cascade="all, delete-orphan")
