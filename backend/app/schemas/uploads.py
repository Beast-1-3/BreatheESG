from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class DataSourceOut(BaseModel):
    id: str
    name: str
    source_type: str
    is_active: bool

    class Config:
        from_attributes = True

class RawUploadOut(BaseModel):
    id: str
    filename: Optional[str]
    file_size: Optional[int]
    status: str
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
