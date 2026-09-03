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
from core import cheatsheet_data

_suppress_close = False   # True mientras KANYE cierra otras apps
_root: tk.Tk | None = None
_chat_box = None
_status_chip = None
_mode_value = None
_stats_label = None
_player_label = None
_player_bar = None
_kb_frame = None
_kb_entry = None
_kb_active = False
_kb_toggle_btn = None
_sheet_col = None
_sheet_open = False
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
    global _player_label, _player_bar, _kb_frame, _kb_entry
    global _kb_toggle_btn, _sheet_col

    try:
        root = tk.Tk()
    except Exception:
        return

    root.title("K.A.N.Y.E.")
    root.geometry("400x650")
    root.minsize(340, 520)
    root.resizable(True, True)
    root.configure(bg=theme.VOID)

    body = tk.Frame(root, bg=theme.VOID)
    body.pack(fill=tk.BOTH, expand=True)
    # Todo en grid (en vez de pack): así el ancho/alto de cada fila/columna se
    # recalcula correctamente sin importar en qué orden se agregan o se
    # muestran/ocultan elementos dinámicos (reproductor, modo teclado, panel
    # de comandos) — con pack, agregar un widget nuevo después de que otro
    # con expand=True ya reclamó su espacio no siempre lo reacomodaba bien.
    body.grid_columnconfigure(0, weight=1)
    body.grid_columnconfigure(1, weight=0)
    body.grid_rowconfigure(0, weight=1)

    main_col = tk.Frame(body, bg=theme.VOID)
    main_col.grid(row=0, column=0, sticky="nsew")
    main_col.grid_columnconfigure(0, weight=1)
    main_col.grid_rowconfigure(4, weight=1)   # fila del chat

    FONT_WORDMARK = theme.display_font(20, "bold")
    FONT_CAPTION  = theme.mono_font(8)
    FONT_CHIP     = theme.mono_font(9, "bold")
    FONT_BODY     = theme.mono_font(10)
    FONT_BODY_B   = theme.mono_font(10, "bold")
    FONT_LABEL    = theme.mono_font(8, "bold")
    FONT_CTA      = theme.display_font(13, "bold")
    FONT_GHOST    = theme.mono_font(9, "bold")

    # ── Header ────────────────────────────────────────────────────────────────
    header = tk.Frame(main_col, bg=theme.VOID, padx=14)
    header.grid(row=0, column=0, sticky="ew", pady=(14, 10))

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

    divider = tk.Frame(main_col, bg=theme.ACCENT, height=2)
    divider.grid(row=1, column=0, sticky="ew")

    # ── Modo activo ───────────────────────────────────────────────────────────
    mode_row, mode_inner = _bar(main_col, theme.ACCENT_DIM)
    mode_row.grid(row=2, column=0, sticky="ew")
    tk.Label(mode_inner, text="MODO", font=FONT_LABEL,
             bg=theme.INK2, fg=theme.TEXT_DIM).pack(side=tk.LEFT)
    mvalue = tk.Label(mode_inner, text="—", font=theme.mono_font(9, "bold"),
                       bg=theme.INK2, fg=theme.ACCENT, padx=8)
    mvalue.pack(side=tk.LEFT)

    # ── Player bar (oculta hasta que hay reproducción) ─────────────────────────
    player_row, player_inner = _bar(main_col, theme.STATE_COLORS["speaking"])

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
    chat_frame = tk.Frame(main_col, bg=theme.VOID)
    chat_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=(10, 0))

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
    stats_row, stats_inner = _bar(main_col, theme.TEXT_DIM)
    stats_row.grid(row=5, column=0, sticky="ew", pady=(10, 0))
    stlabel = tk.Label(stats_inner, text="CPU --%  ·  RAM --%  ·  BAT --%",
                        font=theme.mono_font(9), bg=theme.INK2, fg=theme.TEXT_DIM)
    stlabel.pack(side=tk.LEFT)

    # ── Acciones ──────────────────────────────────────────────────────────────
    btn_frame = tk.Frame(main_col, bg=theme.VOID, padx=10, pady=10)
    btn_frame.grid(row=6, column=0, sticky="ew")

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

    kb_frame = tk.Frame(main_col, bg=theme.VOID, padx=10)

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

    sheet_toggle_row = tk.Frame(main_col, bg=theme.VOID, padx=10)
    sheet_toggle_row.grid(row=7, column=0, sticky="ew", pady=(0, 10))

    sheet_btn = _ghost(sheet_toggle_row, "»  COMANDOS", lambda: _toggle_sheet(sheet_btn, sheet_col))
    sheet_btn.pack(fill=tk.X)

    # ── Panel de comandos (hoja de trucos, colapsable a la derecha) ────────────
    sheet_col = tk.Frame(body, bg=theme.INK, width=248)
    sheet_col.pack_propagate(False)   # sus hijos (canvas/scrollbar) usan pack; esto fija su ancho aunque el contenido interno sea más ancho

    sheet_canvas = tk.Canvas(sheet_col, bg=theme.INK, highlightthickness=0)
    sheet_scroll = tk.Scrollbar(sheet_col, orient=tk.VERTICAL, command=sheet_canvas.yview)
    sheet_inner = tk.Frame(sheet_canvas, bg=theme.INK)

    sheet_inner.bind(
        "<Configure>",
        lambda e: sheet_canvas.configure(scrollregion=sheet_canvas.bbox("all")),
    )
    sheet_canvas.create_window((0, 0), window=sheet_inner, anchor="nw", width=228)
    sheet_canvas.configure(yscrollcommand=sheet_scroll.set)
    sheet_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
    sheet_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

    def _sheet_wheel(e, canvas=sheet_canvas):
        delta = -1 if getattr(e, "num", None) == 4 or getattr(e, "delta", 0) > 0 else 1
        canvas.yview_scroll(delta, "units")

    # bind_all mientras el mouse está sobre el panel: así el scroll funciona
    # sin importar qué widget hijo (una tarjeta de comando, un título de
    # categoría) esté bajo el cursor, no solo el canvas mismo.
    def _sheet_bind_wheel(_e=None):
        sheet_canvas.bind_all("<MouseWheel>", _sheet_wheel)
        sheet_canvas.bind_all("<Button-4>", _sheet_wheel)
        sheet_canvas.bind_all("<Button-5>", _sheet_wheel)

    def _sheet_unbind_wheel(_e=None):
        sheet_canvas.unbind_all("<MouseWheel>")
        sheet_canvas.unbind_all("<Button-4>")
        sheet_canvas.unbind_all("<Button-5>")

    sheet_col.bind("<Enter>", _sheet_bind_wheel)
    sheet_col.bind("<Leave>", _sheet_unbind_wheel)

    tk.Label(
        sheet_inner, text="COMANDOS DE EJEMPLO — CLIC PARA TIPEAR", font=FONT_LABEL,
        bg=theme.INK, fg=theme.TEXT_DIM, anchor="w", wraplength=220, justify=tk.LEFT,
    ).pack(fill=tk.X, pady=(0, 8))

    for section in cheatsheet_data.CATEGORIES:
        tk.Label(
            sheet_inner, text=section["title"].upper(), font=theme.mono_font(8, "bold"),
            bg=theme.INK, fg=theme.ACCENT_DIM, anchor="w",
        ).pack(fill=tk.X, pady=(10, 3))
        for phrase in section["items"]:
            item = tk.Label(
                sheet_inner, text=phrase, font=theme.mono_font(9),
                bg=theme.INK, fg=theme.TEXT, anchor="w", justify=tk.LEFT,
                wraplength=220, cursor="hand2", pady=4,
            )
            item.pack(fill=tk.X)
            item.bind("<Button-1>", lambda e, p=phrase: _send_cheat_command(p))
            theme.bind_hover(
                item,
                normal={"bg": theme.INK, "fg": theme.TEXT},
                hover={"bg": theme.INK2, "fg": theme.ACCENT},
            )

    _root          = root
    _chat_box      = chat
    _status_chip   = chip
    _mode_value    = mvalue
    _stats_label   = stlabel
    _player_label  = plabel
    _player_bar    = player_row
    _kb_frame      = kb_frame
    _kb_entry      = kb_entry
    _kb_toggle_btn = kb_toggle
    _sheet_col     = sheet_col
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
        frame.grid(row=8, column=0, sticky="ew", pady=(0, 6))
        btn.config(fg=theme.ACCENT, highlightbackground=theme.ACCENT)
        if _kb_entry:
            _kb_entry.focus_set()
    else:
        frame.grid_remove()
        btn.config(fg=theme.TEXT_DIM, highlightbackground=theme.LINE)


