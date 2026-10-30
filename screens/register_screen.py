from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from ui.user_interface import UserInterface


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ui = UserInterface()

    def do_register(self):
        username = self.ids.username_input.text.strip()
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text.strip()

        if not username or not email or not password:
            self.ids.status_label.text = "Заполните все поля"
            return

        result = self.ui.register(username, email, password)

        if result.get("success"):
            self.ids.status_label.text = "Регистрация успешна! Войдите."
            Clock.schedule_once(self._go_to_login, 1.5)
        else:
            self.ids.status_label.text = result.get("error", "Ошибка")

    def _go_to_login(self, dt):
        self.ids.username_input.text = ""
        self.ids.email_input.text = ""
        self.ids.password_input.text = ""
        self.ids.status_label.text = ""
        self.manager.current = "login"

    def go_to_login(self):
        self.manager.current = "login"