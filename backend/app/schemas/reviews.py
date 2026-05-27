from pydantic import BaseModel
from typing import Optional

class ReviewActionInput(BaseModel):
    comment_text: Optional[str] = None

class RejectActionInput(BaseModel):
    comment_text: str  # Comment is mandatory for rejections
