from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base import Base
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    news_id = Column(Integer, ForeignKey("news.id", ondelete="CASCADE"), nullable=False)
    added_date = Column(DateTime(timezone=True), server_default=func.now())
    saved_title = Column(String(500), nullable=True)
    saved_text = Column(String, nullable=True) 

    user = relationship("User", back_populates="favorites")
    news = relationship("News", back_populates="favorites")