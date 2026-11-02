from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base import Base
from sqlalchemy import Column, Integer, String, DateTime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
        # В классе User добавь:
    role = Column(String(20), default="user", nullable=False)

    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    games = relationship("Game", secondary="user_games", back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"