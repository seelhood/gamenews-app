from typing import Optional
from pydantic import BaseModel, Field

class SourceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    rss_url: str = Field(..., min_length=5, max_length=500)
    is_active: bool = True

class SourceCreate(SourceBase):
    pass

class SourceUpdate(BaseModel):
    name: Optional[str] = None
    rss_url: Optional[str] = None
    is_active: Optional[bool] = None

class SourceOut(SourceBase):
    id: int
    class Config:
        from_attributes = True