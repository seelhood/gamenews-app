from database.session import SessionLocal
from database.repositories.favorite_repository import FavoriteRepository


class FavoriteService:
    def toggle(self, user_id: int, news_id: int):
        db = SessionLocal()
        try:
            repo = FavoriteRepository(db)
            if repo.is_favorite(user_id, news_id):
                repo.remove(user_id, news_id)
                return {"status": "removed"}
            repo.add(user_id, news_id)
            return {"status": "added"}
        finally:
            db.close()

    def list_user_favorites(self, user_id: int):
        db = SessionLocal()
        try:
            repo = FavoriteRepository(db)
            favs = repo.get_user_favorites(user_id)
            result = []
            for f in favs:
                if not f.news: # Если новость удалена, пропускаем
                    continue
                result.append({
                    "id": f.id, 
                    "news_id": f.news_id, 
                    "title": f.news.title,
                    "saved_title": f.saved_title,
                    "saved_text": f.saved_text,
                    "game_title": f.news.game.title if f.news.game else "Общие новости"
                })
            return result
        finally:
            db.close()