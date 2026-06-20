"""
Ventana de configuración visual de K.A.N.Y.E.
Permite editar config.local.json, modes.json y sites.json sin tocar archivos.
"""
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path

from core.config_loader import PROJECT_ROOT

CONFIG_LOCAL = PROJECT_ROOT / "config" / "config.local.json"
MODES_FILE   = PROJECT_ROOT / "config" / "modes.json"
SITES_FILE   = PROJECT_ROOT / "config" / "sites.json"

# ── Paleta ────────────────────────────────────────────────────────────────────
BG    = "#111111"
BG2   = "#1C1C1C"
BG3   = "#252525"
FG    = "#E8E8E8"
FG2   = "#AAAAAA"
ACC   = "#C8A000"
SEL   = "#2A3A2A"
FONT  = ("Monospace", 10)
FONTS = ("Monospace", 9)
FONTB = ("Monospace", 11, "bold")

_win = None


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
                    highlightthickness=1, highlightbackground="#333")
    except Exception:
        pass


def _btn(parent, text, cmd, color=ACC):
    return tk.Button(
        parent, text=text, command=cmd,
        bg=BG3, fg=color, font=FONTS,
        activebackground="#333", activeforeground=color,
        relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
    )


# ── Tab Configuración ─────────────────────────────────────────────────────────

