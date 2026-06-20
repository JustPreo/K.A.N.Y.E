import os
import re
import shlex
from pathlib import Path

from rapidfuzz import process, fuzz

from core.platform_utils import is_windows, is_linux


# --- Windows ---

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
    / "Microsoft"
    / "Windows"
    / "Start Menu"
    / "Programs",
    Path(os.environ.get("APPDATA", ""))
    / "Microsoft"
    / "Windows"
    / "Start Menu"
    / "Programs",
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
    apps = []

    for app in BUILTIN_WINDOWS_APPS:
        apps.append({**app, "type": "builtin"})

    for start_path in WINDOWS_START_MENU:
        if not start_path.exists():
            continue

        for file in start_path.rglob("*.lnk"):
            app_name = file.stem
            target = _get_shortcut_target(file)

            if target:
                apps.append(
                    {
                        "name": app_name,
                        "aliases": [app_name.lower()],
                        "path": target,
                        "shortcut": str(file),
                        "type": "shortcut",
                    }
                )

    return apps


# --- Linux ---

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
    {
        "name": "Navegador",
        "aliases": ["navegador", "browser", "firefox", "chrome", "chromium"],
        "command": "xdg-open http://",
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
        cmd = parts[0]
        # Flatpak: keep full command
        if "flatpak" in cmd:
            return exec_str.strip()
        return cmd
    except Exception:
        return exec_str.split()[0] if exec_str.split() else ""


def _parse_desktop_file(path: Path) -> dict | None:
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        in_desktop_entry = False
        name: str | None = None
        exec_cmd: str | None = None
        no_display = False
        hidden = False
        generic_name: str | None = None

        for line in content.splitlines():
            line = line.strip()
            if line == "[Desktop Entry]":
                in_desktop_entry = True
                continue
            if line.startswith("[") and line != "[Desktop Entry]":
                in_desktop_entry = False
                continue

            if not in_desktop_entry:
                continue

            if line.startswith("Name=") and name is None:
                name = line.split("=", 1)[1].strip()
            elif line.startswith("GenericName=") and generic_name is None:
                generic_name = line.split("=", 1)[1].strip()
            elif line.startswith("Exec=") and exec_cmd is None:
                raw_exec = line.split("=", 1)[1].strip()
                exec_cmd = _clean_exec(raw_exec)
            elif line.startswith("NoDisplay="):
                no_display = line.split("=", 1)[1].strip().lower() == "true"
            elif line.startswith("Hidden="):
                hidden = line.split("=", 1)[1].strip().lower() == "true"

        if not name or not exec_cmd or no_display or hidden:
            return None

        aliases = list(
            {
                name.lower(),
                path.stem.lower(),
                *([] if generic_name is None else [generic_name.lower()]),
            }
        )

        return {
            "name": name,
            "aliases": aliases,
            "command": exec_cmd,
            "type": "desktop",
        }
    except Exception:
        return None


def _scan_linux_apps() -> list[dict]:
    apps = []

    for app in BUILTIN_LINUX_APPS:
        apps.append({**app, "type": "builtin"})

    seen_names: set[str] = set()

    for desktop_dir in LINUX_DESKTOP_DIRS:
        if not desktop_dir.exists():
            continue

        for file in desktop_dir.glob("*.desktop"):
            info = _parse_desktop_file(file)
            if info and info["name"] not in seen_names:
                seen_names.add(info["name"])
                apps.append(info)

    return apps


# --- Unified ---

def scan_apps() -> list[dict]:
    if is_windows():
        return _scan_windows_apps()
    return _scan_linux_apps()


def find_best_app_match(query: str) -> dict | None:
    query = query.lower().strip()
    apps = scan_apps()

    if not apps:
        return None

    searchable_names: list[str] = []
    app_lookup: list[dict] = []

    for app in apps:
        aliases = app.get("aliases", [app["name"]])
        for alias in aliases:
            searchable_names.append(alias.lower())
            app_lookup.append(app)

    match = process.extractOne(query, searchable_names, scorer=fuzz.WRatio)

    if not match:
        return None

    matched_name, score, index = match

    if score < 65:
        return None

    selected_app = app_lookup[index]
    selected_app["score"] = score
    selected_app["matched_name"] = matched_name

    return selected_app
