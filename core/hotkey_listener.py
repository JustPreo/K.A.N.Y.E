import os
import threading
import time
from pathlib import Path
from core.config_loader import get_config

TRIGGER_FILE = Path("/tmp/kanye_trigger")


def _to_pynput_format(combo: str) -> str:
    parts = combo.lower().split("+")
    result = []
    single_chars = set("abcdefghijklmnopqrstuvwxyz0123456789")
    for part in parts:
        part = part.strip()
        if part in single_chars:
            result.append(part)
        else:
            result.append(f"<{part}>")
    return "+".join(result)


def _wait_trigger_file() -> None:
    """Espera a que aparezca /tmp/kanye_trigger y lo borra."""
    if TRIGGER_FILE.exists():
        TRIGGER_FILE.unlink()
    while not TRIGGER_FILE.exists():
        time.sleep(0.1)
    TRIGGER_FILE.unlink(missing_ok=True)


def _is_wayland() -> bool:
    session = os.environ.get("XDG_SESSION_TYPE", "").lower()
    display = os.environ.get("WAYLAND_DISPLAY", "")
    return session == "wayland" or bool(display)


def wait_for_hotkey(combo: str | None = None) -> None:
    if combo is None:
        config = get_config()
        combo = config.get("hotkey", "ctrl+f9")

    # En Wayland pynput no puede capturar hotkeys globales — usar archivo señal
    if _is_wayland():
        _wait_trigger_file()
        return

    triggered = threading.Event()

    def on_activate():
        triggered.set()

    try:
        from pynput import keyboard
        pynput_combo = _to_pynput_format(combo)
        listener = keyboard.GlobalHotKeys({pynput_combo: on_activate})
        listener.start()
        triggered.wait()
        listener.stop()

    except Exception as error:
        print(f"K.A.N.Y.E.: Hotkey ({error}). Presioná Enter para activar.")
        input()
