import threading
import time
import re
import html
from database.repositories.favorite_repository import FavoriteRepository
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.properties import StringProperty
from kivy.clock import Clock, mainthread
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.popup import Popup
from database.models.news import News
from database.models.favorite import Favorite
from database.session import SessionLocal
from database.repositories.news_repository import NewsRepository
from kivy.properties import StringProperty, ListProperty
from database.models.favorite import Favorite
import webbrowser
from kivy.clock import Clock
from database.repositories.news_repository import NewsRepository
from services.game_service import GameService
from services.news_service import NewsService
from services.stats_service import StatsService
from services.favorite_service import FavoriteService
from widgets.news_card import NewsCard
from deep_translator import MyMemoryTranslator
import socket


class NewsReaderPopup(ModalView):
    def __init__(self, title, text, image_url=None, link="", news_id=None, user_id=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.background_color = (0.08, 0.09, 0.12, 1)
        self.original_title = title
        self.original_text = text
        self.link = link
        self.news_id = news_id
        self.user_id = user_id
        self.is_translated = False
        
        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Верхние кнопки
        top_bar = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        back_btn = Button(text="← Назад", background_normal="", background_color=(0.2, 0.4, 0.7, 1))
        back_btn.bind(on_release=self.dismiss)
        
        self.link_btn = Button(text="🔗 Источник", background_normal="", background_color=(0.3, 0.3, 0.4, 1))
        self.link_btn.bind(on_release=lambda x: webbrowser.open(self.link) if self.link else None)
        
        fav_btn = Button(text="⭐ В избранное", background_normal="", background_color=(0.8, 0.6, 0.2, 1))
        fav_btn.bind(on_release=self.save_to_favorites)
        
        top_bar.add_widget(back_btn)
        top_bar.add_widget(self.link_btn)
        top_bar.add_widget(fav_btn)
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
            self._update_ui(self.original_title, f"Ошибка: {e}")

    @mainthread
    def _update_ui(self, new_title, new_text):
        self.title_lbl.text = new_title
        self.content.text = new_text
        self.trans_btn.disabled = False
        self.trans_btn.text = "🌐 Перевести еще раз"
        self.is_translated = True # <--- Запоминаем, что текст переведен

    def save_to_favorites(self, instance):
        if not self.news_id or not self.user_id:
            return
            
        # Если текст НЕ переведен, сохраняем как обычно
        if not self.is_translated:
            self._do_save(self.original_title, None)
            return

        # Если переведен - спрашиваем пользователя
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        content.add_widget(Label(text="Текст переведен. Какую версию сохранить?", font_size=dp(16)))
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        btn_orig = Button(text="Оригинал", background_color=(0.2, 0.4, 0.7, 1))
        btn_orig.bind(on_release=lambda x: (self._do_save(self.original_title, None), choice.dismiss()))
        
        btn_trans = Button(text="Перевод", background_color=(0.3, 0.6, 0.3, 1))
        btn_trans.bind(on_release=lambda x: (self._do_save(self.title_lbl.text, self.content.text), choice.dismiss()))
        
        btn_layout.add_widget(btn_orig)
        btn_layout.add_widget(btn_trans)
        content.add_widget(btn_layout)
        
        choice = Popup(title="Сохранение", content=content, size_hint=(0.7, 0.3))
        choice.open()

    def _do_save(self, title_to_save, text_to_save):
        db = SessionLocal()
        try:
            repo = FavoriteRepository(db)
            # Если уже в избранном - удаляем (toggle)
            if repo.is_favorite(self.user_id, self.news_id):
                repo.remove(self.user_id, self.news_id)
                self.show_msg("Удалено из избранного")
            else:
                # Сохраняем с кастомным текстом (если переведен)
                fav = Favorite(user_id=self.user_id, news_id=self.news_id, saved_title=title_to_save, saved_text=text_to_save)
                db.add(fav)
                db.commit()
                self.show_msg("Добавлено в избранное!")
        finally:
            db.close()

    def show_msg(self, text):
        popup = Popup(title="Инфо", content=Label(text=text), size_hint=(0.5, 0.2))
        popup.open()

class EditGamePopup(ModalView):
    def __init__(self, game_id, current_title, on_save, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.8, 0.4)
        self.game_id = game_id
        self.on_save = on_save
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        layout.add_widget(Label(text="Новое название игры:", font_size=dp(16)))
        
        self.input = TextInput(text=current_title, multiline=False, size_hint_y=None, height=dp(40), padding=[dp(10), dp(10)])
        layout.add_widget(self.input)
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        save_btn = Button(text="Сохранить", background_color=(0.3, 0.7, 0.4, 1))
        save_btn.bind(on_release=self.save)
        cancel_btn = Button(text="Отмена", background_color=(0.5, 0.2, 0.2, 1))
        cancel_btn.bind(on_release=self.dismiss)
        
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)
        self.add_widget(layout)

    def save(self, instance):
        new_title = self.input.text.strip()
        if new_title: self.on_save(self.game_id, new_title)
        self.dismiss()

