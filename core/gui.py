"""
Ventana principal de K.A.N.Y.E.
Cross-platform (tkinter, incluido en Python).

Dirección visual: brutalista/editorial — negro puro, un acento dorado,
bloques de color en vez de degradados, tipografía condensada para
titulares y monoespaciada para el cuerpo. Ver core/theme.py.
"""
import threading
import time
import tkinter as tk
from tkinter import scrolledtext

from core import theme

_suppress_close = False   # True mientras KANYE cierra otras apps
_root: tk.Tk | None = None
_chat_box = None
_status_chip = None
_mode_value = None
_stats_label = None
_player_label = None
_player_bar = None
_player_anchor = None     # widget antes del cual se inserta la player bar al mostrarla
_kb_frame = None
_kb_entry = None
_kb_active = False
_trigger_callback = None
_start_hidden = True
_kb_callback = None       # fn(text) → llamado al enviar comando por teclado
_available = False


def _bar(parent, accent: str) -> tk.Frame:
    """Franja horizontal de metadatos: borde izquierdo de 3px de color +
    fondo INK2, el lenguaje visual repetido para modo/reproductor/stats."""
    row = tk.Frame(parent, bg=theme.INK2)
    tk.Frame(row, bg=accent, width=3).pack(side=tk.LEFT, fill=tk.Y)
    inner = tk.Frame(row, bg=theme.INK2, padx=12, pady=5)
    inner.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    return row, inner


