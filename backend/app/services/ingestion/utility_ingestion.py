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

class UtilityIngestionService:
    @staticmethod
    async def ingest_utility_csv(
        db: AsyncSession,
        file_bytes: bytes,
        filename: str,
        uploader_id: str,
        organization_id: str,
        datasource_id: str
    ) -> RawUpload:
        """
        Ingests a Utility Electricity CSV file.
        """
        parsed_rows, _ = parse_csv_bytes(file_bytes)
        
        upload = RawUpload(
            organization_id=organization_id,
            datasource_id=datasource_id,
            uploader_id=uploader_id,
            filename=filename,
            file_size=len(file_bytes),
            status="pending"
        )
        db.add(upload)
        await db.flush()
        
        success_count = 0
        
        for idx, row in enumerate(parsed_rows):
            raw_record = RawRecord(
                raw_upload_id=upload.id,
                row_index=idx + 1,
                raw_payload=row,
                status="pending"
            )
            db.add(raw_record)
            await db.flush()
            
            try:
                meter_id = row.get("Meter ID")
                start_date_str = row.get("Billing Start Date")
                end_date_str = row.get("Billing End Date")
                usage_str = row.get("kWh Usage")
                cost_str = row.get("Cost")
                invoice_no = row.get("Invoice Number")
                
                # Normalization
                norm_val, norm_unit, unit_confidence = unit_normalizer_service.normalize_record_unit(usage_str, "kWh")
                
                # Classify Scope
                scope, category = scope_classifier_service.classify_scope("utility", "electricity")
                
                # Compute Emissions
                emissions, factor, ef_confidence = emission_mapper_service.calculate_emissions(
                    "utility", "electricity", norm_val
                )
                
                # Resolve date (use end date as the transaction date)
                txn_date = None
                if end_date_str:
                    try:
                        txn_date = date.fromisoformat(end_date_str.strip())
                    except ValueError:
                        pass
                
                confidence_score = unit_confidence * ef_confidence
                if not txn_date:
                    confidence_score *= 0.7
                    txn_date = date.today()
                    
                amount_val = None
                if usage_str:
                    try:
                        amount_val = float(usage_str.replace(",", ".").replace(" ", ""))
                    except ValueError:
                        pass
                        
                norm_record = NormalizedEmissionRecord(
                    organization_id=organization_id,
                    raw_record_id=raw_record.id,
                    source_type="utility",
                    source_reference=invoice_no,
                    activity_type="Electricity",
                    category=category,
                    scope=scope,
                    amount=amount_val,
                    original_unit="kWh",
                    normalized_unit=norm_unit,
                    normalized_value=norm_val,
                    emission_factor=factor,
                    estimated_emissions=emissions,
                    confidence_score=confidence_score,
                    validation_status=STATUS_PENDING,
                    review_status=STATUS_PENDING,
                    locked_for_audit=False,
                    transaction_date=txn_date,
                    facility_id=meter_id,
                    cost_center=None
                )
                db.add(norm_record)
                await db.flush()
                
                # Validate Record
                validation_issues = await validation_service.validate_record(db, norm_record, row)
                
                # Anomaly Checks
                anomaly = await anomaly_detector_service.detect_anomaly(db, norm_record)
                if anomaly:
                    validation_issues.append(anomaly)
                    
                # Save Issues
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
                
                if has_errors or has_warnings:
                    norm_record.validation_status = STATUS_FLAGGED
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
            
        await audit_log_service.log_action(
            db=db,
            organization_id=organization_id,
            user_id=uploader_id,
            action="upload_data",
            target_type="raw_upload",
            target_id=upload.id,
            after_state={"filename": filename, "source": "utility", "row_count": len(parsed_rows)}
        )
        
        await db.commit()
        return upload
utility_ingestion_service = UtilityIngestionService()
