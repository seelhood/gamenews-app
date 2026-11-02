import os
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.resources import resource_add_path

from screens.login_screen import LoginScreen
from screens.register_screen import RegisterScreen
from screens.main_screen import MainScreen

class GameNewsApp(App):
    def build(self):
        self.title = "GameNews"
        
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        resource_add_path(cur_dir)

        # ПРИНУДИТЕЛЬНО читаем KV-файлы в кодировке UTF-8
        with open("kv/login.kv", "r", encoding="utf-8") as f:
            Builder.load_string(f.read())
        with open("kv/register.kv", "r", encoding="utf-8") as f:
            Builder.load_string(f.read())
        with open("kv/main.kv", "r", encoding="utf-8") as f:
            Builder.load_string(f.read())

        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(MainScreen(name="main"))

        return sm

if __name__ == "__main__":
    GameNewsApp().run()