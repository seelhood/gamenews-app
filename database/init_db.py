from database.connection import engine
from database.base import Base

# Импорт моделей — обязателен для регистрации в Base.metadata
from database.models import user, game, news, favorite, source, user_game, tag  # noqa


def init_db():
    Base.metadata.create_all(bind=engine)
    print("[OK] Таблицы созданы")


if __name__ == "__main__":
    init_db()