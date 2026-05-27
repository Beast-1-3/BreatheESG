from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog

class AuditLogService:
    @staticmethod
    async def log_action(
        db: AsyncSession,
        organization_id: str,
        user_id: Optional[str],
        action: str,
        target_type: str,
        target_id: str,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """
        Constructs and persists an audit log entry.
        """
        audit_entry = AuditLog(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            before_state=before_state,
            after_state=after_state,
            ip_address=ip_address
        )
        db.add(audit_entry)
        await db.flush()  # Ensures the record gets an ID and is part of the transaction
        return audit_entry
audit_log_service = AuditLogService()
