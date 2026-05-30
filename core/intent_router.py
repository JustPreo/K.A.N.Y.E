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
    
        # Activar modo
    for word in mode_words:
        if text.startswith(word):
            query = text.replace(word, "", 1).strip()

            return {
                "intent": "activate_mode",
                "query": query
            }

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