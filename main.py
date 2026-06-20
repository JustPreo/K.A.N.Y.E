from core.intent_router import detect_intent
from core.app_resolver import find_best_app_match
from core.system_actions import open_application
from core.web_search import search_google
from core.folder_actions import open_folder
from core.mode_actions import (
    activate_mode,
    create_mode_interactive,
    list_modes,
    delete_mode,
    edit_mode_interactive,
)
from core.text_to_speech import speak
from core.local_llm import ask_llm
from core.text_normalizer import normalize_text
from core.hotkey_listener import wait_for_hotkey
from core.speech_to_text import listen_once
from core.llm_intent import classify_with_llm
from core.file_actions import read_file, search_in_file, backup_file, replace_in_file
from core.music_actions import play_on_youtube_music
from core.media_actions import (
    media_play_pause,
    media_next,
    media_previous,
    volume_up,
    volume_down,
    volume_mute,
)
from core.process_actions import close_application
from core.site_actions import open_site
from core.responses import response
from core.config_loader import get_config


LAST_INTERACTION = {"type": None}


def set_last_interaction(interaction_type: str) -> None:
    LAST_INTERACTION["type"] = interaction_type


def say(message: str) -> None:
    print(f"K.A.N.Y.E.: {message}")
    speak(message, use_cache=True)


def is_clear_system_command(command: str) -> bool:
    text = command.lower().strip()
    command_starters = [
        "abre sitio", "abrir sitio", "abre página", "abre pagina",
        "abrir página", "abrir pagina",
        "cierra", "cerrar", "cerrá", "termina", "terminar", "mata",
        "cerrar programa", "cierra programa",
        "pon", "pone", "reproduce", "toca", "pon música", "poner música",
        "busca música", "busca cancion", "busca canción",
        "abre", "abrí", "abrir", "ejecuta", "lanza",
        "busca", "buscar", "googlea", "investiga",
        "activa modo", "activar modo", "modo",
        "crea modo", "crear modo", "nuevo modo", "agrega modo", "agregar modo",
        "edita modo", "editar modo", "modifica modo", "modificar modo",
        "cambia modo", "cambiar modo",
        "elimina modo", "eliminar modo", "borra modo", "borrar modo",
        "quita modo", "quitar modo",
        "modos", "lista modos", "ver modos", "mostrar modos",
        "salir", "cerrar", "exit", "quit",
    ]
    return any(text.startswith(s) for s in command_starters)


def handle_chat(query: str) -> bool:
    print(f"K.A.N.Y.E.: Conversando: {query}")
    answer = ask_llm(query)
    print(f"K.A.N.Y.E.: {answer}\n")
    speak(answer, use_cache=False)
    set_last_interaction("chat")
    return True


def handle_media_control(action: str) -> bool:
    handlers = {
        "play_pause": (media_play_pause, "Listo.", "No pude pausar o reanudar."),
        "next": (media_next, "Siguiente canción.", "No pude pasar la canción."),
        "previous": (media_previous, "Canción anterior.", "No pude regresar la canción."),
        "volume_up": (volume_up, "Subiendo volumen.", "No pude subir el volumen."),
        "volume_down": (volume_down, "Bajando volumen.", "No pude bajar el volumen."),
        "mute": (volume_mute, "Silencio.", "No pude silenciar."),
    }

    if action not in handlers:
        say("No entendí el control multimedia.")
        print()
        set_last_interaction("command")
        return True

    fn, ok_msg, fail_msg = handlers[action]
    say(ok_msg if fn() else fail_msg)
    print()
    set_last_interaction("command")
    return True


def _read_file_command(raw_query: str, workspace: str) -> bool:
    file_path = raw_query.strip()
    content = read_file(file_path, workspace)

    if content is None:
        say("No pude leer el archivo.")
        return True

    print("\n--- CONTENIDO DEL ARCHIVO ---")
    print(content[:1200])
    if len(content) > 1200:
        print("\n--- Vista previa limitada a 1200 caracteres ---")

    say("Archivo leído.")
    set_last_interaction("command")
    return True


