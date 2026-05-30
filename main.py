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


WAKE_WORDS = ["kanye", "kanie", "kan ye", "caña", "canye"]


def remove_wake_word(text: str) -> str:
    text = text.lower().strip()

    for wake_word in WAKE_WORDS:
        if text.startswith(wake_word):
            return text.replace(wake_word, "", 1).strip()

    return ""


def handle_command(command: str) -> bool:
    """
    Ejecuta un comando.
    Devuelve False si el usuario quiere salir.
    Devuelve True para seguir corriendo.
    """

    result = detect_intent(command)

    intent = result["intent"]
    query = result["query"]

    if intent == "exit":
        print("K.A.N.Y.E.: Cerrando.")
        return False

    elif intent == "open_app":
        print(f"K.A.N.Y.E.: Buscando app parecida a: {query}")

        app = find_best_app_match(query)

        if not app:
            print("K.A.N.Y.E.: No encontré una app parecida.\n")
            return True

        print(f"K.A.N.Y.E.: Encontré: {app['name']} | Score: {app['score']}")

        opened = open_application(app)

        if opened:
            print(f"K.A.N.Y.E.: Abriendo {app['name']}.\n")
        else:
            print("K.A.N.Y.E.: Encontré la app, pero no pude abrirla.\n")

    elif intent == "web_search":
        print(f"K.A.N.Y.E.: Buscando en Google: {query}")

        searched = search_google(query)

        if searched:
            print("K.A.N.Y.E.: Búsqueda abierta.\n")
        else:
            print("K.A.N.Y.E.: No pude hacer la búsqueda.\n")

    elif intent == "open_folder":
        print(f"K.A.N.Y.E.: Abriendo carpeta: {query}")

        opened = open_folder(query)

        if opened:
            print("K.A.N.Y.E.: Carpeta abierta.\n")
        else:
            print("K.A.N.Y.E.: No pude abrir esa carpeta.\n")

    elif intent == "activate_mode":
        if not query:
            print("K.A.N.Y.E.: Decime qué modo querés activar.\n")
            return True

        activated = activate_mode(query)

        if activated:
            print("K.A.N.Y.E.: Modo ejecutado correctamente.\n")
        else:
            print("K.A.N.Y.E.: No pude activar ese modo.\n")

    elif intent == "create_mode":
        if not query:
            print("K.A.N.Y.E.: Decime el nombre del modo. Ej: crea modo gaming\n")
            return True

        created = create_mode_interactive(query)

        if created:
            print("K.A.N.Y.E.: Modo creado correctamente.\n")
        else:
            print("K.A.N.Y.E.: No se creó el modo.\n")

    elif intent == "list_modes":
        list_modes()
        print()

    elif intent == "delete_mode":
        if not query:
            print("K.A.N.Y.E.: Decime qué modo querés eliminar. Ej: elimina modo gaming\n")
            return True

        deleted = delete_mode(query)

        if deleted:
            print("K.A.N.Y.E.: Modo eliminado correctamente.\n")
        else:
            print("K.A.N.Y.E.: No se eliminó el modo.\n")

    elif intent == "edit_mode":
        if not query:
            print("K.A.N.Y.E.: Decime qué modo querés editar. Ej: editar modo gaming\n")
            return True

        edited = edit_mode_interactive(query)

        if edited:
            print("K.A.N.Y.E.: Modo editado correctamente.\n")
        else:
            print("K.A.N.Y.E.: No se editó el modo.\n")

    else:
        print("K.A.N.Y.E.: No entendí el comando.\n")

    return True


def main():
    print("K.A.N.Y.E. iniciado en modo escucha continua.")
    print("Di comandos empezando con 'Kanye'.")
    print("Ejemplos:")
    print("- Kanye abre notas")
    print("- Kanye busca árboles B")
    print("- Kanye activa modo gaming")
    print("- Kanye salir\n")

    running = True

    while running:
        heard_text = listen_once(timeout=4, phrase_time_limit=6)

        if not heard_text:
            continue

        print(f"Escuché: {heard_text}")

        command = remove_wake_word(heard_text)

        if not command:
            continue

        print(f"Comando detectado: {command}")

        running = handle_command(command)


if __name__ == "__main__":
    main()