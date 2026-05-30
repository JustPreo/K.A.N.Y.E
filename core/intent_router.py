def detect_intent(command: str) -> dict:
    """
    Detecta qué quiere hacer el usuario.
    Devuelve un diccionario con:
    - intent: tipo de acción
    - query: contenido útil del comando
    """

    text = command.lower().strip()

    if text in ["salir", "cerrar", "exit", "quit"]:
        return {
            "intent": "exit",
            "query": ""
        }
    
    delete_mode_words = [
        "elimina modo",
        "eliminar modo",
        "borra modo",
        "borrar modo",
        "quita modo",
        "quitar modo"
    ]

    for word in delete_mode_words:
        if text.startswith(word):
            query = text.replace(word, "", 1).strip()

            return {
                "intent": "delete_mode",
                "query": query
            }
    
    create_mode_words = [
        "crea modo",
        "crear modo",
        "agrega modo",
        "agregar modo",
        "nuevo modo"
    ]

    for word in create_mode_words:
        if text.startswith(word):
            query = text.replace(word, "", 1).strip()

            return {
                "intent": "create_mode",
                "query": query
            }

    if text in ["modos", "lista modos", "ver modos", "mostrar modos"]:
        return {
            "intent": "list_modes",
            "query": ""
        }
        # Activar modo
    

    open_words = [
        "abre",
        "abrí",
        "abrir",
        "abreme",
        "ábreme",
        "ejecuta",
        "lanza"
    ]

    search_words = [
        "busca",
        "buscar",
        "googlea",
        "investiga"
    ]

    mode_words = [
    "activa modo",
    "activar modo",
    "modo"
    ]

    for word in mode_words:
        if text.startswith(word):
            query = text.replace(word, "", 1).strip()

            return {
                "intent": "activate_mode",
                "query": query
            }

    
    

    folder_words = [
        "descargas",
        "downloads",
        "documentos",
        "documents",
        "escritorio",
        "desktop",
        "imágenes",
        "imagenes",
        "pictures",
        "videos",
        "música",
        "musica",
        "music"
    ]

    # Buscar en Google
    for word in search_words:
        if text.startswith(word):
            query = text.replace(word, "", 1).strip()

            if query.startswith("en google"):
                query = query.replace("en google", "", 1).strip()

            return {
                "intent": "web_search",
                "query": query
            }

    # Abrir algo
    for word in open_words:
        if text.startswith(word):
            query = text.replace(word, "", 1).strip()

            if query in folder_words:
                return {
                    "intent": "open_folder",
                    "query": query
                }

            return {
                "intent": "open_app",
                "query": query
            }

    # Si no reconoce nada, asumimos que quiere abrir una app
    return {
        "intent": "open_app",
        "query": text
    }