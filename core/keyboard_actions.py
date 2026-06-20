"""
Control de teclado por voz.
Usa clipboard para typing (soporta cualquier unicode) y pyautogui para shortcuts.
"""
import time

import pyautogui

pyautogui.FAILSAFE = False
pyautogui.PAUSE    = 0.04


def _clipboard_type(text: str) -> bool:
    """Pega texto usando el portapapeles para soportar acentos y caracteres especiales."""
    try:
        import pyperclip
        previous = pyperclip.paste()
        pyperclip.copy(text)
        time.sleep(0.1)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.15)
        pyperclip.copy(previous)   # restaura el portapapeles original
        return True
    except ImportError:
        # Fallback sin pyperclip: typewrite (solo ASCII confiable)
        pyautogui.typewrite(text, interval=0.04)
        return True
    except Exception as error:
        print(f"K.A.N.Y.E.: Error al escribir: {error}")
        return False


def type_text(text: str, uppercase: bool = False) -> bool:
    if not text:
        return False
    if uppercase:
        text = text.upper()
    return _clipboard_type(text)


def press_key(key: str) -> bool:
    try:
        pyautogui.press(key)
        return True
    except Exception as error:
        print(f"K.A.N.Y.E.: Error presionando '{key}': {error}")
        return False


def hotkey(*keys: str) -> bool:
    try:
        pyautogui.hotkey(*keys)
        return True
    except Exception as error:
        print(f"K.A.N.Y.E.: Error en hotkey {'+'.join(keys)}: {error}")
        return False


# ─── Comandos mapeados ────────────────────────────────────────────────────────

# Mapeo de frases reconocidas → acción
SHORTCUT_COMMANDS: dict[str, tuple] = {
    # Navegación
    "presiona enter":   ("press", "enter"),
    "dar enter":        ("press", "enter"),
    "nueva línea":      ("press", "enter"),
    "nueva linea":      ("press", "enter"),
    "presiona tab":     ("press", "tab"),
    "presiona escape":  ("press", "escape"),
    "presiona esc":     ("press", "escape"),
    "presiona espacio": ("press", "space"),
    "presiona retroceso": ("press", "backspace"),
    "borra letra":      ("press", "backspace"),

    # Selección y edición
    "selecciona todo":  ("hotkey", "ctrl", "a"),
    "copia":            ("hotkey", "ctrl", "c"),
    "copiar":           ("hotkey", "ctrl", "c"),
    "pega":             ("hotkey", "ctrl", "v"),
    "pegar":            ("hotkey", "ctrl", "v"),
    "corta":            ("hotkey", "ctrl", "x"),
    "cortar":           ("hotkey", "ctrl", "x"),
    "deshace":          ("hotkey", "ctrl", "z"),
    "deshacer":         ("hotkey", "ctrl", "z"),
    "rehace":           ("hotkey", "ctrl", "y"),
    "rehacer":          ("hotkey", "ctrl", "y"),
    "guarda el archivo": ("hotkey", "ctrl", "s"),
    "guardar archivo":  ("hotkey", "ctrl", "s"),

    # Ventanas
    "cierra ventana":   ("hotkey", "alt", "f4"),
    "minimiza":         ("hotkey", "super", "down"),
    "maximiza":         ("hotkey", "super", "up"),
    "cambia ventana":   ("hotkey", "alt", "tab"),

    # Navegador
    "nueva pestaña":    ("hotkey", "ctrl", "t"),
    "cierra pestaña":   ("hotkey", "ctrl", "w"),
    "recarga":          ("press", "f5"),
    "recargar":         ("press", "f5"),
    "va atrás":         ("hotkey", "alt", "left"),
    "volver atrás":     ("hotkey", "alt", "left"),
}


def execute_shortcut(phrase: str) -> bool:
    """Ejecuta un shortcut mapeado por nombre de frase."""
    action = SHORTCUT_COMMANDS.get(phrase.lower().strip())
    if not action:
        return False

    if action[0] == "press":
        return press_key(action[1])
    elif action[0] == "hotkey":
        return hotkey(*action[1:])

    return False
