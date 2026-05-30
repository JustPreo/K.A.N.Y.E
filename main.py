from core.intent_router import detect_intent
from core.app_resolver import find_best_app_match
from core.system_actions import open_application
from core.web_search import search_google
from core.folder_actions import open_folder
from core.mode_actions import activate_mode, create_mode_interactive, list_modes, delete_mode


def main():
    print("K.A.N.Y.E. iniciado en modo texto.")
    print("Ejemplos:")
    print("- abre notas")
    print("- abre calculadora")
    print("- busca árboles B")
    print("- abre descargas")
    print("- salir\n")

    while True:
        command = input("Tú: ")

        result = detect_intent(command)

        intent = result["intent"]
        query = result["query"]

        if intent == "exit":
            print("K.A.N.Y.E.: Cerrando.")
            break

        elif intent == "open_app":
            print(f"K.A.N.Y.E.: Buscando app parecida a: {query}")

            app = find_best_app_match(query)

            if not app:
                print("K.A.N.Y.E.: No encontré una app parecida.\n")
                continue

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
                continue

            activated = activate_mode(query)

            if activated:
                print("K.A.N.Y.E.: Modo ejecutado correctamente.\n")
            else:
                print("K.A.N.Y.E.: No pude activar ese modo.\n")

        elif intent == "create_mode":
            if not query:
                print("K.A.N.Y.E.: Decime el nombre del modo. Ej: crea modo gaming\n")
                continue

            created = create_mode_interactive(query)

            if created:
                print("K.A.N.Y.E.: Modo creado correctamente.\n")
            else:
                print("K.A.N.Y.E.: No se creó el modo.\n")

        elif intent == "delete_mode":
            if not query:
                print("K.A.N.Y.E.: Decime qué modo querés eliminar. Ej: elimina modo gaming\n")
                continue

            deleted = delete_mode(query)

            if deleted:
                print("K.A.N.Y.E.: Modo eliminado correctamente.\n")
            else:
                print("K.A.N.Y.E.: No se eliminó el modo.\n")

        elif intent == "list_modes":
            list_modes()
            print()
        
        else:
            print("K.A.N.Y.E.: No entendí el comando.\n")


if __name__ == "__main__":
    main()