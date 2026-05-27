from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from collections import defaultdict
from app.core.database import get_db
from app.core.dependencies import get_current_active_analyst
from app.models.user import User
from app.models.emission_record import NormalizedEmissionRecord
from app.schemas.dashboard import DashboardSummaryOut, ScopeMetrics

router = APIRouter()

@router.get("/summary", response_model=DashboardSummaryOut)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_active_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve aggregated metrics, scope analysis, source splits, and trend lines for the organization dashboard.
    """
    org_id = current_user.organization_id
    
    # Query all active emissions records for organization
    stmt = select(NormalizedEmissionRecord).where(NormalizedEmissionRecord.organization_id == org_id)
    res = await db.execute(stmt)
    records = res.scalars().all()
    
    # Process aggregates in Python to ensure perfect cross-database compatibility (SQLite + Postgres)
    total_emissions = 0.0
    record_count = len(records)
    
    scope_data = {
        "Scope 1": {"emissions": 0.0, "count": 0},
        "Scope 2": {"emissions": 0.0, "count": 0},
        "Scope 3": {"emissions": 0.0, "count": 0}
    }
    
    source_counts = defaultdict(int)
    review_counts = defaultdict(int)
    validation_counts = defaultdict(int)
    
    # Monthly emissions tracking
    monthly_data = defaultdict(lambda: {"Scope 1": 0.0, "Scope 2": 0.0, "Scope 3": 0.0})
    
    for r in records:
        em = r.estimated_emissions or 0.0
        total_emissions += em
        
        # Scope stats
        sc = r.scope or "Scope 3"
        if sc in scope_data:
            scope_data[sc]["emissions"] += em
            scope_data[sc]["count"] += 1
            
        # Source split
        source_counts[r.source_type] += 1
        
        # Status splits
        review_counts[r.review_status] += 1
        validation_counts[r.validation_status] += 1
        
        # Monthly splits
        if r.transaction_date:
            month_key = r.transaction_date.strftime("%Y-%m")
            monthly_data[month_key][sc] += em

    # Format monthly trends list sorted by date key
    sorted_months = sorted(list(monthly_data.keys()))
    monthly_emissions_list = []
    for m in sorted_months:
        monthly_emissions_list.append({
            "month": m,
            "Scope 1": round(monthly_data[m]["Scope 1"], 2),
            "Scope 2": round(monthly_data[m]["Scope 2"], 2),
            "Scope 3": round(monthly_data[m]["Scope 3"], 2)
        })

    # Prepare response payload
    return {
        "total_emissions_kg": round(total_emissions, 2),
        "record_count": record_count,
        "scope_breakdown": {
            k: ScopeMetrics(emissions=round(v["emissions"], 2), count=v["count"])
            for k, v in scope_data.items()
        },
        "source_breakdown": {
            "sap": source_counts["sap"],
            "utility": source_counts["utility"],
            "travel": source_counts["travel"]
        },
        "review_status_breakdown": {
            "pending": review_counts["pending"],
            "approved": review_counts["approved"],
            "rejected": review_counts["rejected"]
        },
        "validation_status_breakdown": {
            "pending": validation_counts["pending"],
            "validated": validation_counts["validated"],
            "flagged": validation_counts["flagged"]
        },
        "monthly_emissions": monthly_emissions_list
    }
