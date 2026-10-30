from kivy.uix.screenmanager import Screen
from ui.user_interface import UserInterface


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ui = UserInterface()

    def do_login(self):
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()

        if not username or not password:
            self.ids.status_label.text = "Заполните все поля"
            return

        result = self.ui.login(username, password)

        if result.get("success"):
            self.ids.status_label.text = ""
            main = self.manager.get_screen("main")
            main.set_ui(self.ui)
            self.manager.current = "main"
        else:
            self.ids.status_label.text = result.get("error", "Ошибка входа")

    def go_to_register(self):
        self.ids.username_input.text = ""
        self.ids.password_input.text = ""
        self.ids.status_label.text = ""
        self.manager.current = "register"