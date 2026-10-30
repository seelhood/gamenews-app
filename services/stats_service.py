"""
Сервис для подсчета статистики.
"""
from database.session import SessionLocal
from database.models.news import News
from database.models.game import Game
from database.models.favorite import Favorite


class StatsService:
    def get_stats(self, user_id: int = None) -> dict:
        """
        Собирает общую статистику по БД.
        Если передан user_id, считает избранное для этого пользователя.
        """
        db = SessionLocal()
        try:
            news_count = db.query(News).count()
            games_count = db.query(Game).count()
            
            fav_count = 0
            if user_id:
                fav_count = db.query(Favorite).filter(Favorite.user_id == user_id).count()
                
            return {
                "news": news_count,
                "games": games_count,
                "favorites": fav_count,
            }
        finally:
            db.close()