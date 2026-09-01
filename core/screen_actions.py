"""
Captura de pantalla para el modo de ayuda remota (core/it_worker.py). No
existía código de captura en el repo antes de esto.

En Wayland, pyautogui/PIL no ven nada (las apps no tienen acceso directo al
framebuffer por diseño) — hace falta `grim`, que solo funciona en
compositores wlroots (Hyprland, Sway). GNOME/KDE Wayland no soportan el
protocolo que usa grim (wlr-screencopy) — ahí capture() devuelve None y el
caller debe avisar que no se puede, no fallar en silencio.
"""
import os
import platform
import subprocess
import tempfile
from pathlib import Path


def _capture_pyautogui() -> bytes | None:
    try:
        import pyautogui
        import io
        img = pyautogui.screenshot()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as error:
        print(f"K.A.N.Y.E.: Error capturando pantalla (pyautogui): {error}")
        return None


def _capture_grim() -> bytes | None:
    try:
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "kanye_screen.png"
            r = subprocess.run(
                ["grim", str(out_path)],
                capture_output=True, text=True, timeout=10,
            )
            if r.returncode != 0 or not out_path.exists():
                print(f"K.A.N.Y.E.: grim falló: {r.stderr.strip()}")
                return None
            return out_path.read_bytes()
    except Exception as error:
        print(f"K.A.N.Y.E.: Error capturando pantalla (grim): {error}")
        return None


def capture() -> bytes | None:
    """Devuelve una captura de pantalla completa en PNG, o None si no se
    pudo (ej. Wayland sin grim/wlroots)."""
    if platform.system() != "Linux":
        return _capture_pyautogui()
    if os.environ.get("WAYLAND_DISPLAY"):
        return _capture_grim()
    return _capture_pyautogui()
