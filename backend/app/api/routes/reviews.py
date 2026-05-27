from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_active_analyst
from app.models.user import User
from app.schemas.records import EmissionRecordOut
from app.schemas.reviews import ReviewActionInput, RejectActionInput
from app.services.review.review_service import review_service

router = APIRouter()

@router.post("/{id}/approve", response_model=EmissionRecordOut)
async def approve_record(
    id: str,
    review_in: ReviewActionInput,
    current_user: User = Depends(get_current_active_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve an emission record, resolving flags and locking it for audit.
    """
    record = await review_service.approve_record(
        db=db,
        record_id=id,
        analyst_id=current_user.id,
        organization_id=current_user.organization_id,
        comment_text=review_in.comment_text
    )
    return record

@router.post("/{id}/reject", response_model=EmissionRecordOut)
async def reject_record(
    id: str,
    review_in: RejectActionInput,
    current_user: User = Depends(get_current_active_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Reject an emission record. Requires a comment explaining the rejection.
    """
    record = await review_service.reject_record(
        db=db,
        record_id=id,
        analyst_id=current_user.id,
        organization_id=current_user.organization_id,
        comment_text=review_in.comment_text
    )
    return record

@router.post("/{id}/comment")
async def add_comment(
    id: str,
    review_in: RejectActionInput,  # Comment required
    current_user: User = Depends(get_current_active_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a comment to the record timeline.
    """
    comment = await review_service.add_comment(
        db=db,
        record_id=id,
        analyst_id=current_user.id,
        organization_id=current_user.organization_id,
        comment_text=review_in.comment_text
    )
    return {"status": "success", "id": comment.id}
