from fastapi import APIRouter
from app.api.routes import auth, uploads, records, reviews, dashboard, audits

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(records.router, prefix="/records", tags=["records"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(audits.router, prefix="/audit", tags=["audit"])