def _build_window():
    global _root, _chat_box, _status_chip
    global _mode_value, _stats_label, _available
    global _player_label, _player_bar, _player_anchor, _kb_frame, _kb_entry

    try:
        root = tk.Tk()
    except Exception:
        return

    root.title("K.A.N.Y.E.")
    root.geometry("400x600")
    root.minsize(340, 460)
    root.resizable(True, True)
    root.configure(bg=theme.VOID)

    FONT_WORDMARK = theme.display_font(20, "bold")
    FONT_CAPTION  = theme.mono_font(8)
    FONT_CHIP     = theme.mono_font(9, "bold")
    FONT_BODY     = theme.mono_font(10)
    FONT_BODY_B   = theme.mono_font(10, "bold")
    FONT_LABEL    = theme.mono_font(8, "bold")
    FONT_CTA      = theme.display_font(13, "bold")
    FONT_GHOST    = theme.mono_font(9, "bold")

    # ── Header ────────────────────────────────────────────────────────────────
    header = tk.Frame(root, bg=theme.VOID, padx=14)
    header.pack(fill=tk.X, pady=(14, 10))

    top_row = tk.Frame(header, bg=theme.VOID)
    top_row.pack(fill=tk.X)

    tk.Label(
        top_row, text="K·A·N·Y·E", font=FONT_WORDMARK,
        bg=theme.VOID, fg=theme.ACCENT,
    ).pack(side=tk.LEFT)

    chip = tk.Label(
        top_row, text=" ESPERANDO ", font=FONT_CHIP,
        bg=theme.STATE_COLORS["idle"], fg=theme.VOID,
        padx=6, pady=2,
    )
    chip.pack(side=tk.RIGHT, anchor="e")

    tk.Label(
        header,
        text="ASISTENTE LOCAL · 100% OFFLINE",
        font=FONT_CAPTION, bg=theme.VOID, fg=theme.TEXT_DIM,
        anchor="w", wraplength=360, justify=tk.LEFT,
    ).pack(fill=tk.X, pady=(4, 0))

    tk.Frame(root, bg=theme.ACCENT, height=2).pack(fill=tk.X)

    # ── Modo activo ───────────────────────────────────────────────────────────
    mode_row, mode_inner = _bar(root, theme.ACCENT_DIM)
    mode_row.pack(fill=tk.X)
    tk.Label(mode_inner, text="MODO", font=FONT_LABEL,
             bg=theme.INK2, fg=theme.TEXT_DIM).pack(side=tk.LEFT)
    mvalue = tk.Label(mode_inner, text="—", font=theme.mono_font(9, "bold"),
                       bg=theme.INK2, fg=theme.ACCENT, padx=8)
    mvalue.pack(side=tk.LEFT)

    # ── Player bar (oculta hasta que hay reproducción) ─────────────────────────
    player_row, player_inner = _bar(root, theme.STATE_COLORS["speaking"])

    plabel = tk.Label(
        player_inner, text="♫ SIN REPRODUCCIÓN", font=theme.mono_font(9),
        bg=theme.INK2, fg=theme.TEXT, anchor="w",
    )
    plabel.pack(side=tk.LEFT, fill=tk.X, expand=True)

    stop_btn = tk.Label(
        player_inner, text="■ DETENER", font=FONT_LABEL,
        bg=theme.INK2, fg=theme.TEXT_DIM, cursor="hand2", padx=6,
    )
    stop_btn.pack(side=tk.RIGHT)
    stop_btn.bind("<Button-1>", lambda e: _stop_player())
    theme.bind_hover(
        stop_btn,
        normal={"fg": theme.TEXT_DIM},
        hover={"fg": theme.DANGER},
    )

    # ── Chat ──────────────────────────────────────────────────────────────────
    chat_frame = tk.Frame(root, bg=theme.VOID)
    chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

    chat = scrolledtext.ScrolledText(
        chat_frame,
        bg=theme.VOID, fg=theme.TEXT, font=FONT_BODY,
        relief=tk.FLAT, bd=0,
        wrap=tk.WORD,
        state=tk.DISABLED,
        insertbackground=theme.TEXT,
        padx=2, pady=2,
    )
    chat.pack(fill=tk.BOTH, expand=True)

    chat.tag_configure("user_label",  foreground=theme.STATE_COLORS["speaking"], font=FONT_BODY_B)
    chat.tag_configure("user_body",   foreground=theme.TEXT, font=FONT_BODY)
    chat.tag_configure("kanye_label", foreground=theme.ACCENT, font=FONT_BODY_B)
    chat.tag_configure("kanye_body",  foreground=theme.TEXT, font=FONT_BODY)
    chat.tag_configure("system",      foreground=theme.TEXT_DIM, font=theme.mono_font(8))
    chat.tag_configure("alert",       foreground=theme.STATE_COLORS["error"], font=FONT_BODY_B)

    # ── Stats ─────────────────────────────────────────────────────────────────
    stats_row, stats_inner = _bar(root, theme.TEXT_DIM)
    stats_row.pack(fill=tk.X, pady=(10, 0))
    stlabel = tk.Label(stats_inner, text="CPU --%  ·  RAM --%  ·  BAT --%",
                        font=theme.mono_font(9), bg=theme.INK2, fg=theme.TEXT_DIM)
    stlabel.pack(side=tk.LEFT)

    # ── Acciones ──────────────────────────────────────────────────────────────
    btn_frame = tk.Frame(root, bg=theme.VOID, padx=10, pady=10)
    btn_frame.pack(fill=tk.X)

    btn = tk.Label(
        btn_frame,
        text="●  HABLAR   ·   CTRL+F9",
        font=FONT_CTA,
        bg=theme.ACCENT, fg=theme.VOID,
        cursor="hand2", pady=10,
    )
    btn.pack(fill=tk.X)
    btn.bind("<Button-1>", lambda e: _on_button_click())
    theme.bind_hover(
        btn,
        normal={"bg": theme.ACCENT, "fg": theme.VOID},
        hover={"bg": theme.VOID, "fg": theme.ACCENT},
    )

    ghost_row = tk.Frame(btn_frame, bg=theme.VOID)
    ghost_row.pack(fill=tk.X, pady=(8, 0))

    def _ghost(parent, text, cmd):
        lbl = tk.Label(
            parent, text=text, font=FONT_GHOST,
            bg=theme.VOID, fg=theme.TEXT_DIM,
            highlightthickness=1, highlightbackground=theme.LINE,
            cursor="hand2", pady=6,
        )
        lbl.bind("<Button-1>", lambda e: cmd())
        theme.bind_hover(
            lbl,
            normal={"fg": theme.TEXT_DIM, "highlightbackground": theme.LINE},
            hover={"fg": theme.ACCENT, "highlightbackground": theme.ACCENT},
        )
        return lbl

    cfg_btn = _ghost(ghost_row, "⚙  CONFIGURACIÓN", lambda: _open_settings(root))
    cfg_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

    kb_toggle = _ghost(ghost_row, "⌨  MODO TECLADO", lambda: _toggle_keyboard_mode(kb_toggle, kb_frame))
    kb_toggle.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

    kb_frame = tk.Frame(root, bg=theme.VOID, padx=10)

    kb_entry = tk.Entry(
        kb_frame,
        bg=theme.INK2, fg=theme.TEXT,
        insertbackground=theme.ACCENT,
        font=FONT_BODY,
        relief=tk.FLAT, bd=0,
        highlightthickness=1, highlightbackground=theme.LINE,
        highlightcolor=theme.ACCENT,
    )
    kb_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 6))
    kb_entry.bind("<Return>", lambda e: _on_kb_send(kb_entry))

    kb_send = tk.Label(
        kb_frame, text="ENVIAR", font=FONT_GHOST,
        bg=theme.ACCENT, fg=theme.VOID, cursor="hand2", padx=10, pady=6,
    )
    kb_send.bind("<Button-1>", lambda e: _on_kb_send(kb_entry))
    theme.bind_hover(
        kb_send,
        normal={"bg": theme.ACCENT, "fg": theme.VOID},
        hover={"bg": theme.VOID, "fg": theme.ACCENT},
    )
    kb_send.pack(side=tk.RIGHT)

    _root          = root
    _chat_box      = chat
    _status_chip   = chip
    _mode_value    = mvalue
    _stats_label   = stlabel
    _player_label  = plabel
    _player_bar    = player_row
    _player_anchor = chat_frame
    _kb_frame      = kb_frame
    _kb_entry      = kb_entry
    _available     = True

    # Stats loop
    threading.Thread(target=_stats_loop, daemon=True).start()

    root.protocol("WM_DELETE_WINDOW", _on_close)
    root.bind("<Escape>", lambda e: hide())
    if _start_hidden:
        root.withdraw()   # arranca oculta — aparece solo con el hotkey
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
    """Cerrar la ventana (X, Win+C, Alt+F4, etc.) la oculta en vez de matar
    K.A.N.Y.E. — para salir de verdad: 'salir' por voz/texto, o Salir en el
    ícono de bandeja."""
    if _suppress_close:
        return
    hide()


