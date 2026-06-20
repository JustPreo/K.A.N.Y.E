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


def wait_for_hotkey(combo: str | None = None) -> None:
    if combo is None:
        config = get_config()
        combo = config.get("hotkey", "ctrl+f9")

    triggered = threading.Event()

    def on_activate():
        triggered.set()

    # Intentar pynput (funciona en X11, falla silenciosamente en Wayland)
    pynput_ok = False
    try:
        from pynput import keyboard
        pynput_combo = _to_pynput_format(combo)
        listener = keyboard.GlobalHotKeys({pynput_combo: on_activate})
        listener.start()

        # Dar 0.5s para que el listener se establezca; si falla, pynput_ok queda False
        time.sleep(0.5)
        if listener.is_alive():
            pynput_ok = True

    except Exception:
        pynput_ok = False

    if pynput_ok:
        triggered.wait()
        listener.stop()
        return

    # Fallback Wayland: esperar archivo señal /tmp/kanye_trigger
    _wait_trigger_file()
