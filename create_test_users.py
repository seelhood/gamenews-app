from database.session import SessionLocal
from database.models.user import User
from utils.security import hash_password

def create_users():
    db = SessionLocal()
    try:
        # --- 1. Создаем админа Peche4ka ---
        user_admin = db.query(User).filter(User.username == "Peche4ka").first()
        if not user_admin:
            user_admin = User(
                username="Peche4ka",
                email="peche4ka@example.com", # Заглушка для email, т.к. поле unique
                password_hash=hash_password("369gmail.com"),
                role="admin"
            )
            db.add(user_admin)
            print("Создан пользователь Peche4ka (Админ)")
        else:
            user_admin.password_hash = hash_password("369gmail.com")
            user_admin.role = "admin"
            print("Обновлен пользователь Peche4ka (Админ)")

        # --- 2. Создаем обычного пользователя Seelhood ---
        user_regular = db.query(User).filter(User.username == "Seelhood").first()
        if not user_regular:
            user_regular = User(
                username="Seelhood",
                email="seelhood@example.com", # Заглушка для email
                password_hash=hash_password("349gmail.com"),
                role="user"
            )
            db.add(user_regular)
            print("Создан пользователь Seelhood (Пользователь)")
        else:
            user_regular.password_hash = hash_password("349gmail.com")
            user_regular.role = "user"
            print("Обновлен пользователь Seelhood (Пользователь)")

        db.commit()
        print("\n[OK] Пользователи успешно сохранены в базу данных!")

    except Exception as e:
        db.rollback()
        print(f"[ОШИБКА] Не удалось создать пользователей: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_users()