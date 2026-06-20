import os
import re
import shlex
from pathlib import Path

from rapidfuzz import process, fuzz

from core.platform_utils import is_windows, is_linux


# ─── Windows ──────────────────────────────────────────────────────────────────

BUILTIN_WINDOWS_APPS = [
    {
        "name": "Bloc de notas",
        "aliases": ["notas", "nota", "bloc de notas", "notepad", "editor de texto"],
        "command": "notepad.exe",
    },
    {
        "name": "Calculadora",
        "aliases": ["calculadora", "calculator", "calc"],
        "command": "calc.exe",
    },
    {
        "name": "Paint",
        "aliases": ["paint", "dibujo", "mspaint"],
        "command": "mspaint.exe",
    },
    {
        "name": "Explorador de archivos",
        "aliases": ["archivos", "explorador", "explorador de archivos", "carpetas"],
        "command": "explorer.exe",
    },
    {
        "name": "Terminal",
        "aliases": ["terminal", "consola", "powershell", "cmd"],
        "command": "wt.exe",
    },
]

WINDOWS_START_MENU = [
    Path(os.environ.get("PROGRAMDATA", ""))
    / "Microsoft" / "Windows" / "Start Menu" / "Programs",
    Path(os.environ.get("APPDATA", ""))
    / "Microsoft" / "Windows" / "Start Menu" / "Programs",
]


def _get_shortcut_target(shortcut_path: Path) -> str | None:
    try:
        import win32com.client

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(shortcut_path))
        target = shortcut.Targetpath

        if not target:
            return None

        target = target.strip()
        if os.path.exists(target) and target.lower().endswith(".exe"):
            return target
        return None
    except Exception:
        return None


def _scan_windows_apps() -> list[dict]:
    apps = [{**a, "type": "builtin"} for a in BUILTIN_WINDOWS_APPS]

    for start_path in WINDOWS_START_MENU:
        if not start_path.exists():
            continue
        for file in start_path.rglob("*.lnk"):
            target = _get_shortcut_target(file)
            if target:
                apps.append({
                    "name": file.stem,
                    "aliases": [file.stem.lower()],
                    "path": target,
                    "shortcut": str(file),
                    "type": "shortcut",
                })

    return apps


# ─── Linux ────────────────────────────────────────────────────────────────────

BUILTIN_LINUX_APPS = [
    {
        "name": "Terminal",
        "aliases": ["terminal", "consola", "bash", "zsh"],
        "command": "x-terminal-emulator",
    },
    {
        "name": "Calculadora",
        "aliases": ["calculadora", "calculator", "calc"],
        "command": "gnome-calculator",
    },
    {
        "name": "Explorador de archivos",
        "aliases": ["archivos", "explorador", "files", "carpetas", "nautilus"],
        "command": "nautilus",
    },
    {
        "name": "Editor de texto",
        "aliases": ["notas", "nota", "editor", "gedit", "texto"],
        "command": "gedit",
    },
]

LINUX_DESKTOP_DIRS = [
    Path("/usr/share/applications"),
    Path.home() / ".local/share/applications",
    Path("/var/lib/flatpak/exports/share/applications"),
    Path.home() / ".local/share/flatpak/exports/share/applications",
]


def _clean_exec(exec_str: str) -> str:
    exec_str = re.sub(r"%[fFuUdDnNickvmBb]", "", exec_str).strip()
    try:
        parts = shlex.split(exec_str)
        if not parts:
            return ""
        return exec_str.strip() if "flatpak" in parts[0] else parts[0]
    except Exception:
        return exec_str.split()[0] if exec_str.split() else ""


def _parse_desktop_file(path: Path) -> dict | None:
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        in_entry = False
        name = generic_name = exec_cmd = None
        no_display = hidden = False

        for line in content.splitlines():
            line = line.strip()
            if line == "[Desktop Entry]":
                in_entry = True
                continue
            if line.startswith("[") and line != "[Desktop Entry]":
                in_entry = False
                continue
            if not in_entry:
                continue

            if line.startswith("Name=") and name is None:
                name = line.split("=", 1)[1].strip()
            elif line.startswith("GenericName=") and generic_name is None:
                generic_name = line.split("=", 1)[1].strip()
            elif line.startswith("Exec=") and exec_cmd is None:
                exec_cmd = _clean_exec(line.split("=", 1)[1].strip())
            elif line.startswith("NoDisplay="):
                no_display = line.split("=", 1)[1].strip().lower() == "true"
            elif line.startswith("Hidden="):
                hidden = line.split("=", 1)[1].strip().lower() == "true"

        if not name or not exec_cmd or no_display or hidden:
            return None

        aliases = list({
            name.lower(),
            path.stem.lower(),
            *([generic_name.lower()] if generic_name else []),
        })

        return {"name": name, "aliases": aliases, "command": exec_cmd, "type": "desktop"}
    except Exception:
        return None


def _scan_linux_apps() -> list[dict]:
    apps = [{**a, "type": "builtin"} for a in BUILTIN_LINUX_APPS]
    seen: set[str] = set()

    for desktop_dir in LINUX_DESKTOP_DIRS:
        if not desktop_dir.exists():
            continue
        for file in desktop_dir.glob("*.desktop"):
            info = _parse_desktop_file(file)
            if info and info["name"] not in seen:
                seen.add(info["name"])
                apps.append(info)

    return apps


# ─── Cache ────────────────────────────────────────────────────────────────────

_apps_cache: list[dict] | None = None


def scan_apps(force_refresh: bool = False) -> list[dict]:
    global _apps_cache
    if _apps_cache is None or force_refresh:
        _apps_cache = _scan_windows_apps() if is_windows() else _scan_linux_apps()
        print(f"K.A.N.Y.E.: {len(_apps_cache)} apps indexadas.")
    return _apps_cache


# ─── Búsqueda ─────────────────────────────────────────────────────────────────

def find_best_app_match(query: str) -> dict | None:
    query = query.lower().strip()
    apps = scan_apps()

    if not apps:
        return None

    searchable: list[str] = []
    lookup: list[dict] = []

    for app in apps:
        for alias in app.get("aliases", [app["name"]]):
            searchable.append(alias.lower())
            lookup.append(app)

    match = process.extractOne(query, searchable, scorer=fuzz.WRatio)
    if not match:
        return None

    matched_name, score, index = match
    if score < 65:
        return None

    selected = lookup[index]
    selected["score"] = score
    selected["matched_name"] = matched_name
    return selected
