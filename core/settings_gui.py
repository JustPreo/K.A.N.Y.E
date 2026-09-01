"""
Ventana de configuración visual de K.A.N.Y.E.
Permite editar config.local.json, modes.json y sites.json sin tocar archivos.
"""
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path

from core.config_loader import PROJECT_ROOT
from core import theme

CONFIG_LOCAL = PROJECT_ROOT / "config" / "config.local.json"
MODES_FILE   = PROJECT_ROOT / "config" / "modes.json"
SITES_FILE   = PROJECT_ROOT / "config" / "sites.json"

# ── Paleta (core/theme.py) ─────────────────────────────────────────────────────
BG    = theme.VOID
BG2   = theme.INK
BG3   = theme.INK2
FG    = theme.TEXT
FG2   = theme.TEXT_DIM
ACC   = theme.ACCENT
SEL   = theme.ACCENT_DIM
LINE  = theme.LINE

_win = None

# Se resuelven en open_settings() una vez que existe un root Tk — la
# resolución de familias de fuente (core/theme.py) necesita uno.
FONT  = ("TkFixedFont", 10)
FONTS = ("TkFixedFont", 9)
FONTB = ("TkDefaultFont", 13, "bold")


def _resolve_fonts() -> None:
    global FONT, FONTS, FONTB
    FONT  = theme.mono_font(10)
    FONTS = theme.mono_font(9)
    FONTB = theme.display_font(13, "bold")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load(path: Path) -> dict | list:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {} if path.suffix == ".json" else []


def _save(path: Path, data) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar:\n{e}")
        return False


def _style_widget(w, bg=BG2, fg=FG):
    try:
        w.configure(bg=bg, fg=fg, font=FONT,
                    insertbackground=FG, relief=tk.FLAT,
                    highlightthickness=1, highlightbackground=LINE)
    except Exception:
        pass


def _btn(parent, text, cmd, color=ACC):
    return tk.Button(
        parent, text=text, command=cmd,
        bg=BG3, fg=color, font=FONTS,
        activebackground=LINE, activeforeground=color,
        relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
    )


# ── Tab Configuración ─────────────────────────────────────────────────────────

def _detect_voice_models() -> list[str]:
    voices_dir = PROJECT_ROOT / "voices"
    found = sorted(str(p.relative_to(PROJECT_ROOT)) for p in voices_dir.glob("*.onnx")) if voices_dir.exists() else []
    return found or ["voices/es_ES-davefx-medium.onnx"]


# Cada sección agrupa campos relacionados para que la pantalla no sea una
# lista plana de 15 cajas de texto sueltas.
# tipos: combo (dropdown fijo), combo_edit (dropdown + se puede tipear
# otro valor), combo_files (dropdown autodetectado), spin (numérico con
# flechas), check (sí/no), password (oculto, con botón de ojo).
def _build_sections(voice_models: list[str]) -> list[tuple[str, list[tuple]]]:
    return [
        ("GENERAL", [
            ("hotkey", "Hotkey para activar", "combo_edit",
             ["ctrl+f9", "ctrl+shift+k", "alt+space", "ctrl+alt+k"], "ctrl+f9"),
            ("startup_tts", "Anunciar inicio por voz", "check", None, True),
            ("auto_listen_on_hotkey", "Escuchar de una al presionar el hotkey", "check", None, True),
        ]),
        ("VOZ Y RECONOCIMIENTO", [
            ("language", "Idioma de reconocimiento", "combo",
             ["es", "en", "pt", "fr", "de", "it"], "es"),
            ("stt_whisper_model", "Modelo Whisper", "combo",
             ["tiny", "base", "small", "medium"], "base"),
            ("voice_model", "Voz (Piper)", "combo_files", voice_models, voice_models[0]),
            ("stt_silence_secs", "Segundos de silencio para cortar", "spin",
             (0.5, 5.0, 0.5), 1.5),
            ("stt_max_secs", "Máx. segundos grabando", "spin",
             (3, 30, 1), 10.0),
            ("stt_silence_threshold", "Sensibilidad del micrófono (umbral)", "spin",
             (100, 5000, 100), 500),
        ]),
        ("AGENTE", [
            ("chat_backend", "Backend del agente", "combo",
             ["ollama", "deepseek"], "ollama"),
            ("chat_model", "Modelo del agente (Ollama)", "combo_edit",
             ["phi4-mini", "qwen2.5:7b", "llama3.2", "mistral", "gemma2"], "phi4-mini"),
            ("max_tool_iterations", "Máx. acciones encadenadas", "spin",
             (1, 15, 1), 6),
            ("deepseek_model", "Modelo DeepSeek", "combo_edit",
             ["deepseek-chat", "deepseek-reasoner"], "deepseek-chat"),
            ("deepseek_api_key", "DeepSeek API key", "password", None, ""),
        ]),
        ("AYUDA REMOTA", [
            ("it_worker_model", "Modelo de visión (DeepSeek)", "combo_edit",
             ["deepseek-v4-flash-vision-exp"], "deepseek-v4-flash-vision-exp"),
            ("it_worker_max_steps", "Máx. pasos por sesión", "spin",
             (3, 15, 1), 8),
        ]),
    ]


