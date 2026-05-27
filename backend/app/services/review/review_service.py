from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.emission_record import NormalizedEmissionRecord
from app.models.review import ReviewDecision
from app.services.audit.audit_service import audit_log_service
from app.core.constants import STATUS_APPROVED, STATUS_REJECTED, STATUS_LOCKED

class ReviewService:
    @staticmethod
    async def approve_record(
        db: AsyncSession,
        record_id: str,
        analyst_id: str,
        organization_id: str,
        comment_text: Optional[str] = None
    ) -> NormalizedEmissionRecord:
        """
        Approves an emission record, setting it to approved and locked for audit.
        """
        record = await db.get(NormalizedEmissionRecord, record_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
            
        if record.locked_for_audit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Record is locked and cannot be modified"
            )
            
        before_state = {
            "review_status": record.review_status,
            "locked_for_audit": record.locked_for_audit
        }
        
        # Modify record state
        record.review_status = STATUS_APPROVED
        record.locked_for_audit = True  # lock it
        
        # Save decision
        decision = ReviewDecision(
            emission_record_id=record.id,
            analyst_id=analyst_id,
            action="approve",
            comment_text=comment_text
        )
        db.add(decision)
        
        # Audit log
        after_state = {
            "review_status": record.review_status,
            "locked_for_audit": record.locked_for_audit
        }
        await audit_log_service.log_action(
            db=db,
            organization_id=organization_id,
            user_id=analyst_id,
            action="approve_record",
            target_type="emission_record",
            target_id=record.id,
            before_state=before_state,
            after_state=after_state
        )
        
        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def reject_record(
        db: AsyncSession,
        record_id: str,
        analyst_id: str,
        organization_id: str,
        comment_text: str
    ) -> NormalizedEmissionRecord:
        """
        Rejects an emission record. Requires a comment.
        """
        if not comment_text or not comment_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="A comment is required to reject a record"
            )
            
        record = await db.get(NormalizedEmissionRecord, record_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
            
        if record.locked_for_audit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Record is locked and cannot be modified"
            )
            
        before_state = {
            "review_status": record.review_status
        }
        
        record.review_status = STATUS_REJECTED
        
        # Save decision
        decision = ReviewDecision(
            emission_record_id=record.id,
            analyst_id=analyst_id,
            action="reject",
            comment_text=comment_text
        )
        db.add(decision)
        
        # Audit log
        after_state = {
            "review_status": record.review_status
        }
        await audit_log_service.log_action(
            db=db,
            organization_id=organization_id,
            user_id=analyst_id,
            action="reject_record",
            target_type="emission_record",
            target_id=record.id,
            before_state=before_state,
            after_state=after_state
        )
        
        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def add_comment(
        db: AsyncSession,
        record_id: str,
        analyst_id: str,
        organization_id: str,
        comment_text: str
    ) -> ReviewDecision:
        """
        Adds a comment to a record without changing its approval status.
        Allows comments even if a record is locked (e.g. audit notes).
        """
        if not comment_text or not comment_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Comment text cannot be empty"
            )
            
        record = await db.get(NormalizedEmissionRecord, record_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
            
        # Save comment decision
        decision = ReviewDecision(
            emission_record_id=record.id,
            analyst_id=analyst_id,
            action="comment",
            comment_text=comment_text
        )
        db.add(decision)
        
        await audit_log_service.log_action(
            db=db,
            organization_id=organization_id,
            user_id=analyst_id,
            action="comment_record",
            target_type="emission_record",
            target_id=record.id,
            after_state={"comment": comment_text}
        )
        
        await db.commit()
        return decision
review_service = ReviewService()
