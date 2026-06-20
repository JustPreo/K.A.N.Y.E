import threading
from core.config_loader import get_config


def _to_pynput_format(combo: str) -> str:
    """
    Convierte "ctrl+f9" al formato de pynput "<ctrl>+<f9>".
    Teclas de un solo caracter quedan sin corchetes.
    """
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


def wait_for_hotkey(combo: str | None = None) -> None:
    """
    Bloquea hasta que el usuario presione el hotkey configurado.
    """
    if combo is None:
        config = get_config()
        combo = config.get("hotkey", "ctrl+f9")

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
        print(f"K.A.N.Y.E.: Error en hotkey listener ({error}).")
        print("K.A.N.Y.E.: Modo terminal activo. Presioná Enter para activar.")
        input()
