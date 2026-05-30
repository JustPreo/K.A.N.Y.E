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


def save_modes(modes: dict) -> bool:
    try:
        MODES_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(MODES_FILE, "w", encoding="utf-8") as file:
            json.dump(modes, file, indent=4, ensure_ascii=False)

        return True
    except Exception as error:
        print(f"Error guardando modes.json: {error}")
        return False


def split_user_list(text: str) -> list[str]:
    """
    Convierte:
    'steam, discord, chrome'
    en:
    ['steam', 'discord', 'chrome']
    """
    text = text.strip()

    if not text or text.lower() in ["no", "ninguna", "ninguno", "nada"]:
        return []

    items = text.split(",")

    clean_items = []

    for item in items:
        item = item.strip()

        if item:
            clean_items.append(item)

    return clean_items


def create_mode_interactive(mode_name: str) -> bool:
    mode_name = mode_name.lower().strip()

    if not mode_name:
        print("K.A.N.Y.E.: Necesito un nombre para el modo.")
        return False

    modes = load_modes()

    if mode_name in modes:
        print(f"K.A.N.Y.E.: El modo '{mode_name}' ya existe.")
        overwrite = input("¿Querés reemplazarlo? sí/no: ").lower().strip()

        if overwrite not in ["si", "sí", "s"]:
            print("K.A.N.Y.E.: No hice cambios.")
            return False

    print(f"\nK.A.N.Y.E.: Creando modo '{mode_name}'.")

    apps_text = input("Apps a abrir, separadas por coma. Ej: steam, discord, chrome\nApps: ")
    urls_text = input("URLs a abrir, separadas por coma. Si no hay, escribe no.\nURLs: ")
    folders_text = input("Carpetas a abrir, separadas por coma. Ej: descargas, documentos. Si no hay, escribe no.\nCarpetas: ")
    message_text = input("Mensaje final del modo. Si lo dejas vacío, usaré uno automático.\nMensaje: ")

    apps = split_user_list(apps_text)
    urls = split_user_list(urls_text)
    folders = split_user_list(folders_text)

    if not message_text.strip():
        message_text = f"Modo {mode_name} activado."

    new_mode = {
        "apps": apps,
        "urls": urls,
        "folders": folders,
        "message": message_text.strip()
    }

    print("\nK.A.N.Y.E.: Resumen del modo:")
    print(json.dumps(new_mode, indent=4, ensure_ascii=False))

    confirm = input("\n¿Guardar este modo? sí/no: ").lower().strip()

    if confirm not in ["si", "sí", "s"]:
        print("K.A.N.Y.E.: Modo cancelado.")
        return False

    modes[mode_name] = new_mode

    saved = save_modes(modes)

    if saved:
        print(f"K.A.N.Y.E.: Modo '{mode_name}' guardado.")
        return True

    return False


def list_modes() -> None:
    modes = load_modes()

    if not modes:
        print("K.A.N.Y.E.: No hay modos guardados.")
        return

    print("K.A.N.Y.E.: Modos disponibles:")

    for mode_name in modes.keys():
        print(f"- {mode_name}")

def delete_mode(mode_name: str) -> bool:
    mode_name = mode_name.lower().strip()

    if not mode_name:
        print("K.A.N.Y.E.: Necesito el nombre del modo que querés eliminar.")
        return False

    modes = load_modes()

    if mode_name not in modes:
        print(f"K.A.N.Y.E.: No existe el modo '{mode_name}'.")
        return False

    print(f"K.A.N.Y.E.: Estás a punto de eliminar el modo '{mode_name}'.")

    confirm = input("¿Seguro que querés eliminarlo? sí/no: ").lower().strip()

    if confirm not in ["si", "sí", "s"]:
        print("K.A.N.Y.E.: Eliminación cancelada.")
        return False

    del modes[mode_name]

    saved = save_modes(modes)

    if saved:
        print(f"K.A.N.Y.E.: Modo '{mode_name}' eliminado.")
        return True

    return False

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