def _on_kb_send(entry) -> None:
    text = entry.get().strip()
    if not text:
        return
    entry.delete(0, tk.END)
    add_user(text)
    if _kb_callback:
        threading.Thread(target=_kb_callback, args=(text,), daemon=True).start()


def _toggle_sheet(btn, frame) -> None:
    """Muestra/oculta el panel de comandos a la derecha, ensanchando o
    achicando la ventana en el ancho que ocupa el panel."""
    global _sheet_open
    _sheet_open = not _sheet_open
    if not _root:
        return
    _root.update_idletasks()
    w, h = _root.winfo_width(), _root.winfo_height()
    if _sheet_open:
        frame.grid(row=0, column=1, sticky="ns")
        btn.config(fg=theme.ACCENT, highlightbackground=theme.ACCENT)
        _root.geometry(f"{w + 248}x{h}")
    else:
        frame.grid_remove()
        btn.config(fg=theme.TEXT_DIM, highlightbackground=theme.LINE)
        _root.geometry(f"{max(w - 248, 340)}x{h}")


def _send_cheat_command(text: str) -> None:
    """Al hacer clic en un comando del panel: activa el modo teclado si
    hace falta y lo tipea letra por letra, listo para que el usuario lo
    revise y presione ENVIAR."""
    if not _kb_active:
        _toggle_keyboard_mode(_kb_toggle_btn, _kb_frame)
    if not _kb_entry:
        return
    _type_cheat_command(text, 0)


