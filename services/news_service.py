from database.session import SessionLocal
from database.repositories.news_repository import NewsRepository

class NewsService:
    def list_news_for_user(self, user_id: int, limit: int = 100, source_name: str = None):
        db = SessionLocal()
        try:
            from database.models.user_game import UserGame
            user_games = db.query(UserGame).filter(UserGame.user_id == user_id).all()
            game_ids = [ug.game_id for ug in user_games]
            
            repo = NewsRepository(db)
            news = repo.get_by_games_and_source(game_ids, source_name, limit)
            
            return [
                {
                    "id": n.id, 
                    "title": n.title, 
                    "description": n.description, 
                    "link": n.link, 
                    "status": n.status, 
                    "source": n.source.name if n.source else "—", 
                    "published": n.published, 
                    "image_url": n.image_url
                } 
                for n in news
            ]
        finally:
            db.close()

    def search_news_for_user(self, user_id: int, query: str):
        db = SessionLocal()
        try:
            from database.models.user_game import UserGame
            from database.models.news import News
            from sqlalchemy import or_
            user_games = db.query(UserGame).filter(UserGame.user_id == user_id).all()
            game_ids = [ug.game_id for ug in user_games]
            if not game_ids: return []

            pattern = f"%{query}%"
            results = db.query(News).filter(News.game_id.in_(game_ids)).filter(or_(News.title.ilike(pattern), News.description.ilike(pattern))).order_by(News.id.desc()).limit(50).all()
            return [{"id": n.id, "title": n.title, "description": n.description, "link": n.link, "status": n.status, "source": n.source.name if n.source else "—", "published": n.published, "image_url": n.image_url} for n in results]
        finally:
            db.close()