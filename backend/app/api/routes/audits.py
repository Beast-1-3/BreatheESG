from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.dependencies import get_current_active_analyst
from app.models.user import User
from app.models.audit_log import AuditLog

router = APIRouter()

@router.get("")
async def get_system_audit_timeline(
    current_user: User = Depends(get_current_active_analyst),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, ge=1, le=500)
):
    """
    Fetch the general timeline of all changes, uploads, approvals, and actions for this organization.
    """
    stmt = (
        select(AuditLog)
        .where(AuditLog.organization_id == current_user.organization_id)
        .options(selectinload(AuditLog.user))
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    res = await db.execute(stmt)
    logs = res.scalars().all()
    
    # Format to include username details easily for frontend timeline
    timeline = []
    for log in logs:
        timeline.append({
            "id": log.id,
            "user": log.user.username if log.user else "System",
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "before_state": log.before_state,
            "after_state": log.after_state,
            "created_at": log.created_at
        })
        
    return timeline

@router.get("/{target_id}")
async def get_target_audit_logs(
    target_id: str,
    current_user: User = Depends(get_current_active_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve audit details specifically for one target resource (e.g. detailed edits/rejections for an emission record).
    """
    stmt = (
        select(AuditLog)
        .where(
            AuditLog.organization_id == current_user.organization_id,
            AuditLog.target_id == target_id
        )
        .options(selectinload(AuditLog.user))
        .order_by(AuditLog.created_at.desc())
    )
    res = await db.execute(stmt)
    logs = res.scalars().all()
    
    timeline = []
    for log in logs:
        timeline.append({
            "id": log.id,
            "user": log.user.username if log.user else "System",
            "action": log.action,
            "before_state": log.before_state,
            "after_state": log.after_state,
            "created_at": log.created_at
        })
        
    return timeline
