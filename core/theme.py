"""
Sistema de diseño compartido de K.A.N.Y.E.: paleta, tipografía y colores de
estado. Un solo lugar para que gui.py, settings_gui.py y tray_icon.py no
diverjan en los mismos valores.

Dirección visual: brutalista/editorial. Negro puro, un acento dorado
saturado, bloques de color en vez de degradados, sin esquinas redondeadas.
"""
import tkinter.font as tkfont

# ── Paleta ────────────────────────────────────────────────────────────────────
VOID     = "#0A0A0A"   # fondo base
INK      = "#141414"   # panel
INK2     = "#1E1E1E"   # superficie elevada / hover
LINE     = "#2A2A2A"   # línea divisoria
TEXT     = "#F2F2F0"   # texto primario
TEXT_DIM = "#6B6B6B"   # texto secundario
GOLD     = "#FFC300"   # acento de marca
GOLD_DIM = "#7A5D00"   # acento apagado (bordes, texto secundario dorado)
ON_GOLD  = VOID         # texto sobre superficies doradas
DANGER   = "#FF3B3B"

STATE_COLORS = {
    "idle":       "#4D4D4D",
    "listening":  "#39FF6A",
    "processing": "#FF8A00",
    "speaking":   "#33B1FF",
    "error":      DANGER,
}

STATE_TEXT = {
    "idle":       "ESPERANDO",
    "listening":  "ESCUCHANDO",
    "processing": "PROCESANDO",
    "speaking":   "HABLANDO",
    "error":      "ERROR",
}

# ── Tipografía ──────────────────────────────────────────────────────────────
# Candidatos en orden de preferencia. Se resuelven en runtime contra las
# fuentes realmente instaladas (varía entre Linux/Windows/Mac), con
# fallback a las fuentes genéricas de Tk si ninguna está disponible.
_DISPLAY_CANDIDATES = [
    "Bahnschrift", "Haettenschweiler", "Impact", "Nimbus Sans Narrow",
    "Arial Narrow", "Noto Sans", "DejaVu Sans",
]
_MONO_CANDIDATES = [
    "JetBrainsMono Nerd Font Mono", "JetBrainsMono Nerd Font",
    "JetBrains Mono", "Consolas", "Menlo",
    "DejaVu Sans Mono", "Liberation Mono", "Courier New",
]

_resolved: dict[str, str] = {}


def _resolve(candidates: list[str], fallback: str) -> str:
    cache_key = candidates[0]
    if cache_key in _resolved:
        return _resolved[cache_key]
    try:
        available = {f.lower() for f in tkfont.families()}
    except Exception:
        _resolved[cache_key] = fallback
        return fallback
    for name in candidates:
        if name.lower() in available:
            _resolved[cache_key] = name
            return name
    _resolved[cache_key] = fallback
    return fallback


def display_font(size: int, weight: str = "bold") -> tuple:
    """Fuente condensada/bold para titulares y CTAs. Requiere un root Tk ya creado."""
    family = _resolve(_DISPLAY_CANDIDATES, "TkDefaultFont")
    return (family, size, weight)


def mono_font(size: int, weight: str = "normal") -> tuple:
    """Fuente monoespaciada para cuerpo de texto. Requiere un root Tk ya creado."""
    family = _resolve(_MONO_CANDIDATES, "TkFixedFont")
    return (family, size, weight)


def bind_hover(widget, normal: dict, hover: dict) -> None:
    """Aplica `normal` ahora y alterna a `hover` en <Enter>/<Leave>. Sirve para
    dar feedback de hover consistente incluso donde activebackground de Tk
    no alcanza (fondo Y borde a la vez, por ejemplo)."""
    widget.configure(**normal)
    widget.bind("<Enter>", lambda e: widget.configure(**hover))
    widget.bind("<Leave>", lambda e: widget.configure(**normal))