def _stop_player() -> None:
    from core.media_player import stop
    stop()


def _toggle_keyboard_mode(btn, frame) -> None:
    global _kb_active
    _kb_active = not _kb_active
    if _kb_active:
        frame.pack(fill=tk.X, pady=(0, 6))
        btn.config(fg=theme.ACCENT, highlightbackground=theme.ACCENT)
        if _kb_entry:
            _kb_entry.focus_set()
    else:
        frame.pack_forget()
        btn.config(fg=theme.TEXT_DIM, highlightbackground=theme.LINE)


def _on_kb_send(entry) -> None:
    text = entry.get().strip()
    if not text:
        return
    entry.delete(0, tk.END)
    add_user(text)
    if _kb_callback:
        threading.Thread(target=_kb_callback, args=(text,), daemon=True).start()


def _stats_loop():
    while _available:
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            bat = psutil.sensors_battery()
            bat_str = f"{int(bat.percent)}%" if bat else "N/A"
            plug = " ⚡" if bat and bat.power_plugged else ""
            text = f"CPU {cpu:.0f}%  ·  RAM {ram:.0f}%  ·  BAT {bat_str}{plug}"
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

def start(on_trigger=None, start_hidden: bool = True) -> bool:
    """Inicia la ventana en un hilo daemon. Retorna True si tkinter está disponible."""
    global _trigger_callback, _start_hidden
    _trigger_callback = on_trigger
    _start_hidden = start_hidden
    try:
        import tkinter as _tk  # noqa: verificar disponibilidad
        t = threading.Thread(target=_build_window, daemon=True)
        t.start()
        time.sleep(0.3)   # dar tiempo a que la ventana aparezca
        return _available
    except Exception:
        return False


