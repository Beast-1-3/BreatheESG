from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.emission_record import NormalizedEmissionRecord
from app.core.constants import ISSUE_ANOMALY

class AnomalyDetectorService:
    @staticmethod
    async def detect_anomaly(
        db: AsyncSession,
        record: NormalizedEmissionRecord
    ) -> Optional[Dict[str, Any]]:
        """
        Compares the record's emissions/normalized value against historical data for the same source and facility.
        If it exceeds 5x the historical average (and there is enough history), flags as anomaly.
        """
        if record.normalized_value is None or record.normalized_value <= 0:
            return None

        # Filter by source_type and facility_id (plant/meter code)
        stmt = select(func.avg(NormalizedEmissionRecord.normalized_value)).where(
            NormalizedEmissionRecord.source_type == record.source_type,
            NormalizedEmissionRecord.facility_id == record.facility_id,
            NormalizedEmissionRecord.id != record.id,
            NormalizedEmissionRecord.normalized_value > 0
        )
        
        res = await db.execute(stmt)
        avg_val = res.scalar()
        
        if avg_val is not None:
            # Check if count is significant (optional, let's assume if there's any history)
            multiplier = 5.0
            if record.normalized_value > (avg_val * multiplier):
                return {
                    "type": ISSUE_ANOMALY,
                    "field": "normalized_value",
                    "message": f"Suspiciously high value: {record.normalized_value} is {record.normalized_value / avg_val:.1f}x the historical average ({avg_val:.1f}) for this facility/source.",
                    "severity": "warning"
                }

        # Absolute fallback checks for obvious errors
        # e.g., Diesel liters > 500,000 in a single invoice
        if record.source_type == "sap" and record.activity_type == "diesel" and record.normalized_value > 500000:
             return {
                "type": ISSUE_ANOMALY,
                "field": "normalized_value",
                "message": f"Anomalous single Diesel purchase: {record.normalized_value} L exceeds the safety ceiling of 500,000 L.",
                "severity": "warning"
            }
            
        if record.source_type == "utility" and record.normalized_value > 1000000:
             return {
                "type": ISSUE_ANOMALY,
                "field": "normalized_value",
                "message": f"Anomalous single electricity usage: {record.normalized_value} kWh exceeds the safety ceiling of 1,000,000 kWh.",
                "severity": "warning"
            }

        return None
anomaly_detector_service = AnomalyDetectorService()
