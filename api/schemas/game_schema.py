from typing import Optional
from pydantic import BaseModel, Field


class GameBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    genre: Optional[str] = None


class GameCreate(GameBase):
    pass


class GameUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    genre: Optional[str] = None


class GameOut(GameBase):
    id: int
    is_tracked: bool

    class Config:
        from_attributes = True