# Добавь этот класс перед class MainScreen(Screen):
class GameFolder(BoxLayout):
    def __init__(self, game_title, cards, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, spacing=dp(10), **kwargs)
        # Привязываем высоту самой папки к её содержимому
        self.bind(minimum_height=self.setter('height'))
        
        self.is_open = True
        self.game_title = game_title
        
        # Кнопка-заголовок
        self.header = Button(
            text=f"▼ 🎮 {game_title}", 
            size_hint_y=None, height=dp(45),
            background_normal='', background_color=(0.15, 0.16, 0.22, 1),
            halign='left', valign='middle'
        )
        self.header.bind(size=lambda s, v: setattr(s, 'text_size', v))
        self.header.bind(on_release=self.toggle)
        self.add_widget(self.header)
        
        # Контейнер для новостей
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        # Привязываем высоту контейнера к его содержимому
        self.content.bind(minimum_height=self.content.setter('height'))
        
        for card in cards:
            self.content.add_widget(card)
            
        self.add_widget(self.content)

    def toggle(self, instance):
        self.is_open = not self.is_open
        
        if self.is_open:
            self.header.text = f"▼ 🎮 {self.game_title}"
            self.content.opacity = 1
            self.content.disabled = False
            
            # ВОЗВРАЩАЕМ ПРИВЯЗКУ: теперь контейнер снова считает высоту по карточкам
            self.content.bind(minimum_height=self.content.setter('height'))
            self.content.height = self.content.minimum_height
        else:
            self.header.text = f"▶ 🎮 {self.game_title}"
            self.content.opacity = 0
            self.content.disabled = True
            
            # ОТВЯЗЫВАЕМ: чтобы Kivy не мешал нам схлопнуть контейнер в 0
            self.content.unbind(minimum_height=self.content.setter('height'))
            self.content.height = 0

