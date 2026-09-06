"""
Control de teclado por voz.

En sesiones Wayland (Hyprland, Sway, etc.) pynput y pyautogui inyectan
teclas vía XTEST, que solo llega a ventanas X11/XWayland — no a clientes
Wayland nativos (la gran mayoría de apps modernas: kitty, Brave, GTK4,
Electron en modo Wayland...). Por eso todo lo de acá prueba primero con
wtype (protocolo virtual-keyboard de Wayland, llega a cualquier ventana
con foco real) y solo cae a pynput/pyautogui si no hay wtype disponible
(X11 puro, Windows, macOS).
"""
import os
import random
import re
import shutil
import subprocess
import threading
import time

import pyautogui

pyautogui.FAILSAFE = False
pyautogui.PAUSE    = 0.04


def _wayland_typing_available() -> bool:
    return bool(os.environ.get("WAYLAND_DISPLAY")) and shutil.which("wtype") is not None


def _wtype_run(args: list[str], timeout: float = 15.0) -> bool:
    try:
        result = subprocess.run(["wtype", *args], capture_output=True, timeout=timeout)
        return result.returncode == 0
    except Exception as error:
        print(f"K.A.N.Y.E.: Error con wtype: {error}")
        return False


def _clipboard_type(text: str) -> bool:
    """Pega texto usando el portapapeles para soportar acentos y caracteres especiales."""
    try:
        import pyperclip
        previous = pyperclip.paste()
        pyperclip.copy(text)
        time.sleep(0.1)
        hotkey("ctrl", "v")
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
    if _wayland_typing_available() and _wtype_run([text]):
        return True
    return _clipboard_type(text)


# ─── Dictado directo ("escribí esto: ...") ────────────────────────────────
# Se resuelve acá con regex en vez de dejarlo en manos del LLM: es un pedido
# tan común y mecánico (pegar texto tal cual) que conviene que sea 100%
# confiable, igual que "cd" en modo teclado.

_DICTATE_ESTO_RE = re.compile(
    r"^(?:escrib[ieéí]?(?:me)?|tipe[aá])\s+esto\b\s*[:,]?\s*(.*)$",
    re.IGNORECASE | re.DOTALL,
)
_DICTATE_COLON_RE = re.compile(
    r"^(?:escrib[ieéí]?(?:me)?|tipe[aá])\s*:\s*(.*)$",
    re.IGNORECASE | re.DOTALL,
)


def parse_dictation_command(text: str) -> str | None:
    """Si el texto es un pedido directo de tipeo ('escribí esto: ...',
    'escribí: ...'), devuelve el texto a escribir preservando mayúsculas
    tal cual se tipeó. Si no matchea ninguna de esas formas, None."""
    if not text:
        return None
    stripped = text.strip()
    for pattern in (_DICTATE_ESTO_RE, _DICTATE_COLON_RE):
        match = pattern.match(stripped)
        if match:
            content = match.group(1).strip()
            if content:
                return content
    return None


# ─── Tipeo lento (letra por letra) para dictar documentos largos ─────────
# A diferencia de type_text (pega todo de una via clipboard), esto simula
# tecleo real caracter por caracter para que se vea "escribiendo" en vivo
# dentro de la app con foco (Word, un editor, etc). Corre en un hilo aparte
# para no bloquear el asistente, y se puede cancelar a mitad de camino.

_typing_lock = threading.Lock()
_typing_cancel = threading.Event()
_typing_active = False
_typing_process: "subprocess.Popen | None" = None


def is_typing() -> bool:
    return _typing_active


def stop_typing() -> bool:
    if not _typing_active:
        return False
    _typing_cancel.set()
    if _typing_process is not None:
        _typing_process.terminate()
    return True


def _type_worker_wtype(text: str, delay_ms: int) -> None:
    """Un solo proceso wtype para todo el texto: -d aplica el delay entre
    cada tecla, y los saltos de línea se mandan como Return explícito."""
    global _typing_process
    args = ["wtype", "-d", str(delay_ms)]
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if i > 0:
            args += ["-k", "Return"]
        if line:
            args.append(line)

    try:
        _typing_process = subprocess.Popen(args)
        while _typing_process.poll() is None:
            if _typing_cancel.is_set():
                _typing_process.terminate()
                print("K.A.N.Y.E.: Tipeo cancelado.")
                return
            time.sleep(0.05)
        print("K.A.N.Y.E.: Terminé de escribir el documento.")
    except Exception as error:
        print(f"K.A.N.Y.E.: Error al escribir con wtype: {error}")
    finally:
        _typing_process = None


