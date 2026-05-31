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
    edit_mode_interactive
)
from core.speech_to_text import listen_once
from core.text_to_speech import speak
from core.local_llm import ask_llm
from core.text_normalizer import normalize_text
from core.llm_intent import classify_with_llm
from core.file_actions import read_file, search_in_file, backup_file, replace_in_file
from core.music_actions import play_on_youtube_music
from core.media_actions import (
    media_play_pause,
    media_next,
    media_previous,
    volume_up,
    volume_down,
    volume_mute
)
from core.process_actions import close_application
from core.site_actions import open_site
from core.responses import response

LAST_INTERACTION = {
    "type": None
}

WAKE_WORDS = [
    "kanye",
    "kanie",
    "kan ye",
    "caña",
    "canye",
    "calle"
]


def set_last_interaction(interaction_type: str) -> None:
    """
    Guarda si lo último fue comando o conversación.
    """
    LAST_INTERACTION["type"] = interaction_type


def is_clear_system_command(command: str) -> bool:
    """
    Detecta si el usuario está dando un comando claro del sistema.
    Si no es claro, lo dejamos como conversación cuando venimos de chat.
    """
    text = command.lower().strip()

    command_starters = [
        "abre sitio",
        "abrir sitio",
        "abre página",
        "abre pagina",
        "abrir página",
        "abrir pagina",
        "cierra",
        "cerrar",
        "cerrá",
        "termina",
        "terminar",
        "mata",
        "cerrar programa",
        "cierra programa",
        "pon",
        "pone",
        "reproduce",
        "toca",
        "pon música",
        "poner música",
        "busca música",
        "busca cancion",
        "busca canción",
        "abre",
        "abrí",
        "abrir",
        "ejecuta",
        "lanza",

        "busca",
        "buscar",
        "googlea",
        "investiga",

        "activa modo",
        "activar modo",
        "modo",

        "crea modo",
        "crear modo",
        "nuevo modo",
        "agrega modo",
        "agregar modo",

        "edita modo",
        "editar modo",
        "modifica modo",
        "modificar modo",
        "cambia modo",
        "cambiar modo",

        "elimina modo",
        "eliminar modo",
        "borra modo",
        "borrar modo",
        "quita modo",
        "quitar modo",

        "modos",
        "lista modos",
        "ver modos",
        "mostrar modos",

        "salir",
        "cerrar",
        "exit",
        "quit"
    ]

    return any(text.startswith(starter) for starter in command_starters)


def say(message: str) -> None:
    """
    Imprime y habla el mensaje usando caché.
    Para comandos fijos del sistema.
    """
    print(f"K.A.N.Y.E.: {message}")
    speak(message, use_cache=True)


def remove_wake_word(text: str) -> str:
    text = text.lower().strip()

    for wake_word in WAKE_WORDS:
        if text.startswith(wake_word):
            return text.replace(wake_word, "", 1).strip()

    return ""


def handle_chat(query: str) -> bool:
    """
    Maneja conversación normal con el LLM.
    No usa caché porque las respuestas del LLM son variables.
    """
    print(f"K.A.N.Y.E.: Conversando: {query}")

    answer = ask_llm(query)

    print(f"K.A.N.Y.E.: {answer}\n")
    speak(answer, use_cache=False)

    set_last_interaction("chat")
    return True
def handle_media_control(action: str) -> bool:
    if action == "play_pause":
        done = media_play_pause()

        if done:
            say("Listo.")
        else:
            say("No pude pausar o reanudar.")

    elif action == "next":
        done = media_next()

        if done:
            say("Siguiente canción.")
        else:
            say("No pude pasar la canción.")

    elif action == "previous":
        done = media_previous()

        if done:
            say("Canción anterior.")
        else:
            say("No pude regresar la canción.")

    elif action == "volume_up":
        done = volume_up()

        if done:
            say("Subiendo volumen.")
        else:
            say("No pude subir el volumen.")

    elif action == "volume_down":
        done = volume_down()

        if done:
            say("Bajando volumen.")
        else:
            say("No pude bajar el volumen.")

    elif action == "mute":
        done = volume_mute()

        if done:
            say("Silencio.")
        else:
            say("No pude silenciar.")

    else:
        say("No entendí el control multimedia.")

    print()
    set_last_interaction("command")
    return True

