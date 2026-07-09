# -*- coding: utf-8 -*-
"""
Studex — mobil qurilmada fayl saqlash (chat tarixi) va ovozli talaffuz (TTS).
Android'da App.user_data_dir ilova uchun ajratilgan xavfsiz papkani beradi.
"""

import json
import os
import threading

from kivy.app import App


def _data_file(name):
    app = App.get_running_app()
    base = app.user_data_dir if app else "."
    if not os.path.isdir(base):
        os.makedirs(base, exist_ok=True)
    return os.path.join(base, name)


def load_sessions(filename):
    path = _data_file(filename)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_sessions(filename, sessions):
    path = _data_file(filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def speak_word(word):
    """Android'da matnni ovozli o'qiydi (plyer TTS orqali).
    Kompyuterda (test paytida) xato chiqsa, jim tarzda o'tkazib yuboradi."""

    def target():
        try:
            from plyer import tts
            tts.speak(message=word)
        except Exception:
            pass

    threading.Thread(target=target, daemon=True).start()
