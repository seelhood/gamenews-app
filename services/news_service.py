from database.session import SessionLocal
from database.repositories.news_repository import NewsRepository
from services.news_lifecycle import NewsLifecycle, NotFoundError, InvalidTransitionError

class NewsService:
    def list_news(self, limit: int = 50):
        db = SessionLocal()
        try:
            repo = NewsRepository(db)
            return [{"id": n.id, "title": n.title, "description": n.description, "status": n.status, "link": n.link, "published": n.published, "source": n.source.name if n.source else "—", "image_url": n.image_url} for n in repo.get_all(limit)]
        finally:
            db.close()

    def list_news_for_user(self, user_id: int, limit: int = 100, source_name: str = None):
        db = SessionLocal()
        try:
            from database.models.user_game import UserGame
            
            # 1. Получаем список ID игр пользователя
            user_games = db.query(UserGame).filter(UserGame.user_id == user_id).all()
            game_ids = [ug.game_id for ug in user_games]
            
            # 2. Обращаемся к репозиторию. 
            # Если game_ids пустой (нет игр) - репозиторий вернет общие новости (где game_id = None)
            # Если source_name передан ("IGN", "Kotaku") - репозиторий отфильтрует по источнику
            repo = NewsRepository(db)
            news = repo.get_by_games_and_source(game_ids, source_name, limit)
            
            # 3. Форматируем результат для возврата в UI
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

    def change_status(self, news_id: int, new_status: str) -> dict:
        db = SessionLocal()
        try:
            repo = NewsRepository(db)
            news = repo.get_by_id(news_id)
            if not news: raise NotFoundError(f"Новость id={news_id} не найдена")
            NewsLifecycle.validate_transition(news.status, new_status)
            news.status = new_status
            db.commit()
            db.refresh(news)
            return {"success": True, "id": news.id, "status": news.status}
        finally:
            db.close()