def _build_config_tab(nb: ttk.Notebook):
    frame = tk.Frame(nb, bg=BG)
    nb.add(frame, text="  Configuración  ")

    canvas = tk.Canvas(frame, bg=BG, highlightthickness=0)
    scroll = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    inner  = tk.Frame(canvas, bg=BG)

    inner.bind("<Configure>", lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")))
    canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.bind("<Configure>", lambda e: canvas.itemconfigure(canvas_window, width=e.width))
    canvas.configure(yscrollcommand=scroll.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _on_wheel(evt):
        canvas.yview_scroll(-1 if evt.delta > 0 else 1, "units")
    canvas.bind_all("<MouseWheel>", _on_wheel)
    canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    from core.config_loader import get_config
    current = get_config()

    widgets = {}
    row = 0

    for section_title, fields in _build_sections(_detect_voice_models()):
        if row > 0:
            tk.Frame(inner, bg=BG, height=14).grid(row=row, columnspan=2)
            row += 1

        tk.Label(inner, text=section_title, bg=BG, fg=ACC, font=FONTB,
                 anchor="w").grid(row=row, columnspan=2, sticky="w", padx=14, pady=(4, 2))
        row += 1
        tk.Frame(inner, bg=LINE, height=1).grid(
            row=row, columnspan=2, sticky="ew", padx=14, pady=(0, 6))
        row += 1

        for key, label, wtype, options, default in fields:
            val = current.get(key, default)

            tk.Label(inner, text=label, bg=BG, fg=FG2, font=FONTS,
                     anchor="w").grid(row=row, column=0, sticky="w", padx=(24, 8), pady=6)

            if wtype in ("combo", "combo_edit", "combo_files"):
                choices = options if wtype != "combo_files" else options
                var = tk.StringVar(value=str(val))
                state = "readonly" if wtype == "combo" else "normal"
                c = ttk.Combobox(inner, textvariable=var, values=choices,
                                  width=28, state=state, font=FONTS)
                c.grid(row=row, column=1, sticky="w", padx=16, pady=6)
                widgets[key] = ("str", var)

            elif wtype == "spin":
                lo, hi, step = options
                var = tk.StringVar(value=str(val))
                s = ttk.Spinbox(inner, from_=lo, to=hi, increment=step,
                                 textvariable=var, width=10, font=FONTS)
                s.grid(row=row, column=1, sticky="w", padx=16, pady=6)
                widgets[key] = ("num", var)

            elif wtype == "check":
                var = tk.BooleanVar(value=bool(val))
                cb = tk.Checkbutton(inner, variable=var, bg=BG, fg=FG,
                                     selectcolor=BG3, activebackground=BG,
                                     font=FONT)
                cb.grid(row=row, column=1, sticky="w", padx=16, pady=6)
                widgets[key] = ("bool", var)

            elif wtype == "password":
                pw_frame = tk.Frame(inner, bg=BG)
                pw_frame.grid(row=row, column=1, sticky="ew", padx=16, pady=6)
                var = tk.StringVar(value=str(val))
                e = tk.Entry(pw_frame, textvariable=var, show="•", width=30)
                _style_widget(e)
                e.pack(side=tk.LEFT, fill=tk.X, expand=True)

                eye_btn = tk.Button(pw_frame, text="MOSTRAR",
                                     bg=BG3, fg=FG2, activebackground=LINE,
                                     relief=tk.FLAT, cursor="hand2", padx=6)

                def toggle_show(entry=e, btn=eye_btn):
                    hidden = entry.cget("show") == "•"
                    entry.configure(show="" if hidden else "•")
                    btn.configure(text="OCULTAR" if hidden else "MOSTRAR")

                eye_btn.configure(command=toggle_show)
                eye_btn.pack(side=tk.LEFT, padx=(4, 0))
                widgets[key] = ("str", var)

            row += 1

    inner.columnconfigure(1, weight=1)

    def save():
        data = {}
        for key, (kind, var) in widgets.items():
            raw = var.get()
            if kind == "bool":
                data[key] = bool(raw)
            elif kind == "num":
                try:
                    data[key] = float(raw) if "." in str(raw) else int(raw)
                except ValueError:
                    data[key] = raw
            else:
                data[key] = raw
        if _save(CONFIG_LOCAL, data):
            messagebox.showinfo("Guardado", "Configuración guardada.\nReiniciá K.A.N.Y.E. para aplicar los cambios.")

    tk.Frame(inner, bg=BG, height=12).grid(row=row, columnspan=2)
    row += 1
    _btn(inner, "GUARDAR CONFIGURACIÓN", save).grid(
        row=row, column=0, columnspan=2, pady=(4, 16), padx=16, sticky="ew")

    return frame


# ── Tab Modos ─────────────────────────────────────────────────────────────────

def _build_modes_tab(nb: ttk.Notebook):
    frame = tk.Frame(nb, bg=BG)
    nb.add(frame, text="  Modos  ")

    # Lista
    list_frame = tk.Frame(frame, bg=BG2, width=160)
    list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(8,0), pady=8)
    list_frame.pack_propagate(False)

    tk.Label(list_frame, text="Modos", bg=BG2, fg=ACC, font=FONTB).pack(pady=(8,4))

    lb = tk.Listbox(list_frame, bg=BG2, fg=FG, font=FONT,
                    selectbackground=SEL, selectforeground=FG,
                    relief=tk.FLAT, highlightthickness=0, bd=0)
    lb.pack(fill=tk.BOTH, expand=True, padx=4)

    # Panel edición
    edit_frame = tk.Frame(frame, bg=BG)
    edit_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

    fields = {}
    focus_vars = {}

    def make_field(parent, label, key, row, multiline=False):
        tk.Label(parent, text=label, bg=BG, fg=FG2, font=FONTS,
                 anchor="w").grid(row=row, column=0, sticky="nw", pady=(8,0), padx=4)
        if multiline:
            t = tk.Text(parent, height=3, width=36, bg=BG2, fg=FG, font=FONT,
                        insertbackground=FG, relief=tk.FLAT,
                        highlightthickness=1, highlightbackground=LINE)
            t.grid(row=row, column=1, sticky="ew", pady=(8,0), padx=4)
            fields[key] = ("text", t)
        else:
            var = tk.StringVar()
            e = tk.Entry(parent, textvariable=var, bg=BG2, fg=FG, font=FONT,
                         insertbackground=FG, relief=tk.FLAT,
                         highlightthickness=1, highlightbackground=LINE)
            e.grid(row=row, column=1, sticky="ew", pady=(8,0), padx=4)
            fields[key] = ("entry", var)

    tk.Label(edit_frame, text="Editar modo", bg=BG, fg=ACC, font=FONTB).grid(
        row=0, columnspan=2, sticky="w", padx=4, pady=(4,0))

    make_field(edit_frame, "Apps (coma)",     "apps",     1, multiline=True)
    make_field(edit_frame, "URLs (coma)",     "urls",     2, multiline=True)
    make_field(edit_frame, "Carpetas (coma)", "folders",  3, multiline=True)
    make_field(edit_frame, "Mensaje",         "message",  4)

    # Cerrar antes
    close_var = tk.BooleanVar()
    tk.Label(edit_frame, text="Cerrar apps antes", bg=BG, fg=FG2,
             font=FONTS, anchor="w").grid(row=5, column=0, sticky="w", padx=4, pady=(8,0))
    tk.Checkbutton(edit_frame, variable=close_var, bg=BG, fg=FG,
                   selectcolor=BG3, activebackground=BG,
                   font=FONT).grid(row=5, column=1, sticky="w", padx=4, pady=(8,0))

    # Focus
    tk.Label(edit_frame, text="── Focus ──", bg=BG, fg=FG2,
             font=FONTS).grid(row=6, columnspan=2, sticky="w", padx=4, pady=(12,0))

    focus_enabled = tk.BooleanVar()
    tk.Label(edit_frame, text="Focus activado", bg=BG, fg=FG2,
             font=FONTS, anchor="w").grid(row=7, column=0, sticky="w", padx=4)
    tk.Checkbutton(edit_frame, variable=focus_enabled, bg=BG, fg=FG,
                   selectcolor=BG3, activebackground=BG,
                   font=FONT).grid(row=7, column=1, sticky="w", padx=4)
    focus_vars["enabled"] = focus_enabled

    focus_dur = tk.StringVar(value="50")
    tk.Label(edit_frame, text="Duración (min)", bg=BG, fg=FG2,
             font=FONTS, anchor="w").grid(row=8, column=0, sticky="w", padx=4, pady=(4,0))
    e_dur = tk.Entry(edit_frame, textvariable=focus_dur, width=8, bg=BG2, fg=FG,
                     font=FONT, insertbackground=FG, relief=tk.FLAT,
                     highlightthickness=1, highlightbackground=LINE)
    e_dur.grid(row=8, column=1, sticky="w", padx=4, pady=(4,0))
    focus_vars["duration"] = focus_dur

    focus_sites = tk.Text(edit_frame, height=3, width=36, bg=BG2, fg=FG, font=FONT,
                          insertbackground=FG, relief=tk.FLAT,
                          highlightthickness=1, highlightbackground=LINE)
    tk.Label(edit_frame, text="Sitios bloqueados\n(uno por línea)", bg=BG, fg=FG2,
             font=FONTS, anchor="nw").grid(row=9, column=0, sticky="nw", padx=4, pady=(4,0))
    focus_sites.grid(row=9, column=1, sticky="ew", padx=4, pady=(4,0))
    focus_vars["sites"] = focus_sites

    edit_frame.columnconfigure(1, weight=1)

    modes_data    = [_load(MODES_FILE)]
    selected_mode = [None]  # nombre del modo actualmente cargado en el panel

    def refresh_list():
        lb.delete(0, tk.END)
        for name in modes_data[0]:
            lb.insert(tk.END, f"  {name}")

    def on_select(evt=None):
        sel = lb.curselection()
        if not sel:
            return
        name = lb.get(sel[0]).strip()
        selected_mode[0] = name
        m = modes_data[0].get(name, {})

        def set_text(widget, val):
            widget.delete("1.0", tk.END)
            widget.insert("1.0", val)

        def set_entry(var, val):
            var.set(str(val))

        set_text(fields["apps"][1],    ", ".join(m.get("apps", [])))
        set_text(fields["urls"][1],    ", ".join(m.get("urls", [])))
        set_text(fields["folders"][1], ", ".join(m.get("folders", [])))
        set_entry(fields["message"][1], m.get("message", ""))
        close_var.set(m.get("close_before", False))

        fc = m.get("focus", {})
        focus_enabled.set(fc.get("enabled", False))
        focus_dur.set(str(fc.get("duration_minutes", 50)))
        focus_sites.delete("1.0", tk.END)
        focus_sites.insert("1.0", "\n".join(fc.get("blocked_sites", [])))

    lb.bind("<<ListboxSelect>>", on_select)

    def save_mode():
        name = selected_mode[0]
        if not name:
            messagebox.showwarning("Sin selección", "Seleccioná un modo primero.")
            return

        def get_list(key):
            raw = fields[key][1].get("1.0", tk.END).strip()
            return [x.strip() for x in raw.split(",") if x.strip()]

        mode = {
            "close_before": close_var.get(),
            "apps":    get_list("apps"),
            "urls":    get_list("urls"),
            "folders": get_list("folders"),
            "message": fields["message"][1].get().strip(),
        }
        if focus_enabled.get():
            sites_raw = focus_sites.get("1.0", tk.END).strip()
            mode["focus"] = {
                "enabled": True,
                "duration_minutes": int(focus_dur.get() or 50),
                "blocked_sites": [s.strip() for s in sites_raw.splitlines() if s.strip()],
            }
        modes_data[0][name] = mode
        if _save(MODES_FILE, modes_data[0]):
            messagebox.showinfo("Guardado", f"Modo '{name}' guardado.")

    def new_mode():
        name = simpledialog.askstring("Nuevo modo", "Nombre del modo:",
                                      parent=frame)
        if not name:
            return
        name = name.lower().strip()
        if name in modes_data[0]:
            messagebox.showwarning("Ya existe", f"El modo '{name}' ya existe.")
            return
        modes_data[0][name] = {
            "close_before": False, "apps": [], "urls": [],
            "folders": [], "message": f"Modo {name} activado."
        }
        _save(MODES_FILE, modes_data[0])
        refresh_list()
        selected_mode[0] = name
        lb.select_set(tk.END)
        on_select()

    def delete_mode():
        name = selected_mode[0]
        if not name:
            return
        if messagebox.askyesno("Eliminar", f"¿Eliminar el modo '{name}'?"):
            del modes_data[0][name]
            _save(MODES_FILE, modes_data[0])
            selected_mode[0] = None
            refresh_list()

    btn_row = tk.Frame(edit_frame, bg=BG)
    btn_row.grid(row=10, columnspan=2, pady=10, padx=4, sticky="ew")
    _btn(btn_row, "Guardar",  save_mode, ACC).pack(side=tk.LEFT, padx=(0,6))
    _btn(btn_row, "+ Nuevo",  new_mode,  theme.STATE_COLORS["listening"]).pack(side=tk.LEFT, padx=(0,6))
    _btn(btn_row, "Eliminar", delete_mode, theme.DANGER).pack(side=tk.LEFT)

    refresh_list()
    return frame


# ── Tab Sitios ────────────────────────────────────────────────────────────────

def _build_sites_tab(nb: ttk.Notebook):
    frame = tk.Frame(nb, bg=BG)
    nb.add(frame, text="  Sitios  ")

    sites_data = [_load(SITES_FILE)]

    # Treeview
    tree_frame = tk.Frame(frame, bg=BG)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8,0))

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Kanye.Treeview",
                    background=BG2, foreground=FG,
                    fieldbackground=BG2, font=FONT, rowheight=26)
    style.configure("Kanye.Treeview.Heading",
                    background=BG3, foreground=ACC, font=FONTS)
    style.map("Kanye.Treeview", background=[("selected", SEL)])

    tree = ttk.Treeview(tree_frame, columns=("nombre","url"), show="headings",
                        style="Kanye.Treeview")
    tree.heading("nombre", text="Nombre")
    tree.heading("url",    text="URL")
    tree.column("nombre", width=150, stretch=False)
    tree.column("url",    width=300, stretch=True)

    sb = tk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb.pack(side=tk.RIGHT, fill=tk.Y)

    # Edición inline
    edit_row = tk.Frame(frame, bg=BG)
    edit_row.pack(fill=tk.X, padx=8, pady=6)

    tk.Label(edit_row, text="Nombre:", bg=BG, fg=FG2, font=FONTS).pack(side=tk.LEFT)
    name_var = tk.StringVar()
    name_e = tk.Entry(edit_row, textvariable=name_var, width=18, bg=BG2, fg=FG,
                      font=FONT, insertbackground=FG, relief=tk.FLAT,
                      highlightthickness=1, highlightbackground=LINE)
    name_e.pack(side=tk.LEFT, padx=(4,12))

    tk.Label(edit_row, text="URL:", bg=BG, fg=FG2, font=FONTS).pack(side=tk.LEFT)
    url_var = tk.StringVar()
    url_e = tk.Entry(edit_row, textvariable=url_var, width=36, bg=BG2, fg=FG,
                     font=FONT, insertbackground=FG, relief=tk.FLAT,
                     highlightthickness=1, highlightbackground=LINE)
    url_e.pack(side=tk.LEFT, padx=(4,0), fill=tk.X, expand=True)

    def refresh_tree():
        tree.delete(*tree.get_children())
        for name, url in sorted(sites_data[0].items()):
            tree.insert("", tk.END, values=(name, url))

    def on_select(evt=None):
        sel = tree.selection()
        if sel:
            vals = tree.item(sel[0], "values")
            name_var.set(vals[0])
            url_var.set(vals[1])

    tree.bind("<<TreeviewSelect>>", on_select)

    def save_site():
        name = name_var.get().strip().lower()
        url  = url_var.get().strip()
        if not name or not url:
            messagebox.showwarning("Incompleto", "Completá nombre y URL.")
            return
        if not url.startswith("http"):
            url = "https://" + url
        sites_data[0][name] = url
        if _save(SITES_FILE, sites_data[0]):
            refresh_tree()
            name_var.set("")
            url_var.set("")

    def delete_site():
        sel = tree.selection()
        if not sel:
            return
        name = tree.item(sel[0], "values")[0]
        if messagebox.askyesno("Eliminar", f"¿Eliminar '{name}'?"):
            del sites_data[0][name]
            _save(SITES_FILE, sites_data[0])
            refresh_tree()
            name_var.set("")
            url_var.set("")

    btn_row = tk.Frame(frame, bg=BG)
    btn_row.pack(fill=tk.X, padx=8, pady=(0,8))
    _btn(btn_row, "Guardar / Actualizar", save_site, ACC).pack(side=tk.LEFT, padx=(0,6))
    _btn(btn_row, "Eliminar", delete_site, theme.DANGER).pack(side=tk.LEFT)

    refresh_tree()
    return frame


