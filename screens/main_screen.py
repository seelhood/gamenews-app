import threading
import time
import re
import html
import webbrowser
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.properties import StringProperty, ListProperty
from kivy.clock import Clock, mainthread
from kivy.metrics import dp
from kivy.uix.popup import Popup

from services.game_service import GameService
from services.news_service import NewsService
from services.favorite_service import FavoriteService
from widgets.news_card import NewsCard
from deep_translator import MyMemoryTranslator

class NewsReaderPopup(ModalView):
    def __init__(self, title, text, image_url=None, link="", news_id=None, token=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.background_color = (0.08, 0.09, 0.12, 1)
        self.original_title = title
        self.original_text = text
        self.link = link
        self.news_id = news_id
        self.token = token
        self.is_translated = False

        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        top_bar = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        back_btn = Button(text="← Назад", background_normal="", background_color=(0.2, 0.4, 0.7, 1))
        back_btn.bind(on_release=self.dismiss)
        link_btn = Button(text="🔗 Источник", background_normal="", background_color=(0.3, 0.3, 0.4, 1))
        link_btn.bind(on_release=lambda x: webbrowser.open(self.link) if self.link else None)
        fav_btn = Button(text="⭐ В избранное", background_normal="", background_color=(0.8, 0.6, 0.2, 1))
        fav_btn.bind(on_release=self.save_to_favorites)
        top_bar.add_widget(back_btn); top_bar.add_widget(link_btn); top_bar.add_widget(fav_btn)
        self.layout.add_widget(top_bar)

        if image_url:
            img = AsyncImage(source=image_url, size_hint_y=None, height=dp(200), allow_stretch=True, keep_ratio=False)
            self.layout.add_widget(img)

        self.title_lbl = Label(text=title, font_size=dp(20), bold=True, size_hint_y=None, text_size=(self.width - dp(40), None))
        self.title_lbl.bind(size=lambda s, v: setattr(s, "text_size", v))
        self.layout.add_widget(self.title_lbl)

        scroll = ScrollView(size_hint=(1, 1))
        self.content = Label(text=text, font_size=dp(16), size_hint_y=None)
        self.content.bind(width=lambda s, v: setattr(s, "text_size", (v, None)))
        self.content.bind(texture_size=self.content.setter('size'))
        scroll.add_widget(self.content)
        self.layout.add_widget(scroll)

        self.trans_btn = Button(text="🌐 Перевести на русский", size_hint_y=None, height=dp(50), background_normal="", background_color=(0.3, 0.6, 0.3, 1))
        self.trans_btn.bind(on_release=self.translate)
        self.layout.add_widget(self.trans_btn)
        self.add_widget(self.layout)

    def translate(self, instance):
        self.trans_btn.disabled = True
        self.trans_btn.text = "Перевод..."
        threading.Thread(target=self._do_translate, daemon=True).start()

    def _do_translate(self):
        try:
            translator = MyMemoryTranslator(source='english', target='russian')
            translated_title = translator.translate(self.original_title[:490])
            time.sleep(1)
            text = self.original_text
            chunks = [text[i:i+490] for i in range(0, len(text), 490)]
            translated_chunks = [translator.translate(chunk) for chunk in chunks if chunk.strip()]
            final_text = " ".join(translated_chunks)
            self._update_ui(translated_title, final_text)
        except Exception as e:
            self._update_ui(self.original_title, f"Ошибка перевода: {e}")

    @mainthread
    def _update_ui(self, new_title, new_text):
        self.title_lbl.text = new_title
        self.content.text = new_text
        self.trans_btn.disabled = False
        self.trans_btn.text = "🌐 Перевести еще раз"
        self.is_translated = True

    def save_to_favorites(self, instance):
        if not self.news_id or not self.token: return
        if not self.is_translated:
            res = FavoriteService().toggle(self.token, self.news_id)
            self._show_msg("Добавлено в избранное" if res == "added" else "Удалено из избранного")
            return
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        content.add_widget(Label(text="Текст переведен. Какую версию сохранить?", font_size=dp(16)))
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        btn_orig = Button(text="Оригинал", background_color=(0.2, 0.4, 0.7, 1))
        btn_orig.bind(on_release=lambda x: (self._do_save(self.original_title, None), choice.dismiss()))
        btn_trans = Button(text="Перевод", background_color=(0.3, 0.6, 0.3, 1))
        btn_trans.bind(on_release=lambda x: (self._do_save(self.title_lbl.text, self.content.text), choice.dismiss()))
        btn_layout.add_widget(btn_orig); btn_layout.add_widget(btn_trans)
        content.add_widget(btn_layout)
        choice = Popup(title="Сохранение", content=content, size_hint=(0.7, 0.3))
        choice.open()

    def _do_save(self, title, text):
        res = FavoriteService().toggle(self.token, self.news_id, saved_title=title, saved_text=text)
        self._show_msg("Сохранено!" if res == "added" else "Удалено из избранного")

    def _show_msg(self, text):
        Popup(title="Инфо", content=Label(text=text), size_hint=(0.5, 0.2)).open()


class MainScreen(Screen):
    current_section = StringProperty("news")
    bg_color = ListProperty([0.08, 0.09, 0.12, 1])
    current_filter = StringProperty("Все")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ui = None
        self.is_admin = False
        self.game_service = GameService()
        self.news_service = NewsService()
        self.favorite_service = FavoriteService()
        self.auto_refresh_event = None

    def set_ui(self, ui):
        self.ui = ui
        if "user_info" in self.ids and ui.current_user:
            self.ids.user_info.text = f"Привет, {ui.current_user['username']}!"
            self.is_admin = (ui.current_user.get('role') == 'admin')
            if "settings_username" in self.ids:
                self.ids.settings_username.text = ui.current_user['username']
            if "settings_email" in self.ids:
                self.ids.settings_email.text = ui.current_user.get('email', '—')
            if "settings_role" in self.ids:
                role_ru = "Администратор" if self.is_admin else "Пользователь"
                self.ids.settings_role.text = role_ru
        self.show_section("news")
        self.update_stats()

    def show_section(self, name):
        self.current_section = name
        titles = {"news": "Лента новостей", "games": "Мои игры", "favorites": "Избранное", "settings": "Настройки"}
        if "section_title" in self.ids:
            self.ids.section_title.text = titles.get(name, "")
        for sec in ("news", "games", "favorites", "settings"):
            if f"{sec}_section" in self.ids:
                w = self.ids[f"{sec}_section"]
                if sec == name:
                    w.opacity = 1
                    w.disabled = False
                    w.size_hint_y = 1
                else:
                    w.opacity = 0
                    w.disabled = True
                    w.size_hint_y = None
                    w.height = 0
        if name == "news": self.load_news()
        elif name == "games": self.load_games()
        elif name == "favorites": self.load_favorites()

    def filter_news(self, source_name):
        self.current_filter = "Все" if source_name is None else source_name
        self.load_news()

    def load_news(self):
        if "news_list" not in self.ids: return
        self.ids.news_list.clear_widgets()
        if not self.ui or not self.ui.token: return
        news = self.news_service.list_news_for_user(self.ui.token, limit=100, source_name=self.current_filter)
        if "status_label" in self.ids:
            self.ids.status_label.text = f"Новостей: {len(news)}"
        if not news:
            lbl = Label(text="Новостей по вашим играм пока нет.\nДобавьте игры или нажмите «Обновить».",
                        size_hint_y=None, height=dp(200), halign="center", valign="middle",
                        color=(0.6, 0.6, 0.7, 1), font_size=dp(16))
            lbl.bind(size=lambda s, v: setattr(s, "text_size", v))
            self.ids.news_list.add_widget(lbl)
            return
        for n in news:
            card = NewsCard(news_id=n["id"], title=n["title"], description=n.get("description") or "",
                            source=n.get("source") or "—", published=n.get("published") or "",
                            link=n.get("link") or "", image_url=n.get("image_url") or "",
                            can_delete=self.is_admin)
            card.on_read_callback = self._read_news
            card.on_delete_callback = self._delete_news
            card.on_favorite_callback = self._save_favorite
            self.ids.news_list.add_widget(card)

    def load_games(self):
        if "games_list" not in self.ids: return
        self.ids.games_list.clear_widgets()
        if not self.ui or not self.ui.token: return
        games = self.game_service.list_games(self.ui.token)
        
        if not isinstance(games, list):
            self.show_msg("Ошибка загрузки игр", is_error=True)
            return

        for g in games:
            title = g.get("title", "Без названия") if isinstance(g, dict) else "Ошибка"
            row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
            lbl = Label(text=title, halign="center", valign="middle")
            lbl.bind(size=lambda s, v: setattr(s, "text_size", v))
            row.add_widget(lbl)
            del_btn = Button(text="X", size_hint_x=None, width=dp(40), background_normal="", background_color=(0.5, 0.15, 0.15, 1))
            game_id = g.get("id") if isinstance(g, dict) else None
            if game_id:
                del_btn.bind(on_release=lambda x, gid=game_id: self._remove_game(gid))
            row.add_widget(del_btn)
            self.ids.games_list.add_widget(row)

    def load_favorites(self):
        if "favorites_list" not in self.ids: return
        self.ids.favorites_list.clear_widgets()
        if not self.ui or not self.ui.token: return
        favs = self.favorite_service.list_user_favorites(self.ui.token)
        if not favs:
            lbl = Label(text="В избранном пусто.\nНажмите ⭐ на новости.", size_hint_y=None, height=dp(300),
                        halign="center", valign="middle", color=(0.6, 0.6, 0.7, 1), font_size=dp(16))
            lbl.bind(size=lambda s, v: setattr(s, "text_size", v))
            self.ids.favorites_list.add_widget(lbl)
            return
        for f in favs:
            title = f.get("saved_title") or f.get("news_title", "Без названия")
            card = NewsCard(news_id=f["news_id"], title=title, description="Избранное", source="⭐", can_delete=True)
            card.on_read_callback = self._read_news
            card.on_delete_callback = self._remove_favorite
            self.ids.favorites_list.add_widget(card)

    def _read_news(self, news_id):
        if not self.ui or not self.ui.token: return
        n = self.news_service.get_news_detail(self.ui.token, news_id)
        if n and isinstance(n, dict):
            title = n.get("title", "Без названия")
            raw_text = n.get("description") or "Текст отсутствует"
            img_url = n.get("image_url")
            if img_url and not str(img_url).startswith("http"): img_url = None
            clean = re.sub(r'<[^>]*>?', '', raw_text)
            clean = html.unescape(clean)
            NewsReaderPopup(title=title, text=clean, image_url=img_url,
                            link=n.get("link", ""), news_id=n.get("id"), token=self.ui.token).open()
        else:
            self.show_msg("Не удалось загрузить новость", is_error=True)

    def add_game(self):
        title = self.ids.game_input.text.strip()
        if not title or not self.ui or not self.ui.token: return
        res = self.game_service.create_game_for_user(self.ui.token, title)
        if "error" in res:
            self.show_msg(res["error"], is_error=True)
        else:
            self.show_msg(f"Игра '{title}' добавлена!")
        self.ids.game_input.text = ""
        self.load_games()
        self.load_news()
        self.update_stats()

    def _remove_game(self, game_id):
        if not self.ui or not self.ui.token: return
        self.game_service.delete_game(self.ui.token, game_id)
        self.load_games()
        self.load_news()
        self.update_stats()

    def _save_favorite(self, news_id):
        if not self.ui or not self.ui.token: return
        self.favorite_service.toggle(self.ui.token, news_id)
        if "status_label" in self.ids: self.ids.status_label.text = "Сохранено!"

    def _remove_favorite(self, news_id):
        if not self.ui or not self.ui.token: return
        self.favorite_service.toggle(self.ui.token, news_id)
        self.load_favorites()

    def refresh_news(self):
        self.ids.status_label.text = "Загрузка с сервера..."
        self.load_news()

    def search_news(self):
        query = self.ids.search_input.text.strip()
        if not query:
            self.load_news()
            return
        if not self.ui or not self.ui.token: return
        news = self.news_service.search_news_for_user(self.ui.token, query)
        self.ids.news_list.clear_widgets()
        for n in news:
            card = NewsCard(news_id=n["id"], title=n["title"], description=n.get("description") or "",
                            source=n.get("source") or "—", published=n.get("published") or "",
                            link=n.get("link") or "", image_url=n.get("image_url") or "",
                            can_delete=self.is_admin)
            card.on_read_callback = self._read_news
            card.on_delete_callback = self._delete_news
            card.on_favorite_callback = self._save_favorite
            self.ids.news_list.add_widget(card)

    def _delete_news(self, news_id):
        self.load_news()

    def update_stats(self):
        if not self.ui or not self.ui.token: return
        games = self.game_service.list_games(self.ui.token)
        news = self.news_service.list_news_for_user(self.ui.token, limit=1000)
        if "stat_news" in self.ids: self.ids.stat_news.text = f"Новостей: {len(news)}"
        if "stat_games" in self.ids: self.ids.stat_games.text = f"Игр: {len(games)}"

    def toggle_theme(self):
        if self.bg_color[0] < 0.5:
            self.bg_color = [0.9, 0.9, 0.95, 1]
            self.show_msg("Включена светлая тема")
        else:
            self.bg_color = [0.08, 0.09, 0.12, 1]
            self.show_msg("Включена темная тема")

    def clear_cache(self):
        self.show_msg("Кэш мобильного клиента пуст. Данные загружаются с сервера.")

    def show_msg(self, text, is_error=False):
        popup = Popup(title="Ошибка" if is_error else "Успех",
                      content=Label(text=text),
                      size_hint=(0.6, 0.3),
                      title_color=(0.95, 0.35, 0.35, 1) if is_error else (0.30, 0.85, 0.50, 1))
        popup.open()

    def logout(self):
        if self.auto_refresh_event: self.auto_refresh_event.cancel()
        if self.ui: self.ui.logout()
        self.manager.current = "login"
