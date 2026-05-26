import uuid
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.csv_parser import parse_csv_bytes
from app.models.raw_upload import RawUpload
from app.models.raw_record import RawRecord
from app.models.emission_record import NormalizedEmissionRecord
from app.models.validation_issue import ValidationIssue
from app.services.normalization.unit_normalizer import unit_normalizer_service
from app.services.normalization.scope_classifier import scope_classifier_service
from app.services.normalization.emission_mapper import emission_mapper_service
from app.services.validation.validators import validation_service
from app.services.validation.anomaly_detector import anomaly_detector_service
from app.services.audit.audit_service import audit_log_service
from app.core.constants import STATUS_PENDING, STATUS_VALIDATED, STATUS_FLAGGED

def parse_sap_date(date_str: str) -> Optional[date]:
    """Parse various dates common in SAP exports."""
    if not date_str:
        return None
    date_str = date_str.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None

class SapIngestionService:
    @staticmethod
    async def ingest_sap_csv(
        db: AsyncSession,
        file_bytes: bytes,
        filename: str,
        uploader_id: str,
        organization_id: str,
        datasource_id: str
    ) -> RawUpload:
        """
        Ingests a SAP CSV file containing fuel and procurement records.
        """
        # Parse CSV
        parsed_rows, _ = parse_csv_bytes(file_bytes)
        
        # 1. Create Raw Upload Metadata
        upload = RawUpload(
            organization_id=organization_id,
            datasource_id=datasource_id,
            uploader_id=uploader_id,
            filename=filename,
            file_size=len(file_bytes),
            status="pending"
        )
        db.add(upload)
        await db.flush()  # populate upload.id
        
        success_count = 0
        
        for idx, row in enumerate(parsed_rows):
            # 2. Save Raw Row Record
            raw_record = RawRecord(
                raw_upload_id=upload.id,
                row_index=idx + 1,
                raw_payload=row,
                status="pending"
            )
            db.add(raw_record)
            await db.flush() # populate raw_record.id
            
            try:
                # Extract fields
                plant_code = row.get("Plant Code")
                fuel_type = row.get("Fuel Type")
                qty_str = row.get("Quantity")
                unit_str = row.get("Unit")
                invoice_no = row.get("Invoice Number")
                date_str = row.get("Invoice Date")
                cost_center = row.get("Cost Center")
                
                # Standardize units and values
                norm_val, norm_unit, unit_confidence = unit_normalizer_service.normalize_record_unit(qty_str, unit_str)
                
                # Classify GHG Scope
                scope, category = scope_classifier_service.classify_scope("sap", fuel_type or "")
                
                # Calculate Emissions
                emissions, factor, ef_confidence = emission_mapper_service.calculate_emissions(
                    "sap", fuel_type or "", norm_val
                )
                
                # Handle dates
                txn_date = parse_sap_date(date_str)
                
                # Overall Confidence Score Calculation
                confidence_score = unit_confidence * ef_confidence
                if not txn_date:
                    confidence_score *= 0.8  # Deduct if date is missing/unparseable
                    txn_date = date.today()  # Fallback to avoid null constraint if required, or keep null
                
                # 3. Construct Normalized Record
                amount_val = None
                if qty_str:
                    try:
                        amount_val = float(qty_str.replace(",", ".").replace(" ", ""))
                    except ValueError:
                        pass
                
                norm_record = NormalizedEmissionRecord(
                    organization_id=organization_id,
                    raw_record_id=raw_record.id,
                    source_type="sap",
                    source_reference=invoice_no,
                    activity_type=fuel_type or "Unknown Fuel",
                    category=category,
                    scope=scope,
                    amount=amount_val,
                    original_unit=unit_str,
                    normalized_unit=norm_unit,
                    normalized_value=norm_val,
                    emission_factor=factor,
                    estimated_emissions=emissions,
                    confidence_score=confidence_score,
                    validation_status=STATUS_PENDING,
                    review_status=STATUS_PENDING,
                    locked_for_audit=False,
                    transaction_date=txn_date,
                    facility_id=plant_code,
                    cost_center=cost_center
                )
                db.add(norm_record)
                await db.flush() # Populate norm_record.id
                
                # 4. Perform Validations
                validation_issues = await validation_service.validate_record(db, norm_record, row)
                
                # 5. Check Anomalies
                anomaly = await anomaly_detector_service.detect_anomaly(db, norm_record)
                if anomaly:
                    validation_issues.append(anomaly)
                    
                # 6. Save Issues and set final Status
                has_errors = False
                has_warnings = False
                
                for issue in validation_issues:
                    db_issue = ValidationIssue(
                        emission_record_id=norm_record.id,
                        issue_type=issue["type"],
                        field=issue["field"],
                        message=issue["message"],
                        severity=issue["severity"]
                    )
                    db.add(db_issue)
                    if issue["severity"] == "error":
                        has_errors = True
                    else:
                        has_warnings = True
                
                if has_errors:
                    norm_record.validation_status = STATUS_FLAGGED  # Record needs correction
                elif has_warnings:
                    norm_record.validation_status = STATUS_FLAGGED  # Flagged but not fatal
                else:
                    norm_record.validation_status = STATUS_VALIDATED
                    
                raw_record.status = "processed"
                success_count += 1
                
            except Exception as e:
                db.rollback()
                raw_record.status = "failed"
                raw_record.error_message = str(e)
                
        upload.status = "processed" if success_count == len(parsed_rows) else "failed"
        if upload.status == "failed":
            upload.error_message = f"Processed {success_count}/{len(parsed_rows)} successfully."
            
        # Write Audit Log
        await audit_log_service.log_action(
            db=db,
            organization_id=organization_id,
            user_id=uploader_id,
            action="upload_data",
            target_type="raw_upload",
            target_id=upload.id,
            after_state={"filename": filename, "source": "sap", "row_count": len(parsed_rows)}
        )
        
        await db.commit()
        return upload
sap_ingestion_service = SapIngestionService()
