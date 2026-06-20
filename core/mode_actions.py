import json
import re
import webbrowser
from pathlib import Path

from core.app_resolver import find_best_app_match
from core.system_actions import open_application
from core.folder_actions import open_folder
from core.process_actions import close_all_desktop_apps
from core.config_loader import PROJECT_ROOT

MODES_FILE = PROJECT_ROOT / "config" / "modes.json"


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
    close_before_text = input("¿Cerrar apps antes de activar este modo? sí/no: ").lower().strip()
    close_before = close_before_text in ["si", "sí", "s"]
    message_text = input("Mensaje final del modo. Si lo dejas vacío, usaré uno automático.\nMensaje: ")

    apps = split_user_list(apps_text)
    urls = split_user_list(urls_text)
    folders = split_user_list(folders_text)

    if not message_text.strip():
        message_text = f"Modo {mode_name} activado."

    new_mode = {
        "close_before": close_before,
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

def edit_mode_interactive(mode_name: str) -> bool:
    mode_name = mode_name.lower().strip()

    if not mode_name:
        print("K.A.N.Y.E.: Necesito el nombre del modo que querés editar.")
        return False

    modes = load_modes()

    if mode_name not in modes:
        print(f"K.A.N.Y.E.: No existe el modo '{mode_name}'.")
        return False

    mode = modes[mode_name]

    print(f"\nK.A.N.Y.E.: Editando modo '{mode_name}'.")
    print("Contenido actual:")
    print(json.dumps(mode, indent=4, ensure_ascii=False))

    print("\n¿Qué querés editar?")
    print("1. Apps")
    print("2. URLs")
    print("3. Carpetas")
    print("4. Mensaje")
    print("5. Todo")
    print("6. Cerrar apps antes")
    print("7. Cancelar")
    option = input("Opción: ").strip()

    if option == "1":
        apps_text = input("Nuevas apps separadas por coma. Ej: steam, discord, chrome\nApps: ")
        mode["apps"] = split_user_list(apps_text)

    elif option == "2":
        urls_text = input("Nuevas URLs separadas por coma. Si no hay, escribe no.\nURLs: ")
        mode["urls"] = split_user_list(urls_text)

    elif option == "3":
        folders_text = input("Nuevas carpetas separadas por coma. Ej: descargas, documentos. Si no hay, escribe no.\nCarpetas: ")
        mode["folders"] = split_user_list(folders_text)

    elif option == "4":
        message_text = input("Nuevo mensaje final:\nMensaje: ").strip()

        if message_text:
            mode["message"] = message_text
        else:
            mode["message"] = f"Modo {mode_name} activado."

    elif option == "5":
        apps_text = input("Nuevas apps separadas por coma. Ej: steam, discord, chrome\nApps: ")
        urls_text = input("Nuevas URLs separadas por coma. Si no hay, escribe no.\nURLs: ")
        folders_text = input("Nuevas carpetas separadas por coma. Ej: descargas, documentos. Si no hay, escribe no.\nCarpetas: ")
        message_text = input("Nuevo mensaje final. Si lo dejas vacío, usaré uno automático.\nMensaje: ")

        mode["apps"] = split_user_list(apps_text)
        mode["urls"] = split_user_list(urls_text)
        mode["folders"] = split_user_list(folders_text)

        if message_text.strip():
            mode["message"] = message_text.strip()
        else:
            mode["message"] = f"Modo {mode_name} activado."

    elif option == "6":
        close_before_text = input("¿Cerrar apps antes de activar este modo? sí/no: ").lower().strip()
        mode["close_before"] = close_before_text in ["si", "sí", "s"]

    elif option == "7":
        print("K.A.N.Y.E.: Edición cancelada.")
        return False

    else:
        print("K.A.N.Y.E.: Opción no válida.")
        return False

    print("\nK.A.N.Y.E.: Nuevo contenido:")
    print(json.dumps(mode, indent=4, ensure_ascii=False))

    confirm = input("\n¿Guardar cambios? sí/no: ").lower().strip()

    if confirm not in ["si", "sí", "s"]:
        print("K.A.N.Y.E.: Cambios cancelados.")
        return False

    modes[mode_name] = mode

    saved = save_modes(modes)

    if saved:
        print(f"K.A.N.Y.E.: Modo '{mode_name}' actualizado.")
        return True

    return False


_YOUTUBE_PATTERN = re.compile(
    r"(youtube\.com|youtu\.be|music\.youtube\.com)",
    re.IGNORECASE,
)


def _add_autoplay_param(url: str) -> str:
    """Agrega autoplay=1 a URLs de YouTube si no lo tienen ya."""
    if "autoplay=1" in url:
        return url
    sep = "&" if "?" in url else "?"
    return url + sep + "autoplay=1"


def _open_media_url(url: str) -> None:
    """Abre una URL multimedia en el browser. Agrega autoplay=1 para YouTube."""
    if _YOUTUBE_PATTERN.search(url):
        url = _add_autoplay_param(url)
    webbrowser.open(url)


def activate_mode(mode_name: str) -> bool:
    mode_name = mode_name.lower().strip()
    modes = load_modes()

    if mode_name not in modes:
        print(f"K.A.N.Y.E.: No existe el modo '{mode_name}'.")
        return False

    mode = modes[mode_name]

    apps        = mode.get("apps", [])
    urls        = mode.get("urls", [])
    folders     = mode.get("folders", [])
    message     = mode.get("message", f"Modo {mode_name} activado.")
    close_before = mode.get("close_before", False)
    focus_cfg   = mode.get("focus", {})

    if close_before:
        print("K.A.N.Y.E.: Cerrando aplicaciones antes de activar el modo...")
        close_all_desktop_apps()

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
        _open_media_url(url)

    for folder in folders:
        print(f"K.A.N.Y.E.: Abriendo carpeta: {folder}")
        open_folder(folder)

    # ── Modo focus ────────────────────────────────────────────────────────────
    if focus_cfg.get("enabled"):
        from core import focus_mode
        sites    = focus_cfg.get("blocked_sites", [])
        duration = focus_cfg.get("duration_minutes", 25)
        if sites:
            focus_mode.activate(sites, duration)
            print(
                f"K.A.N.Y.E.: Focus ON — {duration} min. "
                f"Sitios bloqueados: {', '.join(sites)}"
            )

    # Actualiza el modo en ambient
    try:
        from core import ambient
        ambient.set_mode(mode_name)
    except Exception:
        pass

    print(f"K.A.N.Y.E.: {message}")
    try:
        from core.text_to_speech import speak
        speak(message)
    except Exception as e:
        print(f"K.A.N.Y.E.: No pude hablar: {e}")

    return True