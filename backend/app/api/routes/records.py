from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.dependencies import get_current_active_analyst
from app.models.user import User
from app.models.emission_record import NormalizedEmissionRecord
from app.models.raw_record import RawRecord
from app.models.review import ReviewDecision
from app.schemas.records import RecordsResponse, EmissionRecordDetailOut, EmissionRecordOut

router = APIRouter()

@router.get("", response_model=RecordsResponse)
async def list_records(
    current_user: User = Depends(get_current_active_analyst),
    db: AsyncSession = Depends(get_db),
    scope: Optional[str] = Query(None),
    source_type: Optional[str] = Query(None),
    validation_status: Optional[str] = Query(None),
    review_status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100)
):
    """
    List, filter, and paginate normalized emission records for the user's organization.
    """
    # Base query filtering by organization
    query = select(NormalizedEmissionRecord).where(
        NormalizedEmissionRecord.organization_id == current_user.organization_id
    )
    
    # Apply filters
    if scope:
        query = query.where(NormalizedEmissionRecord.scope == scope)
    if source_type:
        query = query.where(NormalizedEmissionRecord.source_type == source_type)
    if validation_status:
        query = query.where(NormalizedEmissionRecord.validation_status == validation_status)
    if review_status:
        query = query.where(NormalizedEmissionRecord.review_status == review_status)
        
    if search:
        search_lower = f"%{search.lower()}%"
        query = query.where(
            or_(
                func.lower(NormalizedEmissionRecord.source_reference).like(search_lower),
                func.lower(NormalizedEmissionRecord.activity_type).like(search_lower),
                func.lower(NormalizedEmissionRecord.category).like(search_lower),
                func.lower(NormalizedEmissionRecord.facility_id).like(search_lower),
                func.lower(NormalizedEmissionRecord.cost_center).like(search_lower)
            )
        )

    # Count total items
    count_query = select(func.count()).select_from(query.subquery())
    count_res = await db.execute(count_query)
    total = count_res.scalar() or 0
    
    # Pagination
    offset = (page - 1) * size
    query = query.order_by(NormalizedEmissionRecord.transaction_date.desc()).offset(offset).limit(size)
    
    res = await db.execute(query)
    items = res.scalars().all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size
    }

@router.get("/{id}", response_model=EmissionRecordDetailOut)
async def get_record_detail(
    id: str,
    current_user: User = Depends(get_current_active_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch record details, including raw payload data, validation failures, and review logs.
    """
    stmt = (
        select(NormalizedEmissionRecord)
        .where(
            NormalizedEmissionRecord.id == id,
            NormalizedEmissionRecord.organization_id == current_user.organization_id
        )
        .options(
            selectinload(NormalizedEmissionRecord.validation_issues),
            selectinload(NormalizedEmissionRecord.raw_record),
            selectinload(NormalizedEmissionRecord.reviews).selectinload(ReviewDecision.analyst)
        )
    )
    res = await db.execute(stmt)
    record = res.scalars().first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emission record not found"
        )
        
    return record
