
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from database.init_db import init_db
from screens.login_screen import LoginScreen
from screens.register_screen import RegisterScreen
from screens.main_screen import MainScreen


class GameNewsApp(App):
    def build(self):
        self.title = "GameNews"

        init_db()

        Builder.load_file("kv/login.kv")
        Builder.load_file("kv/register.kv")
        Builder.load_file("kv/main.kv")

        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(MainScreen(name="main"))

        return sm


if __name__ == "__main__":
    GameNewsApp().run()