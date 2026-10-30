from database.session import SessionLocal
from database.repositories.game_repository import GameRepository
from database.models.game import Game
from database.models.user_game import UserGame


class GameService:
    def create_game(self, title: str, genre: str = None):
        db = SessionLocal()
        try:
            repo = GameRepository(db)
            if repo.get_by_title(title):
                return {"error": "Игра уже существует"}
            game = repo.create(title, genre)
            return {"id": game.id, "title": game.title, "genre": game.genre}
        finally:
            db.close()

    def create_game_for_user(self, user_id: int, title: str, genre: str = None):
        db = SessionLocal()
        try:
            from database.models.news import News
            from utils.translator import get_game_aliases
            
            repo = GameRepository(db)
            game = repo.get_by_title(title)
            
            if not game:
                game = Game(title=title, genre=genre)
                db.add(game)
                db.flush()

            existing_link = db.query(UserGame).filter(
                UserGame.user_id == user_id, 
                UserGame.game_id == game.id
            ).first()

            if existing_link:
                return {"error": "Игра уже добавлена"}

            link = UserGame(user_id=user_id, game_id=game.id)
            db.add(link)
            
            # --- АВТОМАТИЧЕСКАЯ ПРИВЯЗКА СТАРЫХ НОВОСТЕЙ ---
            # Ищем новости без игры и проверяем, подходят ли они под новую игру
            aliases = get_game_aliases(game.title)
            unlinked_news = db.query(News).filter(News.game_id.is_(None)).all()
            linked_count = 0
            
            for news in unlinked_news:
                full_text = (news.title + " " + (news.description or "")).lower()
                if any(alias in full_text for alias in aliases):
                    news.game_id = game.id
                    linked_count += 1
            
            db.commit()
            print(f"  [AUTO-LINK] К игре '{game.title}' привязано {linked_count} старых новостей из БД!")
            # ------------------------------------------------

            db.refresh(game)
            return {"success": True, "game_id": game.id, "title": game.title}
        except Exception as e:
            db.rollback()
            return {"error": f"Ошибка транзакции: {e}"}
        finally:
            db.close()

    def list_games(self):
        db = SessionLocal()
        try:
            repo = GameRepository(db)
            return [{"id": g.id, "title": g.title, "genre": g.genre} for g in repo.get_all()]
        finally:
            db.close()

    def search_games(self, query: str, limit: int = 5):
        from utils.translator import translate_query
        query = translate_query(query)
        db = SessionLocal()
        try:
            from database.models.game import Game
            if not query: return []
            results = db.query(Game).filter(Game.title.ilike(f"%{query}%")).limit(limit).all()
            return [g.title for g in results]
        finally:
            db.close()

    def update_game(self, game_id: int, new_title: str):
        db = SessionLocal()
        try:
            from database.models.news import News
            from utils.translator import get_game_aliases
            
            repo = GameRepository(db)
            # Проверяем, нет ли уже такой игры
            existing = repo.get_by_title(new_title)
            if existing and existing.id != game_id:
                return {"error": "Игра с таким названием уже существует"}
            
            success = repo.update(game_id, new_title)
            
            if success:
                # --- АВТО-ПРИВЯЗКА СТАРЫХ НОВОСТЕЙ ПО НОВОМУ НАЗВАНИЮ ---
                aliases = get_game_aliases(new_title)
                # Ищем новости, которые еще ни к чему не привязаны
                unlinked_news = db.query(News).filter(News.game_id.is_(None)).all()
                linked_count = 0
                for news in unlinked_news:
                    full_text = (news.title + " " + (news.description or "")).lower()
                    if any(alias in full_text for alias in aliases):
                        news.game_id = game_id
                        linked_count += 1
                db.commit()
                print(f"  [AUTO-LINK] При переименовании привязано {linked_count} новостей.")
                # --------------------------------------------------------
                
            return {"success": success}
        finally:
            db.close()

    def delete_game(self, game_id: int):
        db = SessionLocal()
        try:
            repo = GameRepository(db)
            return {"success": repo.delete(game_id)}
        finally:
            db.close()