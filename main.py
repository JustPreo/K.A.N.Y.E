from core.app_resolver import find_best_app_match
from core.system_actions import open_application


def clean_open_command(text: str) -> str:
    text = text.lower().strip()

    trigger_words = [
        "abre",
        "abrí",
        "abrir",
        "abreme",
        "ábreme",
        "ejecuta",
        "lanza"
    ]

    for word in trigger_words:
        if text.startswith(word):
            return text.replace(word, "", 1).strip()

    return text


def main():
    print("K.A.N.Y.E. iniciado en modo texto.")
    print("Ejemplo: abre notas")
    print("Escribe 'salir' para cerrar.\n")

    while True:
        command = input("Tú: ")

        if command.lower().strip() == "salir":
            print("K.A.N.Y.E.: Cerrando.")
            break

        app_query = clean_open_command(command)

        print(f"K.A.N.Y.E.: Buscando app parecida a: {app_query}")

        app = find_best_app_match(app_query)

        if not app:
            print("K.A.N.Y.E.: No encontré una app parecida.\n")
            continue

        print(f"K.A.N.Y.E.: Encontré: {app['name']} | Score: {app['score']}")

        opened = open_application(app)

        if opened:
            print(f"K.A.N.Y.E.: Abriendo {app['name']}.\n")
        else:
            print("K.A.N.Y.E.: Encontré la app, pero no pude abrirla.\n")


if __name__ == "__main__":
    main()