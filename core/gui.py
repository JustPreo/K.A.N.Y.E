"""
Ventana principal de K.A.N.Y.E.
Cross-platform (tkinter, incluido en Python).
"""
import threading
import time
import tkinter as tk
from tkinter import scrolledtext

_root: tk.Tk | None = None
_chat_box = None
_status_dot = None
_status_label = None
_mode_label = None
_stats_label = None
_trigger_callback = None
_available = False

STATE_COLORS = {
    "idle":       "#787878",
    "listening":  "#32C850",
    "processing": "#DCA800",
    "speaking":   "#3C82DC",
    "error":      "#C83232",
}

STATE_TEXT = {
    "idle":       "Esperando",
    "listening":  "Escuchando...",
    "processing": "Procesando...",
    "speaking":   "Hablando...",
    "error":      "Error",
}

BG       = "#111111"
BG2      = "#1C1C1C"
BG3      = "#252525"
FG       = "#E8E8E8"
FG_DIM   = "#888888"
ACCENT   = "#C8A000"
FONT     = ("Consolas", 10) if __import__("sys").platform == "win32" else ("Monospace", 10)
FONT_SM  = (FONT[0], 9)
FONT_LG  = (FONT[0], 13, "bold")


def _build_window():
    global _root, _chat_box, _status_dot, _status_label
    global _mode_label, _stats_label, _available

    try:
        root = tk.Tk()
    except Exception:
        return

    root.title("K.A.N.Y.E.")
    root.geometry("380x560")
    root.resizable(True, True)
    root.configure(bg=BG)
    root.attributes("-topmost", False)

    # ── Header ────────────────────────────────────────────────────────────────
    header = tk.Frame(root, bg=BG2, pady=8, padx=12)
    header.pack(fill=tk.X)

    tk.Label(header, text="K.A.N.Y.E.", font=FONT_LG, bg=BG2, fg=ACCENT).pack(side=tk.LEFT)

    right = tk.Frame(header, bg=BG2)
    right.pack(side=tk.RIGHT)

    dot = tk.Label(right, text="●", font=(FONT[0], 14), bg=BG2, fg=STATE_COLORS["idle"])
    dot.pack(side=tk.LEFT, padx=(0, 4))

    slabel = tk.Label(right, text="Esperando", font=FONT_SM, bg=BG2, fg=FG_DIM)
    slabel.pack(side=tk.LEFT)

    # ── Modo activo ───────────────────────────────────────────────────────────
    mode_bar = tk.Frame(root, bg=BG3, pady=4, padx=12)
    mode_bar.pack(fill=tk.X)

    mlabel = tk.Label(mode_bar, text="Modo: —", font=FONT_SM, bg=BG3, fg=FG_DIM)
    mlabel.pack(side=tk.LEFT)

    # ── Chat ──────────────────────────────────────────────────────────────────
    chat_frame = tk.Frame(root, bg=BG)
    chat_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 0))

    chat = scrolledtext.ScrolledText(
        chat_frame,
        bg=BG, fg=FG, font=FONT,
        relief=tk.FLAT, bd=0,
        wrap=tk.WORD,
        state=tk.DISABLED,
        insertbackground=FG,
    )
    chat.pack(fill=tk.BOTH, expand=True)

    chat.tag_configure("user",   foreground="#A0D0FF", font=(FONT[0], 10, "bold"))
    chat.tag_configure("kanye",  foreground=FG)
    chat.tag_configure("system", foreground=FG_DIM, font=FONT_SM)
    chat.tag_configure("alert",  foreground="#FFB040")

    # ── Stats ─────────────────────────────────────────────────────────────────
    stats_bar = tk.Frame(root, bg=BG3, pady=4, padx=12)
    stats_bar.pack(fill=tk.X)

    stlabel = tk.Label(stats_bar, text="CPU --%  RAM --%  BAT --%", font=FONT_SM, bg=BG3, fg=FG_DIM)
    stlabel.pack(side=tk.LEFT)

    # ── Botón ─────────────────────────────────────────────────────────────────
    btn_frame = tk.Frame(root, bg=BG, pady=8, padx=8)
    btn_frame.pack(fill=tk.X)

    btn = tk.Button(
        btn_frame,
        text="● Hablar  (Ctrl+F9)",
        font=(FONT[0], 11, "bold"),
        bg="#1E3A1E", fg="#50D050",
        activebackground="#2A502A", activeforeground="#70FF70",
        relief=tk.FLAT, bd=0, pady=8,
        cursor="hand2",
        command=_on_button_click,
    )
    btn.pack(fill=tk.X)

    cfg_btn = tk.Button(
        btn_frame,
        text="⚙ Configuración",
        font=(FONT[0], 9),
        bg=BG2, fg=FG_DIM,
        activebackground=BG3, activeforeground=FG,
        relief=tk.FLAT, bd=0, pady=4,
        cursor="hand2",
        command=lambda: _open_settings(root),
    )
    cfg_btn.pack(fill=tk.X, pady=(4, 0))

    _root        = root
    _chat_box    = chat
    _status_dot  = dot
    _status_label = slabel
    _mode_label  = mlabel
    _stats_label = stlabel
    _available   = True

    # Stats loop
    threading.Thread(target=_stats_loop, daemon=True).start()

    root.protocol("WM_DELETE_WINDOW", _on_close)
    root.mainloop()


