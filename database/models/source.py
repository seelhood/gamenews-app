from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database.base import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    rss_url = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)

    news = relationship("News", back_populates="source")