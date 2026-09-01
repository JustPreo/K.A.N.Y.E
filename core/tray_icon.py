import threading

from core import theme

_icon = None
_available = True


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


STATE_COLORS = {state: _hex_to_rgb(color) for state, color in theme.STATE_COLORS.items()}

STATE_LABELS = {
    "idle":       "K.A.N.Y.E. - Esperando",
    "listening":  "K.A.N.Y.E. - Escuchando...",
    "processing": "K.A.N.Y.E. - Procesando...",
    "speaking":   "K.A.N.Y.E. - Hablando...",
    "error":      "K.A.N.Y.E. - Error",
}


def _make_image(state: str):
    from PIL import Image, ImageDraw

    color = STATE_COLORS.get(state, STATE_COLORS["idle"])
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Círculo relleno con borde más oscuro
    border = tuple(max(0, c - 60) for c in color)
    draw.ellipse([2, 2, size - 2, size - 2], fill=(*border, 255))
    draw.ellipse([6, 6, size - 6, size - 6], fill=(*color, 255))
    return img


def set_state(state: str) -> None:
    global _icon
    if not _available or _icon is None:
        return
    try:
        _icon.icon = _make_image(state)
        _icon.title = STATE_LABELS.get(state, "K.A.N.Y.E.")
    except Exception:
        pass


def start(on_quit=None) -> None:
    global _icon, _available

    try:
        import pystray
        from PIL import Image
    except ImportError:
        _available = False
        print("K.A.N.Y.E.: pystray/Pillow no instalado - bandeja del sistema desactivada.")
        return

    def _quit_action(icon, item):
        icon.stop()
        if on_quit:
            on_quit()

    menu = pystray.Menu(
        pystray.MenuItem("K.A.N.Y.E.", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Salir", _quit_action),
    )

    _icon = pystray.Icon(
        name="kanye",
        icon=_make_image("idle"),
        title="K.A.N.Y.E. - Esperando",
        menu=menu,
    )

    def _run_silent():
        import os, contextlib
        with open(os.devnull, "w") as devnull:
            with contextlib.redirect_stderr(devnull):
                try:
                    _icon.run()
                except Exception:
                    pass

    thread = threading.Thread(target=_run_silent, daemon=True)
    thread.start()
