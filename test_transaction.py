"""
Тест транзакции: игра + связь с пользователем.
"""
import time

from services.game_service import GameService
from database.session import SessionLocal
from database.models.game import Game
from database.models.user_game import UserGame


def run():
    svc = GameService()

    print("=" * 55)
    print(" Тест транзакции")
    print("=" * 55)

    # 1. Успешное создание игры + связи
    print("\n[1] Создание игры + связи в одной транзакции")
    title = f"TestGame_{int(time.time()) % 100000}"
    result = svc.create_game_for_user(user_id=1, title=title, genre="RPG")
    print(f"    Результат: {result}")

    if result.get("success"):
        db = SessionLocal()
        try:
            game = db.query(Game).filter(Game.id == result["game_id"]).first()
            link = db.query(UserGame).filter(
                UserGame.game_id == game.id,
                UserGame.user_id == 1,
            ).first()
            print(f"    Game в БД:  {game}")
            print(f"    Связь в БД: {link}")
        finally:
            db.close()

    # 2. Имитация ошибки в транзакции
    print("\n[2] Имитация ошибки в транзакции")
    db = SessionLocal()
    try:
        g = Game(title="BrokenGame_TEMP", genre="Test")
        db.add(g)
        db.flush()
        raise RuntimeError("Что-то сломалось!")
    except Exception as e:
        db.rollback()
        print(f"    Ошибка: {e}")
        print(f"    Откат выполнен")
    finally:
        db.close()

    # 3. Проверка: BrokenGame НЕ должен сохраниться
    db = SessionLocal()
    try:
        broken = db.query(Game).filter(Game.title == "BrokenGame_TEMP").first()
        print(f"\n[3] BrokenGame в БД: {broken} (должно быть None)")
    finally:
        db.close()


if __name__ == "__main__":
    run()