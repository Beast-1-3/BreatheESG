from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional, Dict, Any

class ValidationIssueOut(BaseModel):
    id: str
    issue_type: str
    field: Optional[str]
    message: str
    severity: str
    created_at: datetime

    class Config:
        from_attributes = True

class AnalystInfo(BaseModel):
    id: str
    username: str

    class Config:
        from_attributes = True

class ReviewDecisionOut(BaseModel):
    id: str
    action: str
    comment_text: Optional[str]
    created_at: datetime
    analyst: Optional[AnalystInfo]

    class Config:
        from_attributes = True

class RawRecordOut(BaseModel):
    id: str
    row_index: int
    raw_payload: Dict[str, Any]
    status: str

    class Config:
        from_attributes = True

class EmissionRecordOut(BaseModel):
    id: str
    source_type: str
    source_reference: Optional[str]
    activity_type: str
    category: str
    scope: str
    amount: Optional[float]
    original_unit: Optional[str]
    normalized_unit: Optional[str]
    normalized_value: Optional[float]
    emission_factor: Optional[float]
    estimated_emissions: Optional[float]
    confidence_score: float
    validation_status: str
    review_status: str
    locked_for_audit: bool
    transaction_date: Optional[date]
    facility_id: Optional[str]
    cost_center: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class EmissionRecordDetailOut(EmissionRecordOut):
    validation_issues: List[ValidationIssueOut] = []
    reviews: List[ReviewDecisionOut] = []
    raw_record: Optional[RawRecordOut] = None

    class Config:
        from_attributes = True

class RecordsResponse(BaseModel):
    items: List[EmissionRecordOut]
    total: int
    page: int
    size: int
