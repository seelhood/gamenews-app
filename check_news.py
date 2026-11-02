from database.session import SessionLocal
from database.models.user import User
from database.models.user_game import UserGame
from database.models.news import News
from database.models.game import Game

def check():
    db = SessionLocal()
    try:
        # Ищем пользователя Seelhood
        user = db.query(User).filter(User.username == "Seelhood").first()
        if not user:
            print("❌ Пользователь Seelhood не найден в базе!")
            return
        
        print(f"👤 Пользователь: {user.username} (ID: {user.id})")
        
        # Ищем игры этого пользователя
        user_games = db.query(Game).join(UserGame).filter(UserGame.user_id == user.id).all()
        if not user_games:
            print("❌ У этого пользователя НЕТ добавленных игр!")
            return
            
        print(f"🎮 Игры пользователя: {[g.title for g in user_games]}")
        
        # Считаем новости для этих игр
        game_ids = [g.id for g in user_games]
        news_count = db.query(News).filter(News.game_id.in_(game_ids)).count()
        print(f"📰 Всего новостей для этих игр: {news_count}")
        
        # Показываем пару заголовков для проверки
        news_sample = db.query(News).filter(News.game_id.in_(game_ids)).limit(3).all()
        for n in news_sample:
            print(f"   - {n.title[:50]}... (game_id: {n.game_id})")
            
    finally:
        db.close()

if __name__ == "__main__":
    check()