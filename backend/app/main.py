from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import api_router
from app.core.database import Base, engine, is_sqlite
from app.utils.logger import logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Analyst-friendly ESG Data Ingestion, Normalization & Audit Platform API",
    version="1.0.0"
)

# Set CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include APIs
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def on_startup():
    logger.info("Starting up Breathe ESG Platform backend...")
    
    # Auto-initialize tables in SQLite for development convenience
    if is_sqlite:
        logger.info("Detected local SQLite. Automatically creating missing tables...")
        async with engine.begin() as conn:
            # Import models to ensure they register on Base
            from app.models.organization import Organization
            from app.models.user import User
            from app.models.datasource import DataSource
            from app.models.raw_upload import RawUpload
            from app.models.raw_record import RawRecord
            from app.models.emission_record import NormalizedEmissionRecord
            from app.models.validation_issue import ValidationIssue
            from app.models.review import ReviewDecision
            from app.models.audit_log import AuditLog
            
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Table creation completed.")
    else:
        logger.info("Using external database. Running migrations via Alembic is recommended.")

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "docs_url": "/docs"
    }
