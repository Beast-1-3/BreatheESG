import os
import json
from datetime import date
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.raw_upload import RawUpload
from app.models.raw_record import RawRecord
from app.models.emission_record import NormalizedEmissionRecord
from app.models.validation_issue import ValidationIssue
from app.utils.airport_mapper import calculate_distance
from app.services.normalization.unit_normalizer import unit_normalizer_service
from app.services.normalization.scope_classifier import scope_classifier_service
from app.services.normalization.emission_mapper import emission_mapper_service
from app.services.validation.validators import validation_service
from app.services.validation.anomaly_detector import anomaly_detector_service
from app.services.audit.audit_service import audit_log_service
from app.core.constants import STATUS_PENDING, STATUS_VALIDATED, STATUS_FLAGGED

class TravelIngestionService:
    @staticmethod
    async def sync_travel_api(
        db: AsyncSession,
        uploader_id: str,
        organization_id: str,
        datasource_id: str
    ) -> RawUpload:
        """
        Simulates syncing with a Corporate Travel API (Concur/Navan).
        Reads a mock JSON travel payload and ingests it.
        """
        # Load local mock JSON
        mock_file_path = "/Users/akarsh/.gemini/antigravity/scratch/breathe-esg-platform/sample-data/travel/travel_bookings.json"
        
        if not os.path.exists(mock_file_path):
            raise FileNotFoundError(f"Mock travel bookings file not found at {mock_file_path}")
            
        with open(mock_file_path, "r") as f:
            bookings = json.load(f)
            
        upload = RawUpload(
            organization_id=organization_id,
            datasource_id=datasource_id,
            uploader_id=uploader_id,
            filename="REST API Sync (travel_bookings.json)",
            file_size=os.path.getsize(mock_file_path),
            status="pending"
        )
        db.add(upload)
        await db.flush()
        
        success_count = 0
        
        for idx, booking in enumerate(bookings):
            raw_record = RawRecord(
                raw_upload_id=upload.id,
                row_index=idx + 1,
                raw_payload=booking,
                status="pending"
            )
            db.add(raw_record)
            await db.flush()
            
            try:
                booking_id = booking.get("booking_id")
                employee_id = booking.get("employee_id")
                travel_type = booking.get("travel_type")
                cost = booking.get("cost")
                currency = booking.get("currency")
                date_str = booking.get("booking_date")
                
                # Normalization inputs depend on travel type
                qty = None
                unit_str = None
                
                if travel_type == "flight":
                    origin = booking.get("origin")
                    dest = booking.get("destination")
                    travel_class = booking.get("travel_class", "economy")
                    
                    # Compute distance using airports lat/lon
                    computed_dist = calculate_distance(origin, dest)
                    qty = computed_dist if computed_dist is not None else booking.get("distance_km")
                    unit_str = "km"
                    
                elif travel_type == "hotel":
                    qty = booking.get("hotel_nights")
                    unit_str = "nights"
                    travel_class = None
                    
                elif travel_type in ["taxi", "train"]:
                    qty = booking.get("distance_km")
                    unit_str = "km"
                    travel_class = None
                    
                else:
                    qty = 0
                    unit_str = "unknown"
                    travel_class = None

                # Call Normalizer
                qty_val_str = str(qty) if qty is not None else None
                norm_val, norm_unit, unit_confidence = unit_normalizer_service.normalize_record_unit(qty_val_str, unit_str or "")
                
                # Classify Scope (Scope 3)
                scope, category = scope_classifier_service.classify_scope("travel", travel_type or "")
                
                # Compute Emissions
                emissions, factor, ef_confidence = emission_mapper_service.calculate_emissions(
                    "travel", travel_type or "", norm_val, travel_class=travel_class
                )
                
                # Date parsing
                txn_date = None
                if date_str:
                    try:
                        txn_date = date.fromisoformat(date_str)
                    except ValueError:
                        pass
                        
                confidence_score = unit_confidence * ef_confidence
                # Penalize missing distances
                if travel_type == "flight" and qty is None:
                    confidence_score *= 0.5
                    
                if not txn_date:
                    confidence_score *= 0.7
                    txn_date = date.today()
                    
                norm_record = NormalizedEmissionRecord(
                    organization_id=organization_id,
                    raw_record_id=raw_record.id,
                    source_type="travel",
                    source_reference=booking_id,
                    activity_type=travel_type.capitalize() if travel_type else "Unknown Travel",
                    category=category,
                    scope=scope,
                    amount=qty if qty is not None else None,
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
                    facility_id=booking.get("origin") if travel_type == "flight" else f"Emp:{employee_id}",
                    cost_center=None
                )
                db.add(norm_record)
                await db.flush()
                
                # Validations
                validation_issues = await validation_service.validate_record(db, norm_record, booking)
                
                # Custom travel validations (like check invalid currencies)
                if currency and currency.upper() not in ["USD", "EUR", "GBP"]:
                    validation_issues.append({
                        "type": "invalid_currency",
                        "field": "currency",
                        "message": f"Unsupported corporate currency code: {currency}",
                        "severity": "warning"
                    })
                    
                # Anomaly Checks
                anomaly = await anomaly_detector_service.detect_anomaly(db, norm_record)
                if anomaly:
                    validation_issues.append(anomaly)
                    
                # Save issues
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
                
        upload.status = "processed" if success_count == len(bookings) else "failed"
        if upload.status == "failed":
            upload.error_message = f"Processed {success_count}/{len(bookings)} successfully."
            
        await audit_log_service.log_action(
            db=db,
            organization_id=organization_id,
            user_id=uploader_id,
            action="upload_data",
            target_type="raw_upload",
            target_id=upload.id,
            after_state={"source": "travel", "row_count": len(bookings)}
        )
        
        await db.commit()
        return upload
travel_ingestion_service = TravelIngestionService()