def _type_worker_pynput(text: str, cps: float) -> None:
    from pynput.keyboard import Controller, Key, Listener

    controller = Controller()
    interval = 1.0 / max(cps, 1.0)

    # Freno físico: con la voz, cancelar tarda el round-trip completo
    # (hotkey → escuchar → transcribir → el LLM decida llamar stop_typing),
    # y mientras tanto se sigue tecleando texto no deseado en el documento.
    # Esc corta al toque sin pasar por el LLM. Solo funciona en X11 puro
    # (sin wtype), igual que el resto de este fallback.
    def _on_press(key):
        if key == Key.esc:
            _typing_cancel.set()

    esc_listener = Listener(on_press=_on_press)
    esc_listener.start()

    try:
        for char in text:
            if _typing_cancel.is_set():
                print("K.A.N.Y.E.: Tipeo cancelado.")
                return
            if char == "\n":
                controller.press(Key.enter)
                controller.release(Key.enter)
            else:
                try:
                    controller.type(char)
                except Exception:
                    pass  # caracter que el layout activo no puede mapear
            time.sleep(max(0.005, interval + random.uniform(-interval * 0.3, interval * 0.3)))

        print("K.A.N.Y.E.: Terminé de escribir el documento.")
    finally:
        esc_listener.stop()


def _type_worker(text: str, cps: float, start_delay: float) -> None:
    global _typing_active

    for i in range(int(start_delay), 0, -1):
        if _typing_cancel.is_set():
            _typing_active = False
            _typing_cancel.clear()
            return
        print(f"K.A.N.Y.E.: Empiezo a escribir en {i}...")
        time.sleep(1.0)

    if _typing_cancel.is_set():
        _typing_active = False
        _typing_cancel.clear()
        return

    try:
        if _wayland_typing_available():
            delay_ms = max(1, round(1000 / max(cps, 1.0)))
            _type_worker_wtype(text, delay_ms)
        else:
            _type_worker_pynput(text, cps)
    finally:
        _typing_active = False
        _typing_cancel.clear()


def start_typing(text: str, cps: float = 18.0, start_delay: float = 3.0) -> bool:
    """Arranca el tipeo lento en segundo plano. Devuelve False si ya hay uno
    en curso o si el texto está vacío."""
    global _typing_active

    if not text:
        return False

    with _typing_lock:
        if _typing_active:
            return False
        _typing_active = True
        _typing_cancel.clear()

    thread = threading.Thread(target=_type_worker, args=(text, cps, start_delay), daemon=True)
    thread.start()
    return True


# Nombres de tecla de pyautogui → nombres que entiende wtype (libxkbcommon).
_WTYPE_KEYS = {
    "enter": "Return", "tab": "Tab", "escape": "Escape", "esc": "Escape",
    "space": "space", "backspace": "BackSpace", "f5": "F5",
    "left": "Left", "right": "Right", "up": "Up", "down": "Down",
}
_WTYPE_MODS = {"ctrl": "ctrl", "alt": "alt", "shift": "shift", "super": "logo"}


def press_key(key: str) -> bool:
    if _wayland_typing_available():
        if _wtype_run(["-k", _WTYPE_KEYS.get(key, key)]):
            return True
    try:
        pyautogui.press(key)
        return True
    except Exception as error:
        print(f"K.A.N.Y.E.: Error presionando '{key}': {error}")
        return False