def extract_workspace(query: str) -> tuple[str, str]:
    text = query.strip()
    lower = text.lower()
    workspace = "kanye"

    for marker in [" en proyecto ", " del proyecto ", " en el proyecto "]:
        if marker in lower:
            idx = lower.rfind(marker)
            workspace = text[idx + len(marker):].strip().lower()
            text = text[:idx].strip()
            break

    return text, workspace


def handle_file_action(query: str) -> bool:
    query, workspace = extract_workspace(query)
    text = query.lower().strip()

    prefixes_read = ["lee archivo", "leer archivo"]
    for prefix in prefixes_read:
        if text.startswith(prefix):
            return _read_file_command(query[len(prefix):], workspace)

    prefixes_backup = ["haz backup de archivo", "hacer backup de archivo"]
    for prefix in prefixes_backup:
        if text.startswith(prefix):
            file_path = query[len(prefix):].strip()
            done = backup_file(file_path, workspace)
            say("Backup creado." if done else "No pude crear el backup.")
            set_last_interaction("command")
            return True

    prefixes_search = ["busca en archivo", "buscar en archivo"]
    for prefix in prefixes_search:
        if text.startswith(prefix):
            rest = query[len(prefix):].strip()
            if " el texto " not in rest:
                say("Usa el formato: busca en archivo main.py el texto LAST_INTERACTION.")
                return True
            file_path, search_text = rest.split(" el texto ", 1)
            found = search_in_file(file_path.strip(), search_text.strip(), workspace)
            say("Texto encontrado." if found else "No encontré ese texto.")
            set_last_interaction("command")
            return True

    if text.startswith("reemplaza") or text.startswith("reemplazar"):
        prefix = "reemplazar" if text.startswith("reemplazar") else "reemplaza"
        rest = query[len(prefix):].strip()
        if " por " not in rest or " en archivo " not in rest:
            say("Usa el formato: reemplaza texto viejo por texto nuevo en archivo main.py.")
            return True
        old_and_new, file_path = rest.rsplit(" en archivo ", 1)
        old_text, new_text = old_and_new.split(" por ", 1)
        changed = replace_in_file(
            file_path.strip(), old_text.strip(), new_text.strip(), workspace
        )
        say("Archivo modificado." if changed else "No se modificó el archivo.")
        set_last_interaction("command")
        return True

    say("No entendí la acción de archivo.")
    set_last_interaction("command")
    return True