class MainScreen(Screen):
    current_section = StringProperty("news")
    current_filter = StringProperty("Все")
    bg_color = ListProperty([0.08, 0.09, 0.12, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ui = None
        self.is_admin = False
        self.current_filter = "Все"  # <--- ЗАМЕНИТЬ None НА "Все"
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
            
            # Вот тут выставляется роль
            if "settings_role" in self.ids:
                role_ru = "Администратор" if self.is_admin else "Пользователь"
                self.ids.settings_role.text = f"{role_ru}"
                
        self.show_section("news")
        self.update_stats()

    
    def show_section(self, name):
        self.current_section = name
        titles = {"news": "Лента новостей", "games": "Мои игры", "favorites": "Избранное", "settings": "Настройки"}
        if "section_title" in self.ids: self.ids.section_title.text = titles.get(name, "")

        for sec in ("news", "games", "favorites", "settings"):
            if f"{sec}_section" in self.ids:
                w = self.ids[f"{sec}_section"]
                if sec == name:
                    w.opacity = 1
                    w.disabled = False
                    w.size_hint_y = 1 # <--- Занимает всё место
                else:
                    w.opacity = 0
                    w.disabled = True
                    w.size_hint_y = None
                    w.height = 0 # <--- Схлопывается в ноль, чтобы не мешать кнопкам

        if name == "news": self.load_news()
        elif name == "games": self.load_games()
        elif name == "favorites": self.load_favorites()

    def filter_news(self, source_name):
        if source_name is None:
            self.current_filter = "Все"
        else:
            self.current_filter = source_name
        self.load_news()

    def load_news(self):
        if "news_list" not in self.ids: return
        self.ids.news_list.clear_widgets()
        user_id = self.ui.current_user["id"] if self.ui else None
        if not user_id: return

        news = self.news_service.list_news_for_user(user_id, limit=100, source_name=self.current_filter)
        if "status_label" in self.ids: self.ids.status_label.text = f"Новостей: {len(news)}"

        # --- ПРОВЕРКА НА ПУСТУЮ ЛЕНТУ ---
        if not news:
            lbl = Label(
                text="Новостей по вашим играм пока нет.\nПопробуйте добавить больше игр или нажать «Обновить».",
                size_hint_y=None,
                height=dp(200),
                halign="center",
                valign="middle",
                color=(0.6, 0.6, 0.7, 1),
                font_size=dp(16)
            )
            # Чтобы текст переносился на новую строку
            lbl.bind(size=lambda s, v: setattr(s, "text_size", v))
            self.ids.news_list.add_widget(lbl)
            return # Выходим, чтобы не запускать цикл ниже
        # ---------------------------------

        for n in news:
            card = NewsCard(
                news_id=n["id"], title=n["title"], description=n.get("description") or "", 
                source=n.get("source") or "—", published=n.get("published") or "", 
                link=n.get("link") or "", image_url=n.get("image_url") or "",
                can_delete=self.is_admin
            )
            card.on_read_callback = self._read_news
            card.on_delete_callback = self._delete_news
            card.on_favorite_callback = self._save_favorite
            self.ids.news_list.add_widget(card)

    def load_favorites(self):
        if "favorites_list" not in self.ids: return
        self.ids.favorites_list.clear_widgets()
        user_id = self.ui.current_user["id"] if self.ui else None
        if not user_id: return

        favs = self.favorite_service.list_user_favorites(user_id)
        
        if not favs:
            lbl = Label(text="В избранном пусто.\nНажмите ⭐ на новости.", size_hint_y=None, height=dp(300), halign="center", valign="middle", color=(0.6, 0.6, 0.7, 1), font_size=dp(16))
            lbl.bind(size=lambda s, v: setattr(s, "text_size", v))
            self.ids.favorites_list.add_widget(lbl)
            return

        # Просто выводим карточки по очереди, как в ленте
        for f in favs:
            display_title = f.get('saved_title') or f['title']
            
            # Защита от пустых заголовков (серый блок)
            if not display_title or not str(display_title).strip(): 
                continue 
                
            card = NewsCard(
                news_id=f['news_id'], 
                title=display_title, 
                description="Избранное", 
                source="⭐", 
                can_delete=True
            )
            card.on_read_callback = self._read_news
            card.on_delete_callback = self._remove_favorite
            self.ids.favorites_list.add_widget(card)

    def load_games(self):
        if "games_list" not in self.ids: return
        self.ids.games_list.clear_widgets()
        user_id = self.ui.current_user["id"] if self.ui else None
        if not user_id: return
        
        from database.session import SessionLocal
        from database.models.user_game import UserGame
        from database.models.game import Game
        
        db = SessionLocal()
        try:
            user_games = db.query(Game).join(UserGame).filter(UserGame.user_id == user_id).all()
            for g in user_games:
                row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
                
                # ВОТ ТУТ ЦЕНТРИРУЕМ ТЕКСТ
                lbl = Label(text=g.title, halign="center", valign="middle")
                lbl.bind(size=lambda s, v: setattr(s, "text_size", v))
                row.add_widget(lbl)
                
                edit_btn = Button(text="✎", size_hint_x=None, width=dp(40), background_normal="", background_color=(0.2, 0.5, 0.7, 1))
                edit_btn.bind(on_release=lambda x, gid=g.id, t=g.title: self._open_edit_game(gid, t))
                row.add_widget(edit_btn)
                
                del_btn = Button(text="X", size_hint_x=None, width=dp(40), background_normal="", background_color=(0.5, 0.15, 0.15, 1))
                del_btn.bind(on_release=lambda x, gid=g.id: self._remove_game(gid))
                row.add_widget(del_btn)
                
                self.ids.games_list.add_widget(row)
        finally:
            db.close()

    def _open_edit_game(self, game_id, current_title):
        EditGamePopup(game_id, current_title, self._save_edited_game).open()

    def _save_edited_game(self, game_id, new_title):
        result = self.game_service.update_game(game_id, new_title)
        if "error" in result: 
            self.show_msg(result["error"], is_error=True)
        else: 
            self.show_msg("Название игры обновлено!")
            self.load_games()
            self.load_news() # Обновляем ленту, чтобы новые новости подтянулись

    def _read_news(self, news_id):
        
        db = SessionLocal()
        try:
            n = NewsRepository(db).get_by_id(news_id)
            if n:
                user_id = self.ui.current_user["id"] if self.ui else None
                
                # --- ПРОВЕРКА НАЛИЧИЯ ПЕРЕВОДА В ИЗБРАННОМ ---
                fav = db.query(Favorite).filter(
                    Favorite.user_id == user_id, 
                    Favorite.news_id == news_id
                ).first()
                
                title_to_show = n.title
                text_to_show = n.description or "Текст отсутствует"
                
                # Если в избранном сохранен перевод, показываем его!
                if fav and fav.saved_title:
                    title_to_show = fav.saved_title
                if fav and fav.saved_text:
                    text_to_show = fav.saved_text
                # -----------------------------------------------

                # Очищаем текст от HTML (на случай, если это оригинал)
                clean_text = re.sub(r'<[^>]*>?', '', text_to_show)
                clean_text = html.unescape(clean_text)
                
                NewsReaderPopup(
                    title=title_to_show, 
                    text=clean_text, 
                    image_url=n.image_url, 
                    link=n.link, 
                    news_id=n.id, 
                    user_id=user_id
                ).open()
        finally:
            db.close()

    def add_game(self):
        title = self.ids.game_input.text.strip()
        if not title: return
        user_id = self.ui.current_user["id"] if self.ui else None
        
        result = self.game_service.create_game_for_user(user_id, title)
        
        if "error" in result:
            self.show_msg(result["error"], is_error=True)
        else:
            self.show_msg(f"Игра '{title}' добавлена!")
            
        self.ids.game_input.text = ""
        self.load_games()
        self.load_news()

    def _remove_game(self, game_id):
        from database.session import SessionLocal
        from database.models.user_game import UserGame
        user_id = self.ui.current_user["id"] if self.ui else None
        db = SessionLocal()
        try:
            db.query(UserGame).filter(UserGame.user_id == user_id, UserGame.game_id == game_id).delete()
            db.commit()
        finally:
            db.close()
        self.load_games()
        self.load_news()

    def _save_favorite(self, news_id):
        user_id = self.ui.current_user["id"] if self.ui else None
        if user_id:
            self.favorite_service.toggle(user_id, news_id)
            if "status_label" in self.ids: self.ids.status_label.text = "Сохранено!"

    def _remove_favorite(self, news_id):
        user_id = self.ui.current_user["id"] if self.ui else None
        if user_id:
            self.favorite_service.toggle(user_id, news_id)
            self.load_favorites()

    def refresh_news(self):
        # Проверка наличия интернета (подключаемся к DNS Google)
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            # Если интернет есть - запускаем парсер
            threading.Thread(target=self._parse_worker, daemon=True).start()
        except OSError:
            # Если интернета нет
            self.ids.status_label.text = "Офлайн-режим"
            self.show_msg("Нет подключения к интернету.\nПоказаны сохраненные новости.", is_error=True)
            self.load_news() # Просто загружаем то, что уже есть в БД

    def _parse_worker(self):
        try:
            from services.news_parser import sync_all_sources
            result = sync_all_sources()
            added = result.get("total_added", 0)
            self._on_refresh_done(added)
        except Exception as e:
            self._on_refresh_done(0, str(e))

    @mainthread
    def _on_refresh_done(self, added_count, error_msg=None):
        if error_msg:
            self.ids.status_label.text = "Ошибка обновления"
            self.show_msg(f"Ошибка парсера: {error_msg}", is_error=True)
        else:
            self.ids.status_label.text = f"Добавлено: {added_count}"
            # Показываем уведомление, как в UC-6
            if added_count > 0:
                self.show_msg(f"🔔 Найдены новые новости! ({added_count} шт.)\nПроверьте ленту.")
            else:
                self.show_msg("Новых новостей по вашим играм не найдено.")
        self.load_news()

    def search_news(self):
        query = self.ids.search_input.text.strip()
        if not query:
            self.load_news()
            return
        user_id = self.ui.current_user["id"] if self.ui else None
        news = self.news_service.search_news_for_user(user_id, query)
        self.ids.news_list.clear_widgets()
        for n in news:
            card = NewsCard(news_id=n["id"], title=n["title"], description=n.get("description") or "", source=n.get("source") or "—", published=n.get("published") or "", link=n.get("link") or "", image_url=n.get("image_url") or "", can_delete=self.is_admin)
            card.on_read_callback = self._read_news
            card.on_delete_callback = self._delete_news
            card.on_favorite_callback = self._save_favorite
            self.ids.news_list.add_widget(card)

    def _delete_news(self, news_id):
        from database.session import SessionLocal
        from database.repositories.news_repository import NewsRepository
        db = SessionLocal()
        try: NewsRepository(db).delete(news_id)
        finally: db.close()
        self.load_news()

    def update_stats(self):
        try:
            user_id = self.ui.current_user["id"] if (self.ui and self.ui.current_user) else None
            stats = StatsService().get_stats(user_id)
            if "stat_news" in self.ids: self.ids.stat_news.text = f"Новостей: {stats['news']}"
            if "stat_games" in self.ids: self.ids.stat_games.text = f"Игр: {stats['games']}"
        except Exception as e: print(f"Stats error: {e}")

    def toggle_theme(self):
        """Переключение светлой/темной темы фона"""
        if self.bg_color[0] < 0.5:
            # Включаем светлую
            self.bg_color = [0.9, 0.9, 0.95, 1]
            self.show_msg("Включена светлая тема")
        else:
            # Включаем темную
            self.bg_color = [0.08, 0.09, 0.12, 1]
            self.show_msg("Включена темная тема")

    def clear_cache(self):
        """Удаляет все новости из БД, КРОМЕ тех, что в избранном"""
        db = SessionLocal()
        try:
            # 1. Получаем ID всех новостей, которые находятся в избранном
            fav_ids = [f.news_id for f in db.query(Favorite.news_id).all()]
            
            # 2. Удаляем новости, которых нет в этом списке
            if fav_ids:
                deleted_count = db.query(News).filter(~News.id.in_(fav_ids)).delete(synchronize_session=False)
            else:
                # Если избранного нет вообще, удаляем все новости
                deleted_count = db.query(News).delete()
                
            db.commit()
            self.show_msg(f"Кэш очищен! Удалено новостей: {deleted_count}")
            
            # 3. Обновляем интерфейс
            self.load_news()
            self.update_stats()
            
        except Exception as e:
            db.rollback()
            self.show_msg(f"Ошибка очистки: {e}", is_error=True)
        finally:
            db.close()

    def show_msg(self, text, is_error=False):
        """Вспомогательный метод для показа всплывающих окон"""
        from kivy.uix.label import Label
        popup = Popup(
            title="Ошибка" if is_error else "Успех",
            content=Label(text=text),
            size_hint=(0.6, 0.3),
            title_color=(0.95, 0.35, 0.35, 1) if is_error else (0.30, 0.85, 0.50, 1)
        )
        popup.open()


    def logout(self):
        if self.auto_refresh_event: self.auto_refresh_event.cancel()
        if self.ui: self.ui.logout()
        self.manager.current = "login"