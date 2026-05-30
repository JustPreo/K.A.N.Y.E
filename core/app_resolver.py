import os
from pathlib import Path
from rapidfuzz import process, fuzz
import win32com.client


START_MENU_PATHS = [
    Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
    Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
]


BUILTIN_WINDOWS_APPS = [
    {
        "name": "Bloc de notas",
        "aliases": ["notas", "nota", "bloc de notas", "notepad", "editor de texto"],
        "command": "notepad.exe"
    },
    {
        "name": "Calculadora",
        "aliases": ["calculadora", "calculator", "calc"],
        "command": "calc.exe"
    },
    {
        "name": "Paint",
        "aliases": ["paint", "dibujo", "mspaint"],
        "command": "mspaint.exe"
    },
    {
        "name": "Explorador de archivos",
        "aliases": ["archivos", "explorador", "explorador de archivos", "carpetas"],
        "command": "explorer.exe"
    },
    {
        "name": "Terminal",
        "aliases": ["terminal", "consola", "powershell", "cmd"],
        "command": "wt.exe"
    },
]


def get_shortcut_target(shortcut_path: Path) -> str | None:
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(shortcut_path))
        target = shortcut.Targetpath

        if not target:
            return None

        target = target.strip()

        # Solo aceptamos ejecutables reales.
        if os.path.exists(target) and target.lower().endswith(".exe"):
            return target

        return None
    except Exception:
        return None


def scan_windows_apps() -> list[dict]:
    apps = []

    # Primero agregamos apps básicas de Windows.
    for app in BUILTIN_WINDOWS_APPS:
        apps.append({
            "name": app["name"],
            "aliases": app["aliases"],
            "command": app["command"],
            "type": "builtin"
        })

    # Luego escaneamos apps del menú inicio.
    for start_path in START_MENU_PATHS:
        if not start_path.exists():
            continue

        for file in start_path.rglob("*.lnk"):
            app_name = file.stem
            target = get_shortcut_target(file)

            if target:
                apps.append({
                    "name": app_name,
                    "aliases": [app_name],
                    "path": target,
                    "shortcut": str(file),
                    "type": "shortcut"
                })

    return apps


def find_best_app_match(query: str) -> dict | None:
    query = query.lower().strip()
    apps = scan_windows_apps()

    if not apps:
        return None

    searchable_names = []
    app_lookup = []

    for app in apps:
        aliases = app.get("aliases", [app["name"]])

        for alias in aliases:
            searchable_names.append(alias.lower())
            app_lookup.append(app)

    match = process.extractOne(
        query,
        searchable_names,
        scorer=fuzz.WRatio
    )

    if not match:
        return None

    matched_name, score, index = match

    if score < 65:
        return None

    selected_app = app_lookup[index]
    selected_app["score"] = score
    selected_app["matched_name"] = matched_name

    return selected_app