def _build_config_tab(nb: ttk.Notebook):
    frame = tk.Frame(nb, bg=BG)
    nb.add(frame, text="  Configuración  ")

    canvas = tk.Canvas(frame, bg=BG, highlightthickness=0)
    scroll = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    inner  = tk.Frame(canvas, bg=BG)

    inner.bind("<Configure>", lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scroll.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    from core.config_loader import get_config
    current = get_config()
    local   = _load(CONFIG_LOCAL)

    FIELDS = [
        ("hotkey",              "Hotkey",               "entry",    "ctrl+f9"),
        ("chat_model",          "Modelo de chat",        "entry",    "phi4-mini"),
        ("intent_model",        "Modelo de intención",   "entry",    "qwen2.5:1.5b"),
        ("stt_whisper_model",   "Modelo Whisper",        "combo",    ["tiny","base","small","medium"]),
        ("use_llm_classifier",  "Usar clasificador LLM", "check",    True),
        ("language",            "Idioma STT",            "entry",    "es"),
        ("stt_silence_secs",    "Segundos de silencio",  "entry",    "1.5"),
        ("stt_max_secs",        "Máx. segundos grabando","entry",    "10.0"),
        ("stt_silence_threshold","Umbral de silencio",   "entry",    "500"),
        ("voice_model",         "Modelo de voz (.onnx)", "entry",    "voices/es_ES-davefx-medium.onnx"),
    ]

    widgets = {}

    for i, (key, label, wtype, default) in enumerate(FIELDS):
        val = current.get(key, default)

        tk.Label(inner, text=label, bg=BG, fg=FG2, font=FONTS,
                 anchor="w").grid(row=i, column=0, sticky="w", padx=16, pady=(8,0))

        if wtype == "entry":
            var = tk.StringVar(value=str(val))
            e = tk.Entry(inner, textvariable=var, width=36)
            _style_widget(e)
            e.grid(row=i, column=1, sticky="ew", padx=16, pady=(8,0))
            widgets[key] = ("entry", var)

        elif wtype == "combo":
            var = tk.StringVar(value=str(val))
            c = ttk.Combobox(inner, textvariable=var, values=default, width=18, state="readonly")
            c.grid(row=i, column=1, sticky="w", padx=16, pady=(8,0))
            widgets[key] = ("entry", var)

        elif wtype == "check":
            var = tk.BooleanVar(value=bool(val))
            cb = tk.Checkbutton(inner, variable=var, bg=BG, fg=FG,
                                selectcolor=BG3, activebackground=BG,
                                font=FONT)
            cb.grid(row=i, column=1, sticky="w", padx=16, pady=(8,0))
            widgets[key] = ("bool", var)

    inner.columnconfigure(1, weight=1)

    def save():
        data = {}
        for key, (wtype, var) in widgets.items():
            raw = var.get()
            if wtype == "bool":
                data[key] = bool(raw)
            else:
                try:
                    if "." in str(raw):
                        data[key] = float(raw)
                    else:
                        data[key] = int(raw)
                except ValueError:
                    data[key] = raw
        if _save(CONFIG_LOCAL, data):
            messagebox.showinfo("Guardado", "config.local.json guardado.\nReiniciá K.A.N.Y.E. para aplicar los cambios.")

    tk.Frame(inner, bg=BG, height=12).grid(row=len(FIELDS), columnspan=2)
    _btn(inner, "Guardar configuración", save).grid(
        row=len(FIELDS)+1, column=0, columnspan=2, pady=12, padx=16, sticky="ew")

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
                        highlightthickness=1, highlightbackground="#333")
            t.grid(row=row, column=1, sticky="ew", pady=(8,0), padx=4)
            fields[key] = ("text", t)
        else:
            var = tk.StringVar()
            e = tk.Entry(parent, textvariable=var, bg=BG2, fg=FG, font=FONT,
                         insertbackground=FG, relief=tk.FLAT,
                         highlightthickness=1, highlightbackground="#333")
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
                     highlightthickness=1, highlightbackground="#333")
    e_dur.grid(row=8, column=1, sticky="w", padx=4, pady=(4,0))
    focus_vars["duration"] = focus_dur

    focus_sites = tk.Text(edit_frame, height=3, width=36, bg=BG2, fg=FG, font=FONT,
                          insertbackground=FG, relief=tk.FLAT,
                          highlightthickness=1, highlightbackground="#333")
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
    _btn(btn_row, "+ Nuevo",  new_mode,  "#50C878").pack(side=tk.LEFT, padx=(0,6))
    _btn(btn_row, "Eliminar", delete_mode, "#C85050").pack(side=tk.LEFT)

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
                      highlightthickness=1, highlightbackground="#333")
    name_e.pack(side=tk.LEFT, padx=(4,12))

    tk.Label(edit_row, text="URL:", bg=BG, fg=FG2, font=FONTS).pack(side=tk.LEFT)
    url_var = tk.StringVar()
    url_e = tk.Entry(edit_row, textvariable=url_var, width=36, bg=BG2, fg=FG,
                     font=FONT, insertbackground=FG, relief=tk.FLAT,
                     highlightthickness=1, highlightbackground="#333")
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
    _btn(btn_row, "Eliminar", delete_site, "#C85050").pack(side=tk.LEFT)

    refresh_tree()
    return frame


# ── Ventana principal ─────────────────────────────────────────────────────────

def open_settings(parent=None):
    global _win
    if _win and _win.winfo_exists():
        _win.lift()
        return

    win = tk.Toplevel(parent) if parent else tk.Tk()
    win.title("K.A.N.Y.E. — Configuración")
    win.geometry("640x560")
    win.configure(bg=BG)
    win.resizable(True, True)

    tk.Label(win, text="Configuración", bg=BG, fg=ACC, font=FONTB).pack(
        pady=(12, 4))

    style = ttk.Style(win)
    style.theme_use("clam")
    style.configure("Kanye.TNotebook",       background=BG,  borderwidth=0)
    style.configure("Kanye.TNotebook.Tab",   background=BG3, foreground=FG2,
                    padding=(12,6), font=FONTS)
    style.map("Kanye.TNotebook.Tab",
              background=[("selected", BG2)],
              foreground=[("selected", ACC)])

    nb = ttk.Notebook(win, style="Kanye.TNotebook")
    nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0,8))

    _build_config_tab(nb)
    _build_modes_tab(nb)
    _build_sites_tab(nb)

    _win = win
    if not parent:
        win.mainloop()
