import uuid
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Date, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class NormalizedEmissionRecord(Base):
    __tablename__ = "emission_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    raw_record_id = Column(String(36), ForeignKey("raw_records.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Unified schema fields
    source_type = Column(String(50), nullable=False)  # "sap", "utility", "travel"
    source_reference = Column(String(100), nullable=True)  # invoice_number, meter_id, booking_id
    activity_type = Column(String(100), nullable=False)    # e.g., Diesel, Electricity, Flight, Hotel, Train
    category = Column(String(100), nullable=False)         # e.g., Stationary Combustion, Business Travel
    scope = Column(String(20), nullable=False)             # "Scope 1", "Scope 2", "Scope 3"
    
    # Numerical data
    amount = Column(Float, nullable=True)                  # original value
    original_unit = Column(String(50), nullable=True)
    normalized_unit = Column(String(50), nullable=True)
    normalized_value = Column(Float, nullable=True)
    emission_factor = Column(Float, nullable=True)          # factor used for calculation
    estimated_emissions = Column(Float, nullable=True)      # calculated in kg CO2e
    confidence_score = Column(Float, default=1.0)           # 0.0 to 1.0 based on missing data/assumptions
    
    # Statuses
    validation_status = Column(String(50), default="pending")  # "pending", "validated", "flagged"
    review_status = Column(String(50), default="pending")      # "pending", "approved", "rejected"
    locked_for_audit = Column(Boolean, default=False)          # Lock edits after approval
    
    # Metadata
    transaction_date = Column(Date, nullable=True)
    facility_id = Column(String(100), nullable=True)  # plant code, meter ID or location
    cost_center = Column(String(100), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="records")
    raw_record = relationship("RawRecord", back_populates="emission_record")
    validation_issues = relationship("ValidationIssue", back_populates="emission_record", cascade="all, delete-orphan")
    reviews = relationship("ReviewDecision", back_populates="emission_record", cascade="all, delete-orphan")