def handle_command(command: str) -> bool:
    """
    Ejecuta un comando.
    Devuelve False si el usuario quiere salir.
    Devuelve True para seguir corriendo.
    """

    # Si venimos de una conversación y el usuario NO dio un comando claro,
    # seguimos conversando sin pasar por el clasificador de intención.
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

        site_opened = open_site(query)

        if site_opened:
            say(f"Abriendo {query}.")
            print()
            set_last_interaction("command")
            return True

        app = find_best_app_match(query)

        if not app:
            say("No encontré una app parecida.")
            print()
            set_last_interaction("command")
            return True

        print(f"K.A.N.Y.E.: Encontré: {app['name']} | Score: {app['score']}")

        opened = open_application(app)

        if opened:
            say(f"Abriendo {app['name']}.")
            print()
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

        print(f"K.A.N.Y.E.: Buscando programa activo parecido a: {query}")

        closed = close_application(query)

        if closed:
            say(f"Cerrando {query}.")
            print()
        else:
            say("No encontré ese programa abierto o no pude cerrarlo.")
            print()

        set_last_interaction("command")

    elif intent == "web_search":
        print(f"K.A.N.Y.E.: Buscando en Google: {query}")

        searched = search_google(query)

        if searched:
            say("Búsqueda abierta.")
            print()
        else:
            say("No pude hacer la búsqueda.")
            print()

        set_last_interaction("command")

    elif intent == "open_folder":
        print(f"K.A.N.Y.E.: Abriendo carpeta: {query}")

        opened = open_folder(query)

        if opened:
            say("Carpeta abierta.")
            print()
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

        activated = activate_mode(query)

        if activated:
            say(f"Modo {query} activado.")
            print()
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

        created = create_mode_interactive(query)

        if created:
            say("Modo creado correctamente.")
            print()
        else:
            say("No se creó el modo.")
            print()

        set_last_interaction("command")

    elif intent == "list_modes":
        list_modes()
        speak("Estos son los modos disponibles.", use_cache=True)
        print()

        set_last_interaction("command")

    elif intent == "delete_mode":
        if not query:
            say("Decime qué modo querés eliminar. Por ejemplo: elimina modo gaming.")
            print()
            set_last_interaction("command")
            return True

        deleted = delete_mode(query)

        if deleted:
            say("Modo eliminado correctamente.")
            print()
        else:
            say("No se eliminó el modo.")
            print()

        set_last_interaction("command")

    elif intent == "edit_mode":
        if not query:
            say("Decime qué modo querés editar. Por ejemplo: editar modo gaming.")
            print()
            set_last_interaction("command")
            return True

        edited = edit_mode_interactive(query)

        if edited:
            say("Modo editado correctamente.")
            print()
        else:
            say("No se editó el modo.")
            print()

        set_last_interaction("command")

    elif intent == "play_music":
        if not query:
            say("Decime qué canción querés escuchar.")
            print()
            set_last_interaction("command")
            return True

        print(f"K.A.N.Y.E.: Buscando en YouTube Music: {query}")

        played = play_on_youtube_music(query)

        if played:
            say(f"Reproduciendo {query} en YouTube Music.")
            print()
        else:
            say("No pude abrir YouTube Music.")
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

        opened = open_site(query)

        if opened:
            say(f"Abriendo {query}.")
            print()
        else:
            say("No encontré esa página guardada.")
            print()

        set_last_interaction("command")


    elif intent == "chat":
        print(f"K.A.N.Y.E.: Analizando intención con LLM: {query}")

        llm_result = classify_with_llm(query)

        llm_intent = llm_result["intent"]
        llm_query = llm_result["query"]

        print(f"K.A.N.Y.E.: LLM interpretó: {llm_intent} | {llm_query}")

        if llm_intent == "activate_mode":
            set_last_interaction("command")
            return handle_command(f"activa modo {llm_query}")

        elif llm_intent == "open_app":
            set_last_interaction("command")
            return handle_command(f"abre {llm_query}")

        elif llm_intent == "close_app":
            set_last_interaction("command")
            return handle_command(f"cierra {llm_query}")

        elif llm_intent == "open_folder":
            set_last_interaction("command")
            return handle_command(f"abre {llm_query}")

        elif llm_intent == "web_search":
            set_last_interaction("command")
            return handle_command(f"busca {llm_query}")

        elif llm_intent == "play_music":
            set_last_interaction("command")
            return handle_command(f"pon {llm_query}")

        return handle_chat(llm_query)
    

    else:
        say("No entendí el comando.")
        print()
        set_last_interaction("command")

    return True

def extract_workspace(query: str) -> tuple[str, str]:
    """
    Extrae 'en proyecto web' o 'del proyecto web'.
    Devuelve:
    - texto sin esa parte
    - nombre del proyecto
    """
    text = query.strip()
    lower = text.lower()

    workspace = "kanye"

    markers = [
        " en proyecto ",
        " del proyecto ",
        " en el proyecto "
    ]

    for marker in markers:
        if marker in lower:
            index = lower.rfind(marker)
            workspace = text[index + len(marker):].strip().lower()
            text = text[:index].strip()
            break

    return text, workspace


def handle_file_action(query: str) -> bool:
    query, workspace = extract_workspace(query)
    text = query.lower().strip()

    if text.startswith("lee archivo"):
        file_path = query.replace("lee archivo", "", 1).strip()
        content = read_file(file_path, workspace)

        if content is None:
            say("No pude leer el archivo.")
            return True

        preview = content[:1200]

        print("\n--- CONTENIDO DEL ARCHIVO ---")
        print(preview)

        if len(content) > 1200:
            print("\n--- Vista previa limitada a 1200 caracteres ---")

        say("Archivo leído.")
        set_last_interaction("command")
        return True

    if text.startswith("leer archivo"):
        file_path = query.replace("leer archivo", "", 1).strip()
        content = read_file(file_path, workspace)

        if content is None:
            say("No pude leer el archivo.")
            return True

        preview = content[:1200]

        print("\n--- CONTENIDO DEL ARCHIVO ---")
        print(preview)

        if len(content) > 1200:
            print("\n--- Vista previa limitada a 1200 caracteres ---")

        say("Archivo leído.")
        set_last_interaction("command")
        return True

    if text.startswith("haz backup de archivo"):
        file_path = query.replace("haz backup de archivo", "", 1).strip()
        done = backup_file(file_path, workspace)

        if done:
            say("Backup creado.")
        else:
            say("No pude crear el backup.")

        set_last_interaction("command")
        return True

    if text.startswith("hacer backup de archivo"):
        file_path = query.replace("hacer backup de archivo", "", 1).strip()
        done = backup_file(file_path, workspace)

        if done:
            say("Backup creado.")
        else:
            say("No pude crear el backup.")

        set_last_interaction("command")
        return True

    if text.startswith("busca en archivo"):
        rest = query.replace("busca en archivo", "", 1).strip()

        if " el texto " not in rest:
            say("Usa el formato: busca en archivo main.py el texto LAST_INTERACTION.")
            return True

        file_path, search_text = rest.split(" el texto ", 1)
        found = search_in_file(file_path.strip(), search_text.strip(), workspace)

        if found:
            say("Texto encontrado.")
        else:
            say("No encontré ese texto.")

        set_last_interaction("command")
        return True

    if text.startswith("buscar en archivo"):
        rest = query.replace("buscar en archivo", "", 1).strip()

        if " el texto " not in rest:
            say("Usa el formato: buscar en archivo main.py el texto LAST_INTERACTION.")
            return True

        file_path, search_text = rest.split(" el texto ", 1)
        found = search_in_file(file_path.strip(), search_text.strip(), workspace)

        if found:
            say("Texto encontrado.")
        else:
            say("No encontré ese texto.")

        set_last_interaction("command")
        return True

    if text.startswith("reemplaza"):
        rest = query.replace("reemplaza", "", 1).strip()

        if " por " not in rest or " en archivo " not in rest:
            say("Usa el formato: reemplaza texto viejo por texto nuevo en archivo main.py.")
            return True

        old_and_new, file_path = rest.rsplit(" en archivo ", 1)
        old_text, new_text = old_and_new.split(" por ", 1)

        changed = replace_in_file(
            file_path.strip(),
            old_text.strip(),
            new_text.strip(),
            workspace
        )

        if changed:
            say("Archivo modificado.")
        else:
            say("No se modificó el archivo.")

        set_last_interaction("command")
        return True

    say("No entendí la acción de archivo.")
    set_last_interaction("command")
    return True

def main():
    print("K.A.N.Y.E. iniciado en modo escucha continua.")
    print("Di comandos empezando con 'Kanye'.")
    print("Ejemplos:")
    print("- Kanye abre notas")
    print("- Kanye busca árboles B")
    print("- Kanye activa modo gaming")
    print("- Kanye salir\n")

    speak("K.A.N.Y.E. iniciado.", use_cache=True)

    running = True

    while running:
        heard_text = listen_once(timeout=8, phrase_time_limit=12)

        if not heard_text:
            continue

        heard_text = normalize_text(heard_text)

        print(f"Escuché: {heard_text}")

        command = remove_wake_word(heard_text)

        if not command:
            continue

        print(f"Comando detectado: {command}")

        running = handle_command(command)


if __name__ == "__main__":
    main()