"""Консольный интерфейс для тестирования User."""
from ui.user_interface import UserInterface


def main():
    ui = UserInterface()

    while True:
        print("\n=== GameNews: Пользователи ===")
        print("1. Регистрация")
        print("2. Вход")
        print("3. Выход из аккаунта")
        print("4. Статус")
        print("0. Выйти из программы")
        choice = input("Выбор: ").strip()

        if choice == "1":
            u = input("Логин: ")
            e = input("Email: ")
            p = input("Пароль: ")
            print(ui.register(u, e, p))

        elif choice == "2":
            u = input("Логин: ")
            p = input("Пароль: ")
            print(ui.login(u, p))

        elif choice == "3":
            print(ui.logout())

        elif choice == "4":
            if ui.is_authenticated():
                print(f"Вы вошли как: {ui.current_user['username']}")
            else:
                print("Вы не авторизованы")

        elif choice == "0":
            break


if __name__ == "__main__":
    main()