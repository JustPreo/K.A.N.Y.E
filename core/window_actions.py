"""
Control de la ventana activa (minimizar / maximizar-restaurar). Sigue el
mismo patrón de detección de compositor/SO que close_all_desktop_apps() en
process_actions.py: un dispatcher por plataforma, con fallback a wmctrl/
xdotool en X11 puro.

No hay forma universal de "traer de vuelta" una ventana minimizada sin
trackear su address/id — igual que un usuario humano, se recupera con
alt-tab o el dock, no con otra tool.
"""
import os
import platform
import subprocess


def _cmd(*args, **kwargs) -> "subprocess.CompletedProcess | None":
    try:
        return subprocess.run(list(args), capture_output=True, text=True, timeout=5, **kwargs)
    except Exception:
        return None


# ── Hyprland ──────────────────────────────────────────────────────────────────

def _minimize_hyprland() -> bool:
    r = _cmd("hyprctl", "dispatch", "movetoworkspacesilent", "special:minimized")
    return bool(r and r.returncode == 0)


def _toggle_maximize_hyprland() -> bool:
    r = _cmd("hyprctl", "dispatch", "fullscreen", "1")
    return bool(r and r.returncode == 0)


# ── Sway ──────────────────────────────────────────────────────────────────────

def _minimize_sway() -> bool:
    r = _cmd("swaymsg", "move", "scratchpad")
    return bool(r and r.returncode == 0)


def _toggle_maximize_sway() -> bool:
    r = _cmd("swaymsg", "fullscreen", "toggle")
    return bool(r and r.returncode == 0)


# ── GNOME Wayland (gdbus) ────────────────────────────────────────────────────

def _minimize_gnome() -> bool:
    r = _cmd(
        "gdbus", "call", "--session", "--dest", "org.gnome.Shell",
        "--object-path", "/org/gnome/Shell", "--method", "org.gnome.Shell.Eval",
        "global.display.focus_window && global.display.focus_window.minimize()",
    )
    return bool(r and r.returncode == 0)


def _toggle_maximize_gnome() -> bool:
    r = _cmd(
        "gdbus", "call", "--session", "--dest", "org.gnome.Shell",
        "--object-path", "/org/gnome/Shell", "--method", "org.gnome.Shell.Eval",
        "(w=>w&&(w.get_maximized()?w.unmaximize(3):w.maximize(3)))(global.display.focus_window)",
    )
    return bool(r and r.returncode == 0)


# ── KDE Wayland / Plasma (kglobalaccel) ──────────────────────────────────────

def _minimize_kde() -> bool:
    r = _cmd(
        "qdbus", "org.kde.kglobalaccel", "/component/kwin",
        "org.kde.kglobalaccel.Component.invokeShortcut", "Window Minimize",
    )
    return bool(r and r.returncode == 0)


def _toggle_maximize_kde() -> bool:
    r = _cmd(
        "qdbus", "org.kde.kglobalaccel", "/component/kwin",
        "org.kde.kglobalaccel.Component.invokeShortcut", "Window Maximize",
    )
    return bool(r and r.returncode == 0)


# ── X11: wmctrl ───────────────────────────────────────────────────────────────

def _minimize_wmctrl() -> bool:
    r = _cmd("wmctrl", "-r", ":ACTIVE:", "-b", "add,hidden")
    return bool(r and r.returncode == 0)


def _toggle_maximize_wmctrl() -> bool:
    r = _cmd("wmctrl", "-r", ":ACTIVE:", "-b", "toggle,maximized_vert,maximized_horz")
    return bool(r and r.returncode == 0)


# ── X11: xdotool (último fallback, solo minimizar) ───────────────────────────

def _minimize_xdotool() -> bool:
    r = _cmd("xdotool", "getactivewindow", "windowminimize")
    return bool(r and r.returncode == 0)


# ── macOS (osascript) ─────────────────────────────────────────────────────────

def _minimize_macos() -> bool:
    r = _cmd("osascript", "-e", 'tell application "System Events" to set visible of first process whose frontmost is true to false')
    return bool(r and r.returncode == 0)


def _toggle_maximize_macos() -> bool:
    r = _cmd("osascript", "-e", (
        'tell application "System Events" to tell (first process whose frontmost is true) '
        'to set zoomed of front window to not (zoomed of front window)'
    ))
    return bool(r and r.returncode == 0)


# ── Windows (ctypes) ──────────────────────────────────────────────────────────

def _minimize_windows() -> bool:
    import ctypes
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    if not hwnd:
        return False
    ctypes.windll.user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE
    return True


def _toggle_maximize_windows() -> bool:
    import ctypes
    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return False
    is_zoomed = user32.IsZoomed(hwnd)
    user32.ShowWindow(hwnd, 9 if is_zoomed else 3)  # SW_RESTORE : SW_MAXIMIZE
    return True


# ── Dispatchers principales ──────────────────────────────────────────────────

def minimize_active() -> bool:
    system = platform.system()

    if system == "Windows":
        return _minimize_windows()
    if system == "Darwin":
        return _minimize_macos()

    if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE") and _minimize_hyprland():
        return True
    if os.environ.get("SWAYSOCK") and _minimize_sway():
        return True

    desktop = os.environ.get("XDG_SESSION_DESKTOP", "").lower()
    if "gnome" in desktop and _minimize_gnome():
        return True
    if ("kde" in desktop or "plasma" in desktop) and _minimize_kde():
        return True

    if _minimize_wmctrl():
        return True
    return _minimize_xdotool()


def toggle_maximize_active() -> bool:
    system = platform.system()

    if system == "Windows":
        return _toggle_maximize_windows()
    if system == "Darwin":
        return _toggle_maximize_macos()

    if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE") and _toggle_maximize_hyprland():
        return True
    if os.environ.get("SWAYSOCK") and _toggle_maximize_sway():
        return True

    desktop = os.environ.get("XDG_SESSION_DESKTOP", "").lower()
    if "gnome" in desktop and _toggle_maximize_gnome():
        return True
    if ("kde" in desktop or "plasma" in desktop) and _toggle_maximize_kde():
        return True

    return _toggle_maximize_wmctrl()