def set_state(state: str) -> None:
    color = theme.STATE_COLORS.get(state, theme.STATE_COLORS["idle"])
    text  = theme.STATE_TEXT.get(state, state.upper())
    _safe(lambda c=color, t=text: _status_chip.config(bg=c, text=f" {t} "))


def set_mode(mode: str) -> None:
    label = mode if mode else "—"
    _safe(lambda l=label: _mode_value.config(text=l))


def add_user(text: str) -> None:
    _append_turn("TÚ", text, "user_label", "user_body")


def add_kanye(text: str) -> None:
    _append_turn("K.A.N.Y.E.", text, "kanye_label", "kanye_body")


def add_system(text: str) -> None:
    _append(f"·  {text}\n", "system")


def add_alert(text: str) -> None:
    _append(f"⚠  {text}\n", "alert")


def _append_turn(label: str, text: str, label_tag: str, body_tag: str) -> None:
    def _do(l=label, t=text, lt=label_tag, bt=body_tag):
        if not _chat_box:
            return
        _chat_box.config(state=tk.NORMAL)
        _chat_box.insert(tk.END, f"{l}  ", lt)
        _chat_box.insert(tk.END, f"{t}\n\n", bt)
        _chat_box.see(tk.END)
        _chat_box.config(state=tk.DISABLED)
    _safe(_do)


def _append(text: str, tag: str) -> None:
    def _do(t=text, tg=tag):
        if not _chat_box:
            return
        _chat_box.config(state=tk.NORMAL)
        _chat_box.insert(tk.END, t, tg)
        _chat_box.see(tk.END)
        _chat_box.config(state=tk.DISABLED)
    _safe(_do)


def show() -> None:
    """Muestra la ventana (popup, como al presionar el hotkey)."""
    def _do():
        if not _root:
            return
        _root.deiconify()
        _root.lift()
        _root.attributes("-topmost", True)
        _root.after(50, lambda: _root.attributes("-topmost", False))
        _root.focus_force()
        if _kb_entry:
            _kb_entry.focus_set()
    _safe(_do)


def hide() -> None:
    """Oculta la ventana (vuelve a correr en segundo plano)."""
    _safe(lambda: _root.withdraw() if _root else None)


def is_available() -> bool:
    return _available


def suppress_close(value: bool) -> None:
    global _suppress_close
    _suppress_close = value


def set_kb_callback(fn) -> None:
    global _kb_callback
    _kb_callback = fn


def set_player_status(url_or_none: str | None) -> None:
    if url_or_none:
        from urllib.parse import urlparse, parse_qs
        title = url_or_none
        try:
            qs = parse_qs(urlparse(url_or_none).query)
            v = qs.get("v", [None])[0]
            if v:
                title = f"youtu.be/{v}"
        except Exception:
            pass
        _safe(lambda t=title: (
            _player_bar.pack(fill=tk.X, pady=(10, 0), before=_player_anchor)
            if (_player_bar and _player_anchor) else None,
            _player_label.config(text=f"♫  {t.upper()}") if _player_label else None,
        ))
    else:
        _safe(lambda: (
            _player_bar.pack_forget() if _player_bar else None,
        ))
