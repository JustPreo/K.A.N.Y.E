import os
import platform
import subprocess

import psutil
from rapidfuzz import process, fuzz

from core.platform_utils import is_windows

PROTECTED_WINDOWS = {
    "python.exe", "pythonw.exe", "powershell.exe",
    "windowsterminal.exe", "cmd.exe", "explorer.exe",
    "ollama.exe", "ollama app.exe",
}

PROTECTED_LINUX = {
    "python", "python3", "bash", "zsh", "fish", "sh",
    "gnome-shell", "plasmashell", "kwin_wayland", "kwin_x11",
    "sway", "hyprland", "i3", "openbox", "xfwm4",
    "xorg", "Xorg", "Xwayland",
    "ollama", "systemd", "init", "dbus-daemon",
}


def _get_protected() -> set[str]:
    return PROTECTED_WINDOWS if is_windows() else PROTECTED_LINUX


def _is_system_process(name: str, exe: str) -> bool:
    if is_windows():
        return "windows\\system32" in exe.lower()
    else:
        protected_paths = ("/usr/lib/systemd", "/lib/systemd", "/sbin/", "/usr/sbin/")
        return any(exe.startswith(p) for p in protected_paths)


def get_running_processes() -> list[dict]:
    processes = []

    for proc in psutil.process_iter(["pid", "name", "exe"]):
        try:
            name = proc.info.get("name")
            exe = proc.info.get("exe") or ""

            if not name:
                continue

            processes.append({"pid": proc.info["pid"], "name": name, "exe": exe})

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return processes


