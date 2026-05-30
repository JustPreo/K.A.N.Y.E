import json
import webbrowser
from pathlib import Path

from core.app_resolver import find_best_app_match
from core.system_actions import open_application
from core.folder_actions import open_folder


MODES_FILE = Path("config") / "modes.json"


def load_modes() -> dict:
    if not MODES_FILE.exists():
        return {}

    try:
        with open(MODES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as error:
        print(f"Error leyendo modes.json: {error}")
        return {}


def activate_mode(mode_name: str) -> bool:
    mode_name = mode_name.lower().strip()
    modes = load_modes()

    if mode_name not in modes:
        print(f"K.A.N.Y.E.: No existe el modo '{mode_name}'.")
        return False

    mode = modes[mode_name]

    apps = mode.get("apps", [])
    urls = mode.get("urls", [])
    folders = mode.get("folders", [])
    message = mode.get("message", f"Modo {mode_name} activado.")

    print(f"K.A.N.Y.E.: Activando modo {mode_name}...")

    for app_query in apps:
        app = find_best_app_match(app_query)

        if app:
            print(f"K.A.N.Y.E.: Abriendo {app['name']}")
            open_application(app)
        else:
            print(f"K.A.N.Y.E.: No encontré la app: {app_query}")

    for url in urls:
        print(f"K.A.N.Y.E.: Abriendo URL: {url}")
        webbrowser.open(url)

    for folder in folders:
        print(f"K.A.N.Y.E.: Abriendo carpeta: {folder}")
        open_folder(folder)

    print(f"K.A.N.Y.E.: {message}")
    return True