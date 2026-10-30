"""
Pydantic-схемы для News.
Модель API отделена от модели БД.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NewsBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    link: str = Field(..., min_length=5, max_length=500)
    description: Optional[str] = None
    published: Optional[str] = None


class NewsCreate(NewsBase):
    """Для POST /news/."""
    game_id: Optional[int] = None
    source_id: Optional[int] = None


class NewsUpdate(BaseModel):
    """Для PUT /news/{id} — все поля опциональны."""
    title: Optional[str] = Field(None, min_length=3, max_length=500)
    description: Optional[str] = None
    status: Optional[str] = None


class NewsOut(NewsBase):
    """Для ответов API."""
    id: int
    status: str
    created_at: Optional[datetime] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True


class NewsListOut(BaseModel):
    """Для пагинированного списка."""
    total: int
    page: int
    per_page: int
    items: list[NewsOut]


# В NewsCreate добавь image_url:
class NewsCreate(NewsBase):
    game_id: Optional[int] = None
    source_id: Optional[int] = None
    image_url: Optional[str] = None

# Добавь в конец файла:
class NewsStatusUpdate(BaseModel):
    status: str