from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class FavoriteCreate(BaseModel):
    news_id: int
    saved_title: Optional[str] = None
    saved_text: Optional[str] = None

class FavoriteOut(BaseModel):
    id: int
    news_id: int
    news_title: str
    saved_title: Optional[str] = None
    added_date: Optional[datetime] = None