def handle_command(command: str) -> bool:
    if LAST_INTERACTION["type"] == "chat" and not is_clear_system_command(command):
        intent = "chat_direct"
        query = command
    else:
        result = detect_intent(command)
        intent = result["intent"]
        query = result["query"]

    if intent == "exit":
        say("Cerrando.")
        set_last_interaction("command")
        return False

    elif intent == "open_app":
        print(f"K.A.N.Y.E.: Buscando app parecida a: {query}")

        if open_site(query):
            say(f"Abriendo {query}.")
            print()
            set_last_interaction("command")
            return True

        app = find_best_app_match(query)

        if not app:
            say(response("app_not_found"))
            print()
            set_last_interaction("command")
            return True

        print(f"K.A.N.Y.E.: Encontré: {app['name']} | Score: {app['score']}")

        if open_application(app):
            say(response("app_opened", name=app["name"]))
        else:
            say("Encontré la app, pero no pude abrirla.")
        print()
        set_last_interaction("command")

    elif intent == "close_app":
        if not query:
            say("Decime qué programa querés cerrar.")
            print()
            set_last_interaction("command")
            return True

        print(f"K.A.N.Y.E.: Buscando proceso activo: {query}")

        if close_application(query):
            say(response("app_closed", name=query))
        else:
            say("No encontré ese programa abierto o no pude cerrarlo.")
        print()
        set_last_interaction("command")

    elif intent == "web_search":
        print(f"K.A.N.Y.E.: Buscando en Google: {query}")
        if search_google(query):
            say(response("search_opened"))
        else:
            say("No pude hacer la búsqueda.")
        print()
        set_last_interaction("command")

    elif intent == "open_folder":
        print(f"K.A.N.Y.E.: Abriendo carpeta: {query}")
        if open_folder(query):
            say(response("folder_opened"))
        else:
            say("No pude abrir esa carpeta.")
        print()
        set_last_interaction("command")

    elif intent == "activate_mode":
        if not query:
            say("Decime qué modo querés activar.")
            print()
            set_last_interaction("command")
            return True

        if activate_mode(query):
            say(response("mode_activated", name=query))
        else:
            say("No pude activar ese modo.")
        print()
        set_last_interaction("command")

    elif intent == "create_mode":
        if not query:
            say("Decime el nombre del modo. Por ejemplo: crea modo gaming.")
            print()
            set_last_interaction("command")
            return True

        if create_mode_interactive(query):
            say("Modo creado correctamente.")
        else:
            say("No se creó el modo.")
        print()
        set_last_interaction("command")

    elif intent == "list_modes":
        list_modes()
        say("Estos son los modos disponibles.")
        print()
        set_last_interaction("command")

    elif intent == "delete_mode":
        if not query:
            say("Decime qué modo querés eliminar.")
            print()
            set_last_interaction("command")
            return True

        say("Modo eliminado correctamente." if delete_mode(query) else "No se eliminó el modo.")
        print()
        set_last_interaction("command")

    elif intent == "edit_mode":
        if not query:
            say("Decime qué modo querés editar.")
            print()
            set_last_interaction("command")
            return True

        say("Modo editado correctamente." if edit_mode_interactive(query) else "No se editó el modo.")
        print()
        set_last_interaction("command")

    elif intent == "play_music":
        if not query:
            say("Decime qué canción querés escuchar.")
            print()
            set_last_interaction("command")
            return True

        print(f"K.A.N.Y.E.: Buscando en YouTube Music: {query}")
        play_on_youtube_music(query)
        say(response("music_playing", name=query))
        print()
        set_last_interaction("command")

    elif intent == "media_control":
        return handle_media_control(query)

    elif intent == "file_action":
        return handle_file_action(query)

    elif intent == "chat_direct":
        return handle_chat(query)

    elif intent == "open_site":
        if not query:
            say("Decime qué página querés abrir.")
            print()
            set_last_interaction("command")
            return True

        if open_site(query):
            say(response("site_opened", name=query))
        else:
            say("No encontré esa página guardada.")
        print()
        set_last_interaction("command")

    elif intent == "chat":
        config = get_config()

        if config.get("use_llm_classifier", True):
            print(f"K.A.N.Y.E.: Analizando intención con LLM: {query}")
            llm_result = classify_with_llm(query)
            llm_intent = llm_result["intent"]
            llm_query = llm_result["query"]
            print(f"K.A.N.Y.E.: LLM interpretó: {llm_intent} | {llm_query}")

            dispatch = {
                "activate_mode": f"activa modo {llm_query}",
                "open_app": f"abre {llm_query}",
                "close_app": f"cierra {llm_query}",
                "open_folder": f"abre {llm_query}",
                "web_search": f"busca {llm_query}",
                "play_music": f"pon {llm_query}",
            }

            if llm_intent in dispatch:
                set_last_interaction("command")
                return handle_command(dispatch[llm_intent])

            return handle_chat(llm_query)

        return handle_chat(query)

    else:
        say(response("not_understood"))
        print()
        set_last_interaction("command")

    return True


def main():
    config = get_config()
    hotkey = config.get("hotkey", "ctrl+f9")

    print("K.A.N.Y.E. iniciado.")
    print(f"Presioná [{hotkey.upper()}] para activar el asistente.")
    print("Decí 'salir' para cerrar.\n")

    speak("KANYE iniciado.", use_cache=True)

    running = True

    while running:
        print(f"Estado: esperando [{hotkey.upper()}]...")
        wait_for_hotkey(hotkey)

        say("Te escucho.")
        print("Estado: escuchando...")

        command = listen_once(timeout=6, phrase_time_limit=10)

        if not command:
            say("No escuché nada.")
            continue

        command = normalize_text(command)
        print(f"Comando detectado: {command}")

        running = handle_command(command)


if __name__ == "__main__":
    main()