def close_application(query: str) -> bool:
    query = query.lower().strip()

    if not query:
        return False

    processes = get_running_processes()

    if not processes:
        return False

    process_names = [proc["name"].lower() for proc in processes]

    match = process.extractOne(query, process_names, scorer=fuzz.WRatio)

    if not match:
        print("K.A.N.Y.E.: No encontré un proceso parecido.")
        return False

    matched_name, score, index = match

    if score < 55:
        print(f"K.A.N.Y.E.: Coincidencia muy baja: {matched_name} | Score: {score}")
        return False

    target_name = processes[index]["name"]
    print(f"K.A.N.Y.E.: Proceso objetivo: {target_name} | Score: {score}")

    closed_any = False

    for proc in processes:
        if proc["name"].lower() == target_name.lower():
            try:
                process_obj = psutil.Process(proc["pid"])
                process_obj.terminate()
                closed_any = True
                print(f"K.A.N.Y.E.: Cerrando {proc['name']} | PID: {proc['pid']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied) as error:
                print(f"K.A.N.Y.E.: No pude cerrar {proc['name']}: {error}")

    return closed_any


PROTECTED_WINDOW_CLASSES = {
    "python", "python3", "tk", "kanye", "rofi", "wofi", "waybar", "eww",
    "hyprpaper", "swaybg", "swaylock", "swayidle",
    "ags", "anyrun", "avizo",
}

PROTECTED_WINDOW_TITLES = {
    "k.a.n.y.e", "kanye",
}


def _cmd(*args, **kwargs) -> "subprocess.CompletedProcess | None":
    """Ejecuta un comando y retorna el resultado, o None si falla."""
    try:
        return subprocess.run(list(args), capture_output=True, text=True, timeout=5, **kwargs)
    except Exception:
        return None


def _is_protected_window(cls: str, title: str) -> bool:
    cls = cls.lower()
    title = title.lower()
    if cls in PROTECTED_WINDOW_CLASSES:
        return True
    return any(k in title for k in PROTECTED_WINDOW_TITLES)


# ── Hyprland ──────────────────────────────────────────────────────────────────

def _close_all_hyprland() -> bool:
    import json

    r = _cmd("hyprctl", "clients", "-j")
    if not r or r.returncode != 0:
        return False

    try:
        clients = json.loads(r.stdout)
    except Exception:
        return False

    current_pid = os.getpid()
    closed_any = False
    for client in clients:
        address = client.get("address", "")
        cls = client.get("class") or ""
        title = client.get("title") or ""
        pid = client.get("pid", -1)
        if pid == current_pid:
            continue
        if _is_protected_window(cls, title):
            continue
        _cmd("hyprctl", "dispatch", "closewindow", f"address:{address}")
        print(f"K.A.N.Y.E.: Cerrando ventana [{cls}] {title}")
        closed_any = True

    return closed_any


# ── Sway ──────────────────────────────────────────────────────────────────────

def _close_all_sway() -> bool:
    import json

    r = _cmd("swaymsg", "-t", "get_tree")
    if not r or r.returncode != 0:
        return False

    try:
        tree = json.loads(r.stdout)
    except Exception:
        return False

    def collect_windows(node: dict) -> list[dict]:
        windows = []
        if node.get("type") in ("con", "floating_con") and node.get("app_id"):
            windows.append(node)
        for child in node.get("nodes", []) + node.get("floating_nodes", []):
            windows.extend(collect_windows(child))
        return windows

    closed_any = False
    for win in collect_windows(tree):
        cls = win.get("app_id") or win.get("window_properties", {}).get("class") or ""
        title = win.get("name") or ""
        if _is_protected_window(cls, title):
            continue
        con_id = win.get("id")
        _cmd("swaymsg", f"[con_id={con_id}]", "kill")
        print(f"K.A.N.Y.E.: Cerrando ventana [{cls}] {title}")
        closed_any = True

    return closed_any


# ── GNOME Wayland (gdbus) ────────────────────────────────────────────────────

def _close_all_gnome() -> bool:
    r = _cmd(
        "gdbus", "call", "--session",
        "--dest", "org.gnome.Shell",
        "--object-path", "/org/gnome/Shell",
        "--method", "org.gnome.Shell.Eval",
        "global.get_window_actors().map(a=>a.meta_window).filter(w=>w.get_window_type()===0)"
        ".forEach(w=>w.delete(global.get_current_time()))"
    )
    if r and r.returncode == 0:
        print("K.A.N.Y.E.: Ventanas GNOME cerradas.")
        return True
    return False


# ── KDE Wayland / Plasma (qdbus) ─────────────────────────────────────────────

def _close_all_kde() -> bool:
    r = _cmd(
        "qdbus", "org.kde.KWin", "/KWin",
        "org.kde.KWin.closeAllClients"
    )
    if r and r.returncode == 0:
        print("K.A.N.Y.E.: Ventanas KDE cerradas.")
        return True
    return False


# ── X11: wmctrl ───────────────────────────────────────────────────────────────

def _close_all_wmctrl() -> bool:
    r = _cmd("wmctrl", "-l")
    if not r or r.returncode != 0:
        return False

    closed_any = False
    for line in r.stdout.strip().splitlines():
        parts = line.split(None, 3)
        if len(parts) < 4:
            continue
        wid, title = parts[0], parts[3]
        if _is_protected_window("", title):
            continue
        _cmd("wmctrl", "-ic", wid)
        print(f"K.A.N.Y.E.: Cerrando ventana {title}")
        closed_any = True

    return closed_any


# ── X11: xdotool ─────────────────────────────────────────────────────────────

def _close_all_xdotool() -> bool:
    r = _cmd("xdotool", "search", "--onlyvisible", "--name", "")
    if not r or r.returncode != 0:
        return False

    closed_any = False
    for wid in r.stdout.strip().splitlines():
        wid = wid.strip()
        if not wid:
            continue
        name_r = _cmd("xdotool", "getwindowname", wid)
        title = name_r.stdout.strip() if name_r else ""
        if _is_protected_window("", title):
            continue
        _cmd("xdotool", "windowclose", wid)
        print(f"K.A.N.Y.E.: Cerrando ventana {title or wid}")
        closed_any = True

    return closed_any


# ── macOS (osascript) ─────────────────────────────────────────────────────────

def _close_all_macos() -> bool:
    script = """
tell application "System Events"
    set appList to name of every process whose background only is false
end tell
repeat with appName in appList
    if appName is not in {"Finder", "Python", "Terminal"} then
        try
            tell application appName to close every window
        end try
    end if
end repeat
"""
    r = _cmd("osascript", "-e", script)
    if r and r.returncode == 0:
        print("K.A.N.Y.E.: Ventanas macOS cerradas.")
        return True
    return False


# ── Windows (WM_CLOSE via ctypes) ────────────────────────────────────────────

def _close_all_windows() -> bool:
    import ctypes

    user32 = ctypes.windll.user32
    current_pid = os.getpid()
    protected = {p.lower() for p in PROTECTED_WINDOWS}
    pids_closed: set[int] = set()
    closed_any = False

    def callback(hwnd, _):
        nonlocal closed_any
        if not user32.IsWindowVisible(hwnd):
            return True
        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        pid_val = pid.value
        if pid_val in (current_pid, *pids_closed):
            return True
        try:
            name = (psutil.Process(pid_val).name() or "").lower()
            if name in protected:
                return True
        except psutil.NoSuchProcess:
            return True
        user32.SendMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE
        pids_closed.add(pid_val)
        print(f"K.A.N.Y.E.: Cerrando ventana PID {pid_val}")
        closed_any = True
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    user32.EnumWindows(WNDENUMPROC(callback), 0)
    return closed_any


# ── Dispatcher principal ──────────────────────────────────────────────────────

def close_all_desktop_apps() -> bool:
    system = platform.system()

    if system == "Windows":
        return _close_all_windows()

    if system == "Darwin":
        return _close_all_macos()

    # Linux — detectar entorno por variables de entorno
    desktop = os.environ.get("XDG_SESSION_DESKTOP", "").lower()
    wm = os.environ.get("WAYLAND_DISPLAY", "")

    if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        if _close_all_hyprland():
            return True

    if os.environ.get("SWAYSOCK"):
        if _close_all_sway():
            return True

    if "gnome" in desktop:
        if _close_all_gnome():
            return True

    if "kde" in desktop or "plasma" in desktop:
        if _close_all_kde():
            return True

    # Fallback X11
    if _close_all_wmctrl():
        return True
    return _close_all_xdotool()
