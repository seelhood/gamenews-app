from database.repositories.user_repository import UserRepository
from database.repositories.game_repository import GameRepository
from database.repositories.news_repository import NewsRepository
from database.repositories.favorite_repository import FavoriteRepository

__all__ = [
    "UserRepository", "GameRepository",
    "NewsRepository", "FavoriteRepository",
]