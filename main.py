#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STUDEX (Kivy versiyasi) — IELTS tayyorlov ilovasi, Android APK sifatida
yig'ish uchun mo'ljallangan.

Bu fayl asl STUDEX.py (Tkinter, faqat PC uchun) ilovaning Kivy'ga
qayta yozilgan versiyasi. Barcha mantiq (bo'limlar, lug'at, Jo'rabek AI,
IELTS Speaking simulyatori) saqlanib qolgan, faqat interfeys mobil
qurilmalar uchun Kivy widgetlari bilan qurilgan.
"""

import functools
import threading
import uuid

from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

import data
import ai
import storage

APP_NAME = "Studex"

GRADIENT_TOP = (214, 245, 224)
GRADIENT_BOTTOM = (255, 255, 255)

SECTIONS = [
    ("Grammar", "Grammar", "Grammatika mashqlari"),
    ("Vocabulary", "Vocabulary", "Lug'at boyligi"),
    ("Reading", "Reading", "O'qish mashqlari"),
    ("Listening", "Listening", "Tinglash mashqlari"),
    ("Writing", "Writing", "Yozish mashqlari"),
    ("Speaking", "Speaking", "Gapirish mashqlari"),
]


def make_gradient_texture(top_rgb, bottom_rgb, height=256):
    """Yashil-oq vertikal gradient texture yasaydi (asl ilovadagi
    GradientCanvas o'rniga)."""
    buf = bytearray()
    for i in range(height):
        t = i / float(height - 1)
        r = int(top_rgb[0] + (bottom_rgb[0] - top_rgb[0]) * t)
        g = int(top_rgb[1] + (bottom_rgb[1] - top_rgb[1]) * t)
        b = int(top_rgb[2] + (bottom_rgb[2] - top_rgb[2]) * t)
        buf += bytes([r, g, b, 255])
    texture = Texture.create(size=(1, height), colorfmt="rgba")
    texture.blit_buffer(bytes(buf), colorfmt="rgba", bufferfmt="ubyte")
    texture.wrap = "clamp_to_edge"
    return texture


def set_bg(screen):
    app = App.get_running_app()
    screen.ids.bg_image.texture = app.gradient_texture


# ---------------------------------------------------------------------------
# HOME
# ---------------------------------------------------------------------------
class HomeScreen(Screen):
    def on_pre_enter(self, *args):
        set_bg(self)
        grid = self.ids.section_grid
        if not grid.children:
            for name, icon, desc in SECTIONS:
                card = Factory.SectionCard()
                card.name = name
                card.icon = icon
                card.desc = desc
                card.press_callback = functools.partial(self.open_section, name)
                grid.add_widget(card)

    def open_section(self, name):
        app = App.get_running_app()
        if name == "Vocabulary":
            self.manager.current = "vocabulary"
        elif name == "Speaking":
            app.configure_chat_screen(mode="speaking")
            self.manager.current = "chat"
        else:
            app.configure_placeholder_screen(name)
            self.manager.current = "placeholder"

    def open_jorabek(self):
        app = App.get_running_app()
        app.configure_chat_screen(mode="jorabek")
        self.manager.current = "chat"


# ---------------------------------------------------------------------------
# PLACEHOLDER (Grammar / Reading / Listening / Writing — "tez orada")
# ---------------------------------------------------------------------------
class PlaceholderScreen(Screen):
    def on_pre_enter(self, *args):
        set_bg(self)
        self.ids.topbar.back_callback = self.go_home

    def go_home(self):
        self.manager.current = "home"


# ---------------------------------------------------------------------------
# VOCABULARY (A1-A2 / B1-B2 / C1-C2 + General Dictionary)
# ---------------------------------------------------------------------------
class VocabularyScreen(Screen):
    LEVELS = [
        ("A1-A2: Beginner-Elementary", data.VOCABULARY_DATA),
        ("B1-B2: Intermediate", data.VOCAB_B1_B2),
        ("C1-C2: Advanced", data.VOCAB_C1_C2),
    ]

    def on_pre_enter(self, *args):
        set_bg(self)
        self.ids.topbar.title_text = "Vocabulary"
        self.ids.topbar.back_callback = self.go_home
        box = self.ids.level_buttons
        if not box.children:
            for title, dataset in self.LEVELS:
                btn = Button(
                    text=title,
                    background_normal="",
                    background_color=(1, 1, 1, 1),
                    color=get_color_from_hex("#1b5e20"),
                    bold=True,
                    font_size="15sp",
                )
                btn.bind(on_release=functools.partial(self.open_level, title, dataset))
                box.add_widget(btn)

    def go_home(self):
        self.manager.current = "home"

    def open_level(self, title, dataset, *args):
        app = App.get_running_app()
        app.configure_subsection_screen(title, dataset)
        self.manager.current = "subsection"

    def open_dictionary(self):
        self.manager.current = "dictionary"


# ---------------------------------------------------------------------------
# SUBSECTION (level ichidagi "Flashcard" tugmasi)
# ---------------------------------------------------------------------------
class SubsectionScreen(Screen):
    title_text = ""
    dataset = None

    def on_pre_enter(self, *args):
        set_bg(self)
        self.ids.topbar.title_text = self.title_text
        self.ids.topbar.back_callback = self.go_back

    def go_back(self):
        self.manager.current = "vocabulary"

    def open_flashcards(self):
        app = App.get_running_app()
        app.configure_flashcard_screen(self.title_text, self.dataset)
        self.manager.current = "flashcard"


# ---------------------------------------------------------------------------
# FLASHCARD
# ---------------------------------------------------------------------------
class FlashcardScreen(Screen):
    title_text = ""
    dataset = None
    index = 0

    def on_pre_enter(self, *args):
        set_bg(self)
        self.ids.topbar.title_text = self.title_text
        self.ids.topbar.back_callback = self.go_back
        self.index = 0
        self.update_card()

    def go_back(self):
        self.manager.current = "subsection"

    def update_card(self):
        if not self.dataset:
            self.ids.lbl_word.text = "So'zlar topilmadi"
            self.ids.lbl_trans.text = ""
            self.ids.lbl_level.text = ""
            self.ids.lbl_example.text = ""
            return
        item = self.dataset[self.index]
        self.ids.lbl_word.text = item["word"]
        self.ids.lbl_trans.text = f"Tarjimasi: {item['translation']}"
        self.ids.lbl_level.text = f"Daraja: {item['level']}  ({self.index + 1}/{len(self.dataset)})"
        self.ids.lbl_example.text = f"Example: {item['example']}"

    def next_card(self):
        if not self.dataset:
            return
        self.index = (self.index + 1) % len(self.dataset)
        self.update_card()

    def prev_card(self):
        if not self.dataset:
            return
        self.index = (self.index - 1) % len(self.dataset)
        self.update_card()

    def play_audio(self):
        if self.dataset:
            storage.speak_word(self.dataset[self.index]["word"])


# ---------------------------------------------------------------------------
# GENERAL DICTIONARY
# ---------------------------------------------------------------------------
class DictionaryScreen(Screen):
    def on_pre_enter(self, *args):
        set_bg(self)
        self.ids.topbar.title_text = "General Dictionary"
        self.ids.topbar.back_callback = self.go_back
        self.filtered = list(data.VOCABULARY_DATA)
        self.selected_word = None
        self.populate_list()

    def go_back(self):
        self.manager.current = "vocabulary"

    def on_search_change(self, text):
        self.populate_list(text)

    def populate_list(self, filter_text=""):
        word_list = self.ids.word_list
        word_list.clear_widgets()
        self.filtered = [
            d for d in data.VOCABULARY_DATA if filter_text.lower() in d["word"].lower()
        ]
        for item in self.filtered:
            btn = Button(
                text=f"{item['word']} ({item['level']})",
                size_hint_y=None,
                height=dp(40),
                background_normal="",
                background_color=(1, 1, 1, 1),
                color=get_color_from_hex("#1b5e20"),
                halign="left",
            )
            btn.bind(on_release=functools.partial(self.select_item, item))
            word_list.add_widget(btn)

    def select_item(self, item, *args):
        self.selected_word = item
        self.ids.det_word.text = item["word"]
        self.ids.det_trans.text = f"Tarjimasi: {item['translation']}"
        self.ids.det_example.text = f"Example: {item['example']}"
        self.ids.det_audio_btn.disabled = False

    def play_selected_audio(self):
        if self.selected_word:
            storage.speak_word(self.selected_word["word"])

    def ask_ai_for_word(self):
        word = self.ids.search_input.text.strip()
        if not word:
            return

        self.ids.det_word.text = word
        self.ids.det_trans.text = "AI'dan so'ralyapti, kuting..."
        self.ids.det_example.text = ""
        self.ids.det_audio_btn.disabled = True

        prompt = ai.DICTIONARY_LOOKUP_PROMPT_TEMPLATE.format(word=word)

        def worker():
            answer, error = ai.get_jorabek_response(
                [{"role": "user", "content": prompt}], temperature=0
            )

            def update_ui(_dt):
                if error:
                    self.ids.det_trans.text = f"Xatolik: {error}"
                    return
                self.ids.det_trans.text = answer
                self.ids.det_audio_btn.disabled = False
                self.selected_word = {"word": word, "translation": "", "example": ""}
                data.VOCABULARY_DATA.append(
                    {"word": word, "translation": "(AI javobi yuqorida)",
                     "level": "AI", "example": ""}
                )

            Clock.schedule_once(update_ui, 0)

        threading.Thread(target=worker, daemon=True).start()


# ---------------------------------------------------------------------------
# CHAT (Jo'rabek AI umumiy chat va IELTS Speaking simulyatori — bitta
# umumiy ekran, mode orqali farqlanadi)
# ---------------------------------------------------------------------------
class ChatScreen(Screen):
    mode = "jorabek"

    def on_pre_enter(self, *args):
        set_bg(self)
        app = App.get_running_app()
        cfg = app.chat_config
        self.ids.topbar.title_text = cfg["title"]
        self.ids.topbar.back_callback = self.go_home
        self.ids.topbar.extra_callback = self.show_history
        self.storage_file = cfg["storage_file"]
        self.system_prompt = cfg["system_prompt"]
        self.greeting = cfg["greeting"]
        self.mode = cfg["mode"]
        self.sessions = storage.load_sessions(self.storage_file)
        self.current_session_id = None

        self.ids.chat_box.clear_widgets()
        if self.sessions:
            self.load_session(self.sessions[0])
        else:
            self.start_new_session()

    def go_home(self):
        self.manager.current = "home"

    def get_current_session(self):
        for s in self.sessions:
            if s["id"] == self.current_session_id:
                return s
        return None

    def start_new_session(self):
        new_id = str(uuid.uuid4())
        title = "Yangi suhbat" if self.mode == "jorabek" else "Yangi imtihon"
        session = {"id": new_id, "title": title, "messages": []}
        self.sessions.insert(0, session)
        self.current_session_id = new_id
        storage.save_sessions(self.storage_file, self.sessions)
        self.ids.chat_box.clear_widgets()
        self.append_bubble("assistant", self.greeting)
        self.get_current_session()["messages"].append(
            {"role": "assistant", "content": self.greeting}
        )
        storage.save_sessions(self.storage_file, self.sessions)

    def load_session(self, session):
        self.current_session_id = session["id"]
        self.ids.chat_box.clear_widgets()
        for m in session["messages"]:
            self.append_bubble(m["role"], m["content"])

    def append_bubble(self, role, content):
        is_user = role == "user"
        sender = "Siz" if is_user else ("Examiner" if self.mode == "speaking" else "Jo'rabek")
        bubble = Factory.ChatBubble()
        bubble.sender = sender
        bubble.msg = content
        bubble.is_user = is_user
        self.ids.chat_box.add_widget(bubble)
        Clock.schedule_once(lambda dt: setattr(
            self.ids.chat_scroll, "scroll_y", 0), 0.05)

    def send_message(self):
        text = self.ids.chat_input.text.strip()
        if not text:
            return
        self.ids.chat_input.text = ""
        self.append_bubble("user", text)
        session = self.get_current_session()
        if session is not None:
            session["messages"].append({"role": "user", "content": text})
            if session["title"] in ("Yangi suhbat", "Yangi imtihon"):
                clean = text.replace("\n", " ")
                session["title"] = clean[:28] + ("..." if len(clean) > 28 else "")
            storage.save_sessions(self.storage_file, self.sessions)

        self.append_bubble("assistant", "Yozmoqda...")
        history_snapshot = list(session["messages"]) if session else []

        def worker():
            answer, error = ai.get_jorabek_response(
                history_snapshot, system_prompt=self.system_prompt
            )

            def update_ui(_dt):
                # "Yozmoqda..." bubble'ini olib tashlaymiz
                children = self.ids.chat_box.children
                if children:
                    self.ids.chat_box.remove_widget(children[0])
                if error:
                    self.append_bubble("assistant", f"Xatolik: {error}")
                    return
                self.append_bubble("assistant", answer)
                if session is not None:
                    session["messages"].append({"role": "assistant", "content": answer})
                    storage.save_sessions(self.storage_file, self.sessions)

            Clock.schedule_once(update_ui, 0)

        threading.Thread(target=worker, daemon=True).start()

    def show_history(self):
        content = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(10))
        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(4))
        grid.bind(minimum_height=grid.setter("height"))

        popup = Popup(title="Suhbatlar tarixi", size_hint=(0.85, 0.85))

        new_btn = Button(text="+ Yangi suhbat", size_hint_y=None, height=dp(44),
                          background_normal="", background_color=get_color_from_hex("#1565c0"),
                          color=(1, 1, 1, 1))

        def on_new(*_a):
            popup.dismiss()
            self.start_new_session()

        new_btn.bind(on_release=on_new)
        content.add_widget(new_btn)

        for s in self.sessions:
            btn = Button(text=s["title"], size_hint_y=None, height=dp(44),
                         background_normal="", background_color=(1, 1, 1, 1),
                         color=get_color_from_hex("#1b5e20"))

            def on_select(_btn, session=s):
                popup.dismiss()
                self.load_session(session)

            btn.bind(on_release=on_select)
            grid.add_widget(btn)

        scroll.add_widget(grid)
        content.add_widget(scroll)
        popup.content = content
        popup.open()


