from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp

class NewsCard(BoxLayout):
    news_id = NumericProperty(0)
    title = StringProperty("")
    description = StringProperty("")
    source = StringProperty("")
    published = StringProperty("")
    link = StringProperty("")
    image_url = StringProperty("")
    can_delete = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(150) 
        self.size_hint_x = 1
        self.padding = [dp(10), dp(10)]
        self.spacing = dp(10)

        with self.canvas.before:
            Color(0.12, 0.13, 0.17, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
        self.bind(pos=self._update_rect, size=self._update_rect)

        self._build_ui()

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _build_ui(self):
        img_container = BoxLayout(size_hint_x=None, width=dp(110))
        with img_container.canvas.before:
            Color(0.2, 0.2, 0.25, 1)
            RoundedRectangle(pos=img_container.pos, size=img_container.size, radius=[dp(8)])
        
        if self.image_url:
            img_container.add_widget(AsyncImage(source=self.image_url, allow_stretch=True, keep_ratio=False))
        else:
            img_container.add_widget(Label(text="NEWS", color=(0.5, 0.5, 0.5, 1), font_size=dp(12)))
            
        text_layout = BoxLayout(orientation="vertical", spacing=dp(5), size_hint_x=1)
        
        self.source_label = Label(text=self.source, halign="left", valign="middle", color=(0.5, 0.6, 0.9, 1), font_size=dp(11), size_hint_y=None, height=dp(20))
        self.source_label.bind(size=lambda s, v: setattr(s, "text_size", v))
        
        self.title_label = Label(text=self.title, bold=True, halign="left", valign="top", color=(0.95, 0.95, 1, 1), font_size=dp(13), size_hint_y=None, height=dp(45))
        self.title_label.bind(size=lambda s, v: setattr(s, "text_size", (v[0], None)))

        bottom = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(5))
        self.read_btn = Button(text="Читать", size_hint_x=None, width=dp(80), background_normal="", background_color=(0.2, 0.4, 0.7, 1), font_size=dp(11))
        self.read_btn.bind(on_release=lambda x: self._call_cb("on_read_callback"))
        
        self.fav_btn = Button(text="⭐", size_hint_x=None, width=dp(40), background_normal="", background_color=(0.8, 0.6, 0.2, 1), font_size=dp(14))
        self.fav_btn.bind(on_release=lambda x: self._call_cb("on_favorite_callback"))
        
        bottom.add_widget(self.read_btn)
        bottom.add_widget(self.fav_btn)
        
        if self.can_delete:
            self.delete_btn = Button(text="X", size_hint_x=None, width=dp(40), background_normal="", background_color=(0.5, 0.15, 0.15, 1), font_size=dp(12))
            self.delete_btn.bind(on_release=lambda x: self._call_cb("on_delete_callback"))
            bottom.add_widget(self.delete_btn)
            
        bottom.add_widget(Label())

        text_layout.add_widget(self.source_label)
        text_layout.add_widget(self.title_label)
        text_layout.add_widget(bottom)

        self.add_widget(img_container)
        self.add_widget(text_layout)

    def _call_cb(self, cb_name):
        cb = getattr(self, cb_name, None)
        if cb: cb(self.news_id)