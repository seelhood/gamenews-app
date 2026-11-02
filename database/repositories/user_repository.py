from sqlalchemy.orm import Session
from database.models.user import User
from utils.security import hash_password, verify_password
from utils.security import hash_password, verify_password

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, username: str, email: str, password: str) -> User:
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_by_id(self, user_id: int):
        return self.session.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str):
        return self.session.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str):
        return self.session.query(User).filter(User.email == email).first()

    def authenticate(self, username: str, password: str):
        user = self.get_by_username(username)
        if not user:
            return None

        # 1. Пробуем проверить через новый bcrypt
        if verify_password(password, user.password_hash):
            return user

        # 2. Если не вышло, проверяем, может это старый пароль (SHA-256)
        import hashlib
        old_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if old_hash == user.password_hash:
            # Если старый пароль подошел — автоматически обновляем его на bcrypt
            user.password_hash = hash_password(password)
            self.session.commit()
            return user

        return None

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if not user:
            return False
        self.session.delete(user)
        self.session.commit()
        return True