from pydantic import BaseModel
from typing import Dict, List, Any

class ScopeMetrics(BaseModel):
    emissions: float
    count: int

class DashboardSummaryOut(BaseModel):
    total_emissions_kg: float
    record_count: int
    scope_breakdown: Dict[str, ScopeMetrics]  # "Scope 1", "Scope 2", "Scope 3"
    source_breakdown: Dict[str, int]          # "sap", "utility", "travel"
    review_status_breakdown: Dict[str, int]   # "pending", "approved", "rejected"
    validation_status_breakdown: Dict[str, int] # "pending", "validated", "flagged"
    monthly_emissions: List[Dict[str, Any]]   # E.g. [{"month": "2026-05", "Scope 1": 1200, "Scope 2": 450, "Scope 3": 90}]