# ---------------------------------------------------------------------------
# APP
# ---------------------------------------------------------------------------
class StudexApp(App):
    def build(self):
        self.title = f"{APP_NAME} — IELTS Prep"
        self.gradient_texture = make_gradient_texture(GRADIENT_TOP, GRADIENT_BOTTOM)
        self.chat_config = {}

        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(PlaceholderScreen(name="placeholder"))
        sm.add_widget(VocabularyScreen(name="vocabulary"))
        sm.add_widget(SubsectionScreen(name="subsection"))
        sm.add_widget(FlashcardScreen(name="flashcard"))
        sm.add_widget(DictionaryScreen(name="dictionary"))
        sm.add_widget(ChatScreen(name="chat"))
        return sm

    def configure_placeholder_screen(self, name):
        screen = self.root.get_screen("placeholder")
        screen.ids.topbar.title_text = name
        screen.ids.info_label.text = (
            "Bu bo'lim tez orada tayyor bo'ladi.\nMazmuni ustida ishlanmoqda..."
        )

    def configure_subsection_screen(self, title, dataset):
        screen = self.root.get_screen("subsection")
        screen.title_text = title
        screen.dataset = dataset

    def configure_flashcard_screen(self, title, dataset):
        screen = self.root.get_screen("flashcard")
        screen.title_text = title
        screen.dataset = dataset

    def configure_chat_screen(self, mode="jorabek"):
        if mode == "speaking":
            self.chat_config = {
                "mode": "speaking",
                "title": "IELTS Speaking",
                "storage_file": "speaking_history.json",
                "system_prompt": ai.IELTS_EXAMINER_SYSTEM_PROMPT,
                "greeting": ai.IELTS_SPEAKING_GREETING,
            }
        else:
            self.chat_config = {
                "mode": "jorabek",
                "title": "Jo'rabek AI",
                "storage_file": "jorabek_history.json",
                "system_prompt": ai.JORABEK_SYSTEM_PROMPT,
                "greeting": ai.JORABEK_GREETING,
            }


if __name__ == "__main__":
    StudexApp().run()
