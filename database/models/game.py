from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database.base import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    genre = Column(String(100), nullable=True)
    is_tracked = Column(Boolean, default=True)

    news = relationship("News", back_populates="game", cascade="all, delete-orphan")
    users = relationship("User", secondary="user_games", back_populates="games")

    def __repr__(self):
        return f"<Game(id={self.id}, title='{self.title}')>"