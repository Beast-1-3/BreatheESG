from datetime import date
from typing import List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.emission_record import NormalizedEmissionRecord
from app.core.constants import (
    ISSUE_DUPLICATE, ISSUE_NEGATIVE_VALUE, ISSUE_MISSING_VALUE,
    ISSUE_INVALID_MAPPING, ISSUE_OVERLAPPING_CYCLE, ISSUE_INVALID_UNIT,
    ISSUE_INVALID_AIRPORT, AIRPORT_COORDINATES, FUEL_MAPPINGS, UNIT_CONVERSIONS
)

class ValidationService:
    @staticmethod
    async def validate_record(
        db: AsyncSession,
        record: NormalizedEmissionRecord,
        raw_row: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Validates a normalized emission record.
        Returns a list of dicts describing issues:
        [{"type": ISSUE_TYPE, "field": FIELD, "message": MSG, "severity": "warning"|"error"}]
        """
        issues = []
        
        # 1. Negative Values Check
        if record.amount is not None and record.amount < 0:
            issues.append({
                "type": ISSUE_NEGATIVE_VALUE,
                "field": "amount",
                "message": f"Negative amount detected: {record.amount}",
                "severity": "error"
            })
            
        # 2. Missing Value Check
        if record.amount is None or not record.original_unit:
            issues.append({
                "type": ISSUE_MISSING_VALUE,
                "field": "amount",
                "message": "Activity amount or unit is missing.",
                "severity": "error"
            })

        # 3. Invalid unit conversion check
        if record.original_unit:
            unit_clean = record.original_unit.strip().lower()
            if unit_clean not in UNIT_CONVERSIONS:
                issues.append({
                    "type": ISSUE_INVALID_UNIT,
                    "field": "original_unit",
                    "message": f"Unsupported or unrecognized unit: {record.original_unit}",
                    "severity": "error"
                })

        # 4. Source specific validations
        if record.source_type == "sap":
            # Check fuel mappings
            fuel = (record.activity_type or "").strip().lower()
            if fuel not in FUEL_MAPPINGS:
                issues.append({
                    "type": ISSUE_INVALID_MAPPING,
                    "field": "activity_type",
                    "message": f"Unrecognized SAP fuel type: {record.activity_type}",
                    "severity": "warning"
                })
                
            # Check for duplicate SAP invoices
            if record.source_reference:
                stmt = select(NormalizedEmissionRecord).where(
                    NormalizedEmissionRecord.source_reference == record.source_reference,
                    NormalizedEmissionRecord.source_type == "sap",
                    NormalizedEmissionRecord.id != record.id
                )
                res = await db.execute(stmt)
                if res.scalars().first():
                    issues.append({
                        "type": ISSUE_DUPLICATE,
                        "field": "source_reference",
                        "message": f"Duplicate SAP Invoice Number detected: {record.source_reference}",
                        "severity": "warning"
                    })

        elif record.source_type == "utility":
            # Check for duplicate utility invoices
            if record.source_reference:
                stmt = select(NormalizedEmissionRecord).where(
                    NormalizedEmissionRecord.source_reference == record.source_reference,
                    NormalizedEmissionRecord.source_type == "utility",
                    NormalizedEmissionRecord.id != record.id
                )
                res = await db.execute(stmt)
                if res.scalars().first():
                    issues.append({
                        "type": ISSUE_DUPLICATE,
                        "field": "source_reference",
                        "message": f"Duplicate Utility Invoice Number detected: {record.source_reference}",
                        "severity": "warning"
                    })

            # Check for overlapping utility billing cycles for same meter (facility_id)
            if record.facility_id and record.transaction_date:
                # We need billing dates from the raw payload
                # Billing Start Date and Billing End Date are in raw_payload
                start_str = raw_row.get("Billing Start Date")
                end_str = raw_row.get("Billing End Date")
                
                if start_str and end_str:
                    try:
                        # parse dates
                        # Format is YYYY-MM-DD
                        start_date = date.fromisoformat(start_str)
                        end_date = date.fromisoformat(end_str)
                        
                        # Find other utility records for the same meter (facility_id)
                        stmt = select(NormalizedEmissionRecord).where(
                            NormalizedEmissionRecord.facility_id == record.facility_id,
                            NormalizedEmissionRecord.source_type == "utility",
                            NormalizedEmissionRecord.id != record.id
                        )
                        res = await db.execute(stmt)
                        other_records = res.scalars().all()
                        
                        for r in other_records:
                            # fetch their raw records to get start/end dates
                            await db.refresh(r, ["raw_record"])
                            r_start_str = r.raw_record.raw_payload.get("Billing Start Date")
                            r_end_str = r.raw_record.raw_payload.get("Billing End Date")
                            
                            if r_start_str and r_end_str:
                                r_start = date.fromisoformat(r_start_str)
                                r_end = date.fromisoformat(r_end_str)
                                
                                # Check overlap: (StartA <= EndB) and (EndA >= StartB)
                                if (start_date <= r_end) and (end_date >= r_start):
                                    issues.append({
                                        "type": ISSUE_OVERLAPPING_CYCLE,
                                        "field": "transaction_date",
                                        "message": f"Billing period ({start_str} to {end_str}) overlaps with billing period ({r_start_str} to {r_end_str}) on Meter {record.facility_id}.",
                                        "severity": "warning"
                                    })
                                    break
                    except ValueError:
                        pass # unparseable dates will be flagged in schema validator if needed

        elif record.source_type == "travel":
            # Check booking duplicates
            if record.source_reference:
                stmt = select(NormalizedEmissionRecord).where(
                    NormalizedEmissionRecord.source_reference == record.source_reference,
                    NormalizedEmissionRecord.source_type == "travel",
                    NormalizedEmissionRecord.id != record.id
                )
                res = await db.execute(stmt)
                if res.scalars().first():
                    issues.append({
                        "type": ISSUE_DUPLICATE,
                        "field": "source_reference",
                        "message": f"Duplicate Travel Booking ID detected: {record.source_reference}",
                        "severity": "warning"
                    })

            # Check flights airport code validity
            if record.activity_type == "flight":
                origin = raw_row.get("origin")
                dest = raw_row.get("destination")
                
                if origin and origin.upper() not in AIRPORT_COORDINATES:
                    issues.append({
                        "type": ISSUE_INVALID_AIRPORT,
                        "field": "origin",
                        "message": f"Invalid origin airport code: {origin}",
                        "severity": "error"
                    })
                if dest and dest.upper() not in AIRPORT_COORDINATES:
                    issues.append({
                        "type": ISSUE_INVALID_AIRPORT,
                        "field": "destination",
                        "message": f"Invalid destination airport code: {dest}",
                        "severity": "error"
                    })

        return issues
validation_service = ValidationService()