def hotkey(*keys: str) -> bool:
    if _wayland_typing_available():
        *mods, key = keys
        wmods = [_WTYPE_MODS.get(m, m) for m in mods]
        wkey = _WTYPE_KEYS.get(key, key)
        args = []
        for m in wmods:
            args += ["-M", m]
        args += ["-k", wkey]
        for m in reversed(wmods):
            args += ["-m", m]
        if _wtype_run(args):
            return True
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
    "presioná enter":   ("press", "enter"),
    "dar enter":        ("press", "enter"),
    "dale enter":       ("press", "enter"),
    "apretá enter":     ("press", "enter"),
    "aprieta enter":    ("press", "enter"),
    "tocá enter":       ("press", "enter"),
    "toca enter":       ("press", "enter"),
    "nueva línea":      ("press", "enter"),
    "nueva linea":      ("press", "enter"),
    "salto de línea":   ("press", "enter"),
    "salto de linea":   ("press", "enter"),
    "presiona tab":     ("press", "tab"),
    "presioná tab":     ("press", "tab"),
    "apretá tab":       ("press", "tab"),
    "tocá tab":         ("press", "tab"),
    "presiona escape":  ("press", "escape"),
    "presioná escape":  ("press", "escape"),
    "presiona esc":     ("press", "escape"),
    "presioná esc":     ("press", "escape"),
    "presiona espacio": ("press", "space"),
    "presioná espacio": ("press", "space"),
    "tocá espacio":     ("press", "space"),
    "barra espaciadora": ("press", "space"),
    "presiona retroceso": ("press", "backspace"),
    "presioná retroceso": ("press", "backspace"),
    "borra letra":      ("press", "backspace"),
    "borrá letra":      ("press", "backspace"),
    "sacá letra":       ("press", "backspace"),
    "elimina letra":    ("press", "backspace"),
    "eliminá letra":    ("press", "backspace"),

    # Selección y edición
    "selecciona todo":  ("hotkey", "ctrl", "a"),
    "seleccioná todo":  ("hotkey", "ctrl", "a"),
    "marca todo":       ("hotkey", "ctrl", "a"),
    "marcá todo":       ("hotkey", "ctrl", "a"),
    "copia":            ("hotkey", "ctrl", "c"),
    "copiar":           ("hotkey", "ctrl", "c"),
    "copiá":            ("hotkey", "ctrl", "c"),
    "copiame":          ("hotkey", "ctrl", "c"),
    "pega":             ("hotkey", "ctrl", "v"),
    "pegar":            ("hotkey", "ctrl", "v"),
    "pegá":             ("hotkey", "ctrl", "v"),
    "pegame":           ("hotkey", "ctrl", "v"),
    "corta":            ("hotkey", "ctrl", "x"),
    "cortar":           ("hotkey", "ctrl", "x"),
    "cortá":            ("hotkey", "ctrl", "x"),
    "cortame":          ("hotkey", "ctrl", "x"),
    "deshace":          ("hotkey", "ctrl", "z"),
    "deshacer":         ("hotkey", "ctrl", "z"),
    "deshacé":          ("hotkey", "ctrl", "z"),
    "revertí":          ("hotkey", "ctrl", "z"),
    "rehace":           ("hotkey", "ctrl", "y"),
    "rehacer":          ("hotkey", "ctrl", "y"),
    "rehacé":           ("hotkey", "ctrl", "y"),
    "guarda el archivo": ("hotkey", "ctrl", "s"),
    "guardar archivo":  ("hotkey", "ctrl", "s"),
    "guardá el archivo": ("hotkey", "ctrl", "s"),
    "guardá archivo":   ("hotkey", "ctrl", "s"),
    "guarda":           ("hotkey", "ctrl", "s"),
    "guardá":           ("hotkey", "ctrl", "s"),

    # Ventanas
    "cierra ventana":   ("hotkey", "alt", "f4"),
    "cerrá ventana":    ("hotkey", "alt", "f4"),
    "cerrá esta ventana": ("hotkey", "alt", "f4"),
    "cerrá la ventana": ("hotkey", "alt", "f4"),
    "minimiza":         ("hotkey", "super", "down"),
    "minimizá":         ("hotkey", "super", "down"),
    "achica":           ("hotkey", "super", "down"),
    "achicá":           ("hotkey", "super", "down"),
    "maximiza":         ("hotkey", "super", "up"),
    "maximizá":         ("hotkey", "super", "up"),
    "agranda":          ("hotkey", "super", "up"),
    "agrandá":          ("hotkey", "super", "up"),
    "cambia ventana":   ("hotkey", "alt", "tab"),
    "cambiá ventana":   ("hotkey", "alt", "tab"),
    "cambia de ventana": ("hotkey", "alt", "tab"),
    "cambiá de ventana": ("hotkey", "alt", "tab"),
    "otra ventana":     ("hotkey", "alt", "tab"),

    # Navegador
    "nueva pestaña":    ("hotkey", "ctrl", "t"),
    "abrí pestaña":     ("hotkey", "ctrl", "t"),
    "abrí una pestaña": ("hotkey", "ctrl", "t"),
    "cierra pestaña":   ("hotkey", "ctrl", "w"),
    "cerrá pestaña":    ("hotkey", "ctrl", "w"),
    "cerrá la pestaña": ("hotkey", "ctrl", "w"),
    "recarga":          ("press", "f5"),
    "recargar":         ("press", "f5"),
    "recargá":          ("press", "f5"),
    "actualiza":        ("press", "f5"),
    "actualizá":        ("press", "f5"),
    "refrescá":         ("press", "f5"),
    "va atrás":         ("hotkey", "alt", "left"),
    "volver atrás":     ("hotkey", "alt", "left"),
    "andá atrás":       ("hotkey", "alt", "left"),
    "volvé atrás":      ("hotkey", "alt", "left"),
    "retrocedé":        ("hotkey", "alt", "left"),
    "retroceder":       ("hotkey", "alt", "left"),
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
