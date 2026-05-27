from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.dependencies import get_current_active_analyst
from app.models.user import User
from app.models.datasource import DataSource
from app.models.raw_upload import RawUpload
from app.schemas.uploads import RawUploadOut, DataSourceOut
from app.services.ingestion.sap_ingestion import sap_ingestion_service
from app.services.ingestion.utility_ingestion import utility_ingestion_service
from app.services.ingestion.travel_ingestion import travel_ingestion_service

router = APIRouter()

async def get_datasource_by_type(db: AsyncSession, org_id: str, source_type: str) -> DataSource:
    stmt = select(DataSource).where(
        DataSource.organization_id == org_id,
        DataSource.source_type == source_type,
        DataSource.is_active == True
    )
    res = await db.execute(stmt)
    ds = res.scalars().first()
    if not ds:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active DataSource config found for type '{source_type}'. Register one first."
        )
    return ds

@router.get("/datasources", response_model=List[DataSourceOut])
async def list_datasources(
    current_user: User = Depends(get_current_active_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Lists data sources for the current organization."""
    stmt = select(DataSource).where(DataSource.organization_id == current_user.organization_id)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/history", response_model=List[RawUploadOut])
async def list_upload_history(
    current_user: User = Depends(get_current_active_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Lists raw uploads history for the organization."""
    stmt = select(RawUpload).where(
        RawUpload.organization_id == current_user.organization_id
    ).order_by(RawUpload.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/sap", response_model=RawUploadOut)
async def upload_sap_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Ingests a SAP CSV report."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only CSV exports are accepted."
        )
    
    ds = await get_datasource_by_type(db, current_user.organization_id, "sap")
    file_bytes = await file.read()
    
    try:
        upload = await sap_ingestion_service.ingest_sap_csv(
            db=db,
            file_bytes=file_bytes,
            filename=file.filename,
            uploader_id=current_user.id,
            organization_id=current_user.organization_id,
            datasource_id=ds.id
        )
        return upload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SAP Ingestion failed: {str(e)}"
        )

@router.post("/utility", response_model=RawUploadOut)
async def upload_utility_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Ingests a Utility Portal CSV export."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only CSV exports are accepted."
        )
        
    ds = await get_datasource_by_type(db, current_user.organization_id, "utility")
    file_bytes = await file.read()
    
    try:
        upload = await utility_ingestion_service.ingest_utility_csv(
            db=db,
            file_bytes=file_bytes,
            filename=file.filename,
            uploader_id=current_user.id,
            organization_id=current_user.organization_id,
            datasource_id=ds.id
        )
        return upload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Utility Ingestion failed: {str(e)}"
        )

@router.post("/travel/sync", response_model=RawUploadOut)
async def sync_travel(
    current_user: User = Depends(get_current_active_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Trigger synchronization run with mock Travel API."""
    ds = await get_datasource_by_type(db, current_user.organization_id, "travel")
    try:
        upload = await travel_ingestion_service.sync_travel_api(
            db=db,
            uploader_id=current_user.id,
            organization_id=current_user.organization_id,
            datasource_id=ds.id
        )
        return upload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Travel Sync failed: {str(e)}"
        )
