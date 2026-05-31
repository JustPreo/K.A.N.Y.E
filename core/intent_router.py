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
    
    close_words = [
        "cierra",
        "cerrar",
        "cerrá",
        "termina",
        "terminar",
        "mata",
        "cerrar programa",
        "cierra programa"
    ]

    for word in close_words:
        if text.startswith(word):
            query = text.replace(word, "", 1).strip()

            query = query.replace("programa", "", 1).strip()
            query = query.replace("aplicación", "", 1).strip()
            query = query.replace("aplicacion", "", 1).strip()

            return {
                "intent": "close_app",
                "query": query
            }
    
    media_commands = {
        "pausa": "play_pause",
        "pausa la música": "play_pause",
        "pausar música": "play_pause",
        "reanuda": "play_pause",
        "reanuda la música": "play_pause",
        "continua": "play_pause",
        "continúa": "play_pause",
        "sigue": "play_pause",

        "siguiente": "next",
        "siguiente canción": "next",
        "pasa canción": "next",
        "cambia canción": "next",

        "anterior": "previous",
        "canción anterior": "previous",
        "regresa canción": "previous",
        "devuelve canción": "previous",

        "sube volumen": "volume_up",
        "subir volumen": "volume_up",
        "más volumen": "volume_up",

        "baja volumen": "volume_down",
        "bajar volumen": "volume_down",
        "menos volumen": "volume_down",

        "silencia": "mute",
        "silencio": "mute",
        "mute": "mute",
        "quita volumen": "mute"
    }

    for phrase, action in media_commands.items():
        if text.startswith(phrase):
            return {
                "intent": "media_control",
                "query": action
            }
    
    music_words = [
        "pon",
        "pone",
        "reproduce",
        "toca",
        "pon música",
        "poner música",
        "busca música",
        "busca cancion",
        "busca canción"
    ]

    for word in music_words:
        if text.startswith(word):
            query = text.replace(word, "", 1).strip()

            # Limpieza extra
            query = query.replace("en youtube music", "").strip()
            query = query.replace("en youtube", "").strip()

            return {
                "intent": "play_music",
                "query": query
            }
    

    file_action_words = [
        "lee archivo",
        "leer archivo",
        "busca en archivo",
        "buscar en archivo",
        "haz backup de archivo",
        "hacer backup de archivo",
        "reemplaza",
        "reemplazar"
    ]

    for word in file_action_words:
        if text.startswith(word):
            return {
                "intent": "file_action",
                "query": text
            }
    
    edit_mode_words = [
        "edita modo",
        "editar modo",
        "modifica modo",
        "modificar modo",
        "cambia modo",
        "cambiar modo"
    ]

    for word in edit_mode_words:
        if text.startswith(word):
            query = text.replace(word, "", 1).strip()

            return {
                "intent": "edit_mode",
                "query": query
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
    "intent": "chat",
    "query": text
}