def _type_cheat_command(text: str, i: int) -> None:
    if not _kb_entry or not _root:
        return
    _kb_entry.delete(0, tk.END)
    _kb_entry.insert(0, text[:i])
    if i < len(text):
        _root.after(26, _type_cheat_command, text, i + 1)
    else:
        _kb_entry.focus_set()
        _kb_entry.icursor(tk.END)


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
            _player_bar.grid(row=3, column=0, sticky="ew", pady=(10, 0))
            if _player_bar else None,
            _player_label.config(text=f"♫  {t.upper()}") if _player_label else None,
        ))
    else:
        _safe(lambda: (
            _player_bar.grid_remove() if _player_bar else None,
        ))


def confirm_action(image_bytes: bytes, description: str,
                    target_xy: tuple[int, int] | None = None,
                    timeout: float = 60.0) -> bool:
    """Muestra la captura de pantalla + la acción propuesta por
    core/it_worker.py y bloquea hasta que el usuario responda Sí/No (o pasen
    `timeout` segundos, que cuenta como No). Se llama desde el hilo del
    tool, no del hilo de la GUI — por eso se agenda con _safe() y se
    sincroniza con un Event, igual que cualquier cosa que toque widgets de
    Tk desde otro hilo."""
    if not _available or not _root:
        return False

    result = {"ok": False}
    done = threading.Event()

    def ask():
        try:
            _build_confirm_dialog(image_bytes, description, target_xy, result, done)
        except Exception as error:
            print(f"K.A.N.Y.E.: Error mostrando confirmación: {error}")
            done.set()

    _safe(ask)
    done.wait(timeout=timeout)
    return result["ok"]


def _build_confirm_dialog(image_bytes: bytes, description: str,
                           target_xy: tuple[int, int] | None,
                           result: dict, done: threading.Event) -> None:
    import io
    from PIL import Image, ImageTk

    top = tk.Toplevel(_root)
    top.title("K.A.N.Y.E. — Confirmar acción")
    top.configure(bg=theme.VOID)
    top.attributes("-topmost", True)

    img = Image.open(io.BytesIO(image_bytes))
    max_w, max_h = 900, 600
    scale = min(max_w / img.width, max_h / img.height, 1.0)
    disp_w, disp_h = max(1, int(img.width * scale)), max(1, int(img.height * scale))
    photo = ImageTk.PhotoImage(img.resize((disp_w, disp_h)))

    canvas = tk.Canvas(top, width=disp_w, height=disp_h, bg=theme.VOID, highlightthickness=0)
    canvas.pack(padx=12, pady=(12, 6))
    canvas.create_image(0, 0, anchor="nw", image=photo)
    canvas.image = photo  # evitar que el GC se lo lleve antes de tiempo

    if target_xy:
        tx, ty = target_xy[0] * scale, target_xy[1] * scale
        r = 10
        canvas.create_oval(tx - r, ty - r, tx + r, ty + r, outline=theme.DANGER, width=3)

    tk.Label(top, text=description, bg=theme.VOID, fg=theme.TEXT,
             font=theme.mono_font(10), wraplength=disp_w, justify="left"
             ).pack(padx=12, pady=(0, 12), fill=tk.X)

    btn_row = tk.Frame(top, bg=theme.VOID)
    btn_row.pack(pady=(0, 16))

    def respond(ok: bool):
        result["ok"] = ok
        done.set()
        top.destroy()

    tk.Button(btn_row, text="SÍ", command=lambda: respond(True),
              bg=theme.ACCENT, fg=theme.ON_ACCENT, font=theme.display_font(12),
              relief=tk.FLAT, padx=24, pady=8, cursor="hand2"
              ).pack(side=tk.LEFT, padx=(0, 8))
    tk.Button(btn_row, text="NO", command=lambda: respond(False),
              bg=theme.INK2, fg=theme.TEXT, font=theme.display_font(12),
              relief=tk.FLAT, padx=24, pady=8, cursor="hand2"
              ).pack(side=tk.LEFT)

    top.protocol("WM_DELETE_WINDOW", lambda: respond(False))


def ask_permission(description: str, timeout: float = 60.0) -> str:
    """Pregunta al usuario si autoriza tocar un archivo fuera de los
    workspaces conocidos. Devuelve 'once', 'always' o 'no' (timeout cuenta
    como 'no'). Se llama desde el hilo del tool, no el de la GUI."""
    if not _available or not _root:
        return "no"

    result = {"choice": "no"}
    done = threading.Event()

    def ask():
        try:
            _build_permission_dialog(description, result, done)
        except Exception as error:
            print(f"K.A.N.Y.E.: Error mostrando permiso: {error}")
            done.set()

    _safe(ask)
    done.wait(timeout=timeout)
    return result["choice"]


def _build_permission_dialog(description: str, result: dict, done: threading.Event) -> None:
    top = tk.Toplevel(_root)
    top.title("K.A.N.Y.E. — Permiso de archivo")
    top.configure(bg=theme.VOID)
    top.attributes("-topmost", True)

    tk.Label(top, text=description, bg=theme.VOID, fg=theme.TEXT,
              font=theme.mono_font(10), wraplength=420, justify="left"
              ).pack(padx=20, pady=(20, 12), fill=tk.X)

    btn_row = tk.Frame(top, bg=theme.VOID)
    btn_row.pack(pady=(0, 20))

    def respond(choice: str):
        result["choice"] = choice
        done.set()
        top.destroy()

    tk.Button(btn_row, text="SOLO UNA VEZ", command=lambda: respond("once"),
              bg=theme.INK2, fg=theme.TEXT, font=theme.display_font(11),
              relief=tk.FLAT, padx=16, pady=8, cursor="hand2"
              ).pack(side=tk.LEFT, padx=(0, 8))
    tk.Button(btn_row, text="SIEMPRE", command=lambda: respond("always"),
              bg=theme.ACCENT, fg=theme.ON_ACCENT, font=theme.display_font(11),
              relief=tk.FLAT, padx=16, pady=8, cursor="hand2"
              ).pack(side=tk.LEFT, padx=(0, 8))
    tk.Button(btn_row, text="NO", command=lambda: respond("no"),
              bg=theme.INK2, fg=theme.DANGER, font=theme.display_font(11),
              relief=tk.FLAT, padx=16, pady=8, cursor="hand2"
              ).pack(side=tk.LEFT)

    top.protocol("WM_DELETE_WINDOW", lambda: respond("no"))