# ── Ventana principal ─────────────────────────────────────────────────────────

def open_settings(parent=None):
    global _win
    if _win and _win.winfo_exists():
        _win.lift()
        return

    win = tk.Toplevel(parent) if parent else tk.Tk()
    _resolve_fonts()
    win.title("K.A.N.Y.E. — Configuración")
    win.geometry("640x560")
    win.configure(bg=BG)
    win.resizable(True, True)

    title_row = tk.Frame(win, bg=BG)
    title_row.pack(fill=tk.X, padx=16, pady=(16, 4))
    tk.Label(title_row, text="C·O·N·F·I·G·U·R·A·C·I·Ó·N", bg=BG, fg=ACC, font=FONTB).pack(side=tk.LEFT)
    tk.Frame(win, bg=ACC, height=2).pack(fill=tk.X, padx=16, pady=(0, 8))

    style = ttk.Style(win)
    style.theme_use("clam")
    style.configure("Kanye.TNotebook",       background=BG,  borderwidth=0)
    style.configure("Kanye.TNotebook.Tab",   background=BG3, foreground=FG2,
                    padding=(14,7), font=FONTS)
    style.map("Kanye.TNotebook.Tab",
              background=[("selected", BG2)],
              foreground=[("selected", ACC)])

    # Combobox / Spinbox oscuros, para que no desentonen con el resto.
    style.configure("TCombobox",
                     fieldbackground=BG2, background=BG2, foreground=FG,
                     arrowcolor=ACC, bordercolor=LINE, lightcolor=BG2, darkcolor=BG2)
    style.map("TCombobox",
              fieldbackground=[("readonly", BG2), ("disabled", BG2)],
              foreground=[("readonly", FG), ("disabled", FG2)],
              selectbackground=[("readonly", BG2)],
              selectforeground=[("readonly", FG)])
    win.option_add("*TCombobox*Listbox.background", BG2)
    win.option_add("*TCombobox*Listbox.foreground", FG)
    win.option_add("*TCombobox*Listbox.selectBackground", SEL)
    win.option_add("*TCombobox*Listbox.font", FONTS)

    style.configure("TSpinbox",
                     fieldbackground=BG2, background=BG2, foreground=FG,
                     arrowcolor=ACC, bordercolor=LINE, lightcolor=BG2, darkcolor=BG2)
    style.map("TSpinbox", fieldbackground=[("readonly", BG2)])

    nb = ttk.Notebook(win, style="Kanye.TNotebook")
    nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0,8))

    _build_config_tab(nb)
    _build_modes_tab(nb)
    _build_sites_tab(nb)

    _win = win
    if not parent:
        win.mainloop()