def _open_settings(parent=None):
    try:
        from core.settings_gui import open_settings
        open_settings(parent)
    except Exception as e:
        print(f"K.A.N.Y.E.: Error abriendo configuración: {e}")


def _on_button_click():
    """Botón 'Hablar' — equivalente a presionar el hotkey."""
    from pathlib import Path
    Path("/tmp/kanye_trigger").touch()
    if _trigger_callback:
        _trigger_callback()


def _on_close():
    global _root, _available
    _available = False
    if _root:
        _root.destroy()
        _root = None
    import os, sys
    os.kill(os.getpid(), 9)


def _stats_loop():
    while _available:
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            bat = psutil.sensors_battery()
            bat_str = f"{int(bat.percent)}%" if bat else "N/A"
            plug = " ⚡" if bat and bat.power_plugged else ""
            text = f"CPU {cpu:.0f}%  RAM {ram:.0f}%  BAT {bat_str}{plug}"
            _safe(lambda t=text: _stats_label.config(text=t))
        except Exception:
            pass
        time.sleep(5)


def _safe(fn):
    """Ejecuta fn en el hilo de UI."""
    if _root and _available:
        try:
            _root.after(0, fn)
        except Exception:
            pass


# ── API pública ───────────────────────────────────────────────────────────────

def start(on_trigger=None) -> bool:
    """Inicia la ventana en un hilo daemon. Retorna True si tkinter está disponible."""
    global _trigger_callback
    _trigger_callback = on_trigger
    try:
        import tkinter as _tk  # noqa: verificar disponibilidad
        t = threading.Thread(target=_build_window, daemon=True)
        t.start()
        time.sleep(0.3)   # dar tiempo a que la ventana aparezca
        return _available
    except Exception:
        return False


def set_state(state: str) -> None:
    color = STATE_COLORS.get(state, STATE_COLORS["idle"])
    text  = STATE_TEXT.get(state, state)
    _safe(lambda c=color, t=text: (
        _status_dot.config(fg=c),
        _status_label.config(text=t),
    ))


def set_mode(mode: str) -> None:
    label = f"Modo: {mode}" if mode else "Modo: —"
    _safe(lambda l=label: _mode_label.config(text=l))


def add_user(text: str) -> None:
    _append(f"Tú: {text}\n", "user")


def add_kanye(text: str) -> None:
    _append(f"K.A.N.Y.E.: {text}\n", "kanye")


def add_system(text: str) -> None:
    _append(f"  {text}\n", "system")


def add_alert(text: str) -> None:
    _append(f"⚠ {text}\n", "alert")


def _append(text: str, tag: str) -> None:
    def _do(t=text, tg=tag):
        if not _chat_box:
            return
        _chat_box.config(state=tk.NORMAL)
        _chat_box.insert(tk.END, t, tg)
        _chat_box.see(tk.END)
        _chat_box.config(state=tk.DISABLED)
    _safe(_do)


def is_available() -> bool:
    return _available
