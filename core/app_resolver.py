import os
from pathlib import Path
from rapidfuzz import process, fuzz
import win32com.client


START_MENU_PATHS = [
    Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
    Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
]


def get_shortcut_target(shortcut_path: Path) -> str | None:
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(shortcut_path))
        target = shortcut.Targetpath

        if target and os.path.exists(target):
            return target

        return None
    except Exception:
        return None


def scan_windows_apps() -> list[dict]:
    apps = []

    for start_path in START_MENU_PATHS:
        if not start_path.exists():
            continue

        for file in start_path.rglob("*.lnk"):
            app_name = file.stem
            target = get_shortcut_target(file)

            if target:
                apps.append({
                    "name": app_name,
                    "path": target,
                    "shortcut": str(file)
                })

    return apps


def find_best_app_match(query: str) -> dict | None:
    apps = scan_windows_apps()

    if not apps:
        return None

    app_names = [app["name"] for app in apps]

    match = process.extractOne(
        query,
        app_names,
        scorer=fuzz.WRatio
    )

    if not match:
        return None

    matched_name, score, index = match

    if score < 55:
        return None

    selected_app = apps[index]
    selected_app["score"] = score

    return selected_app