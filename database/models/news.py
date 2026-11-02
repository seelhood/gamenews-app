from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base import Base


class NewsStatus:
    """Константы статусов новости."""
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

    ALL = [CREATED, ACTIVE, COMPLETED, CANCELLED]


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    link = Column(String(500), unique=True, nullable=False)
    description = Column(String, nullable=True)
    published = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # В классе News добавь:
    image_url = Column(String(500), nullable=True)
    # НОВОЕ: статус жизненного цикла
    status = Column(String(20), default=NewsStatus.CREATED, nullable=False)

    game_id = Column(Integer, ForeignKey("games.id", ondelete="SET NULL"), nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)

    game = relationship("Game", back_populates="news")
    source = relationship("Source", back_populates="news")
    favorites = relationship("Favorite", back_populates="news", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="news_tags", back_populates="news")

    def __repr__(self):
        return f"<News(id={self.id}, status={self.status}, title='{self.title[:30]}...')>"