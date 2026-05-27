import pytest
from datetime import date
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from app.core.database import Base
from app.models.organization import Organization
from app.models.user import User
from app.models.datasource import DataSource
from app.models.raw_upload import RawUpload
from app.models.raw_record import RawRecord
from app.models.emission_record import NormalizedEmissionRecord
from app.models.validation_issue import ValidationIssue
from app.models.review import ReviewDecision
from app.services.normalization.unit_normalizer import unit_normalizer_service
from app.services.normalization.scope_classifier import scope_classifier_service
from app.services.normalization.emission_mapper import emission_mapper_service
from app.services.validation.validators import validation_service
from app.services.validation.anomaly_detector import anomaly_detector_service
from app.services.review.review_service import review_service

import pytest_asyncio

# Use in-memory SQLite for testing
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(DATABASE_URL, future=True, echo=False)
    async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with async_session() as session:
        yield session
        await session.rollback()
        
    await engine.dispose()

@pytest.mark.asyncio
async def test_normalization_and_scopes():
    # 1. Test Unit Normalizer (Liters base for liquid, Gallons conversion)
    norm_val, norm_unit, score = unit_normalizer_service.normalize_record_unit("100", "Gallons")
    assert norm_val == 378.541
    assert norm_unit == "L"
    assert score == 1.0
    
    # German comma conversion
    norm_val_de, _, _ = unit_normalizer_service.normalize_record_unit("3,5", "L")
    assert norm_val_de == 3.5

    # 2. Test Scope Classification
    scope, cat = scope_classifier_service.classify_scope("sap", "Diesel")
    assert scope == "Scope 1"
    assert "Combustion" in cat
    
    scope_util, cat_util = scope_classifier_service.classify_scope("utility", "electricity")
    assert scope_util == "Scope 2"
    assert cat_util == "Purchased Electricity"

    scope_trv, cat_trv = scope_classifier_service.classify_scope("travel", "flight")
    assert scope_trv == "Scope 3"
    assert "Air" in cat_trv

@pytest.mark.asyncio
async def test_emissions_calculations():
    # SAP Diesel liters conversion
    emissions, factor, confidence = emission_mapper_service.calculate_emissions("sap", "diesel", 100)
    assert emissions == 268.0  # 100 L * 2.68
    assert factor == 2.68
    assert confidence == 1.0

    # Travel Flight Economy passenger-km
    emissions_f, factor_f, _ = emission_mapper_service.calculate_emissions("travel", "flight", 1000, travel_class="economy")
    assert emissions_f == 150.0  # 1000 km * 0.15
    assert factor_f == 0.15

@pytest.mark.asyncio
async def test_validation_and_audit_locking(db_session: AsyncSession):
    # Setup organization and user
    org = Organization(name="Acme Org")
    db_session.add(org)
    await db_session.flush()
    
    user = User(username="test_user", email="test@acme.com", hashed_password="pw", organization_id=org.id)
    db_session.add(user)
    await db_session.flush()
    
    ds = DataSource(name="SAP Upload", source_type="sap", organization_id=org.id)
    db_session.add(ds)
    await db_session.flush()

    upload = RawUpload(organization_id=org.id, datasource_id=ds.id, uploader_id=user.id, filename="sap.csv", status="processed")
    db_session.add(upload)
    await db_session.flush()

    raw_rec = RawRecord(raw_upload_id=upload.id, row_index=1, raw_payload={"Fuel Type": "Diesel", "Quantity": "-500", "Unit": "L"}, status="processed")
    db_session.add(raw_rec)
    await db_session.flush()

    # Create invalid record (negative value)
    record = NormalizedEmissionRecord(
        organization_id=org.id,
        raw_record_id=raw_rec.id,
        source_type="sap",
        activity_type="Diesel",
        category="Mobile Combustion",
        scope="Scope 1",
        amount=-500.0,
        original_unit="L",
        normalized_unit="L",
        normalized_value=-500.0,
        validation_status="pending",
        review_status="pending",
        locked_for_audit=False
    )
    db_session.add(record)
    await db_session.flush()

    # Validate
    issues = await validation_service.validate_record(db_session, record, raw_rec.raw_payload)
    assert len(issues) == 1
    assert issues[0]["type"] == "negative_value"
    
    # Approve and Lock Record
    approved_record = await review_service.approve_record(
        db=db_session,
        record_id=record.id,
        analyst_id=user.id,
        organization_id=org.id,
        comment_text="Verified invoice manually."
    )
    
    assert approved_record.review_status == "approved"
    assert approved_record.locked_for_audit is True

    # Attempt to reject locked record (should raise HTTP 400 Exception)
    import fastapi
    with pytest.raises(fastapi.HTTPException) as exc_info:
        await review_service.reject_record(
            db=db_session,
            record_id=record.id,
            analyst_id=user.id,
            organization_id=org.id,
            comment_text="Try to reject"
        )
    assert exc_info.value.status_code == 400
