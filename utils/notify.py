"""
Уведомления: попап + статус-строка.
"""
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.metrics import dp


def show_error(message: str, title: str = "Ошибка"):
    """Показывает всплывающее окно с ошибкой."""
    Popup(
        title=title,
        content=Label(text=message),
        size_hint=(0.6, 0.3),
        title_color=(0.95, 0.35, 0.35, 1),
    ).open()


def show_success(message: str, title: str = "Готово"):
    """Успех."""
    Popup(
        title=title,
        content=Label(text=message),
        size_hint=(0.6, 0.3),
        title_color=(0.30, 0.85, 0.50, 1),
    ).open()