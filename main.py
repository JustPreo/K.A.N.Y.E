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


WAKE_WORDS = ["kanye", "kanie", "kan ye", "caña", "canye"]


def say(message: str) -> None:
    """
    Imprime y habla el mensaje.
    """
    print(f"K.A.N.Y.E.: {message}")
    speak(message)


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
        say("Cerrando.")
        return False

    elif intent == "open_app":
        print(f"K.A.N.Y.E.: Buscando app parecida a: {query}")

        app = find_best_app_match(query)

        if not app:
            say("No encontré una app parecida.")
            print()
            return True

        print(f"K.A.N.Y.E.: Encontré: {app['name']} | Score: {app['score']}")

        opened = open_application(app)

        if opened:
            say(f"Abriendo {app['name']}.")
            print()
        else:
            say("Encontré la app, pero no pude abrirla.")
            print()

    elif intent == "web_search":
        print(f"K.A.N.Y.E.: Buscando en Google: {query}")

        searched = search_google(query)

        if searched:
            say("Búsqueda abierta.")
            print()
        else:
            say("No pude hacer la búsqueda.")
            print()

    elif intent == "open_folder":
        print(f"K.A.N.Y.E.: Abriendo carpeta: {query}")

        opened = open_folder(query)

        if opened:
            say("Carpeta abierta.")
            print()
        else:
            say("No pude abrir esa carpeta.")
            print()

    elif intent == "activate_mode":
        if not query:
            say("Decime qué modo querés activar.")
            print()
            return True

        activated = activate_mode(query)

        if activated:
            say("Modo ejecutado correctamente.")
            print()
        else:
            say("No pude activar ese modo.")
            print()

    elif intent == "create_mode":
        if not query:
            say("Decime el nombre del modo. Por ejemplo: crea modo gaming.")
            print()
            return True

        created = create_mode_interactive(query)

        if created:
            say("Modo creado correctamente.")
            print()
        else:
            say("No se creó el modo.")
            print()

    elif intent == "list_modes":
        list_modes()
        speak("Estos son los modos disponibles.")
        print()

    elif intent == "delete_mode":
        if not query:
            say("Decime qué modo querés eliminar. Por ejemplo: elimina modo gaming.")
            print()
            return True

        deleted = delete_mode(query)

        if deleted:
            say("Modo eliminado correctamente.")
            print()
        else:
            say("No se eliminó el modo.")
            print()

    elif intent == "edit_mode":
        if not query:
            say("Decime qué modo querés editar. Por ejemplo: editar modo gaming.")
            print()
            return True

        edited = edit_mode_interactive(query)

        if edited:
            say("Modo editado correctamente.")
            print()
        else:
            say("No se editó el modo.")
            print()

    else:
        say("No entendí el comando.")
        print()

    return True


def main():
    print("K.A.N.Y.E. iniciado en modo escucha continua.")
    print("Di comandos empezando con 'Kanye'.")
    print("Ejemplos:")
    print("- Kanye abre notas")
    print("- Kanye busca árboles B")
    print("- Kanye activa modo gaming")
    print("- Kanye salir\n")

    speak("K.A.N.Y.E. iniciado.")

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