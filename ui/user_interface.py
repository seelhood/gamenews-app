"""Интерфейс для работы с пользователями (регистрация, вход, выход)."""
from database.session import SessionLocal
from database.repositories.user_repository import UserRepository


class UserInterface:
    def __init__(self):
        self.current_user = None

    def register(self, username: str, email: str, password: str) -> dict:
        db = SessionLocal()
        try:
            repo = UserRepository(db)
            if repo.get_by_username(username):
                return {"success": False, "error": "Логин занят"}
            if repo.get_by_email(email):
                return {"success": False, "error": "Email занят"}
            user = repo.create(username, email, password)
            return {"success": True, "user_id": user.id}
        finally:
            db.close()

    def login(self, username: str, password: str) -> dict:
        db = SessionLocal()
        try:
            repo = UserRepository(db)
            user = repo.authenticate(username, password)
            if not user:
                return {"success": False, "error": "Неверный логин или пароль"}
            
            # ВОТ ЗДЕСЬ МЫ ДОБАВИЛИ ПОЛЕ ROLE
            self.current_user = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": getattr(user, "role", "user") # Безопасный доступ, если вдруг колонки нет в БД
            }
            return {"success": True, "user": self.current_user}
        finally:
            db.close()

    def logout(self):
        self.current_user = None
        return {"success": True}

    def is_authenticated(self) -> bool:
        return self.current_user is not None