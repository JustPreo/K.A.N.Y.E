from core.keyboard_actions import SHORTCUT_COMMANDS


def detect_intent(command: str) -> dict:
    text = command.lower().strip()

    # ── Salir ─────────────────────────────────────────────────────────────────
    if text in ["salir", "cerrar", "exit", "quit"]:
        return {"intent": "exit", "query": ""}

    # ── Historial ─────────────────────────────────────────────────────────────
    if text in ["borra historial", "borrar historial", "limpia historial",
                "limpiar historial", "olvida la conversación", "nueva conversación"]:
        return {"intent": "clear_history", "query": ""}

    # ── Focus ─────────────────────────────────────────────────────────────────
    if text in ["desbloquea", "desbloquear", "desactiva focus",
                "desactivar focus", "salir del focus", "salir de focus",
                "termina focus", "terminar focus"]:
        return {"intent": "focus_off", "query": ""}

    if text in ["estado focus", "tiempo focus", "cuánto focus", "cuanto focus",
                "cuánto queda", "cuanto queda"]:
        return {"intent": "focus_status", "query": ""}

    # ── Teclado — shortcuts ───────────────────────────────────────────────────
    if text in SHORTCUT_COMMANDS:
        return {"intent": "keyboard_shortcut", "query": text}

    # ── Teclado — escribir texto ──────────────────────────────────────────────
    write_words = [
        "escribe en mayúsculas ",
        "escribí en mayúsculas ",
        "escribe mayúsculas ",
        "escribe ",
        "escribí ",
        "escribir ",
        "dictá ",
        "dictar ",
        "teclea ",
        "tipea ",
    ]
    for word in write_words:
        if text.startswith(word):
            raw = command[len(word):]           # conserva mayúsculas originales
            uppercase = "mayúsculas" in word or "mayusculas" in word
            return {"intent": "keyboard_type", "query": raw, "uppercase": uppercase}

    # ── Cerrar app ───────────────────────────────────────────────────────────
    close_words = [
        "cierra", "cerrar", "cerrá", "termina", "terminar",
        "mata", "cerrar programa", "cierra programa",
    ]
    for word in close_words:
        if text.startswith(word):
            query = text.replace(word, "", 1).strip()
            query = query.replace("programa", "", 1).strip()
            query = query.replace("aplicación", "", 1).strip()
            query = query.replace("aplicacion", "", 1).strip()
            return {"intent": "close_app", "query": query}

    # ── Guardar sitio ─────────────────────────────────────────────────────────
    for word in ["guarda sitio", "guardar sitio", "agrega sitio", "agregar sitio",
                 "guarda página", "guardar página", "agrega página", "agregar página",
                 "añade sitio", "añadir sitio"]:
        if text.startswith(word):
            return {"intent": "add_site", "query": text.replace(word, "", 1).strip()}

    # ── Abrir sitio ───────────────────────────────────────────────────────────
    for word in ["abre sitio", "abrir sitio", "abre página", "abre pagina",
                 "abrir página", "abrir pagina"]:
        if text.startswith(word):
            return {"intent": "open_site", "query": text.replace(word, "", 1).strip()}

    # ── Media ────────────────────────────────────────────────────────────────
    media_commands = {
        "pausa": "play_pause", "pausa la música": "play_pause",
        "pausar música": "play_pause", "reanuda": "play_pause",
        "reanuda la música": "play_pause", "continua": "play_pause",
        "continúa": "play_pause", "sigue": "play_pause",
        "siguiente": "next", "siguiente canción": "next",
        "pasa canción": "next", "cambia canción": "next",
        "anterior": "previous", "canción anterior": "previous",
        "regresa canción": "previous", "devuelve canción": "previous",
        "sube volumen": "volume_up", "subir volumen": "volume_up",
        "más volumen": "volume_up",
        "baja volumen": "volume_down", "bajar volumen": "volume_down",
        "menos volumen": "volume_down",
        "silencia": "mute", "silencio": "mute",
        "mute": "mute", "quita volumen": "mute",
    }
    for phrase, action in media_commands.items():
        if text.startswith(phrase):
            return {"intent": "media_control", "query": action}

    # ── Música ────────────────────────────────────────────────────────────────
    for word in ["pon música", "poner música", "busca música",
                 "busca cancion", "busca canción",
                 "pon", "pone", "reproduce", "toca"]:
        if text.startswith(word):
            query = text.replace(word, "", 1).strip()
            query = query.replace("en youtube music", "").replace("en youtube", "").strip()
            return {"intent": "play_music", "query": query}

    # ── Archivos ──────────────────────────────────────────────────────────────
    for word in ["lee archivo", "leer archivo", "busca en archivo",
                 "buscar en archivo", "haz backup de archivo",
                 "hacer backup de archivo", "reemplaza", "reemplazar"]:
        if text.startswith(word):
            return {"intent": "file_action", "query": text}

    # ── Modos ─────────────────────────────────────────────────────────────────
    for word in ["edita modo", "editar modo", "modifica modo",
                 "modificar modo", "cambia modo", "cambiar modo"]:
        if text.startswith(word):
            return {"intent": "edit_mode", "query": text.replace(word, "", 1).strip()}

    for word in ["elimina modo", "eliminar modo", "borra modo",
                 "borrar modo", "quita modo", "quitar modo"]:
        if text.startswith(word):
            return {"intent": "delete_mode", "query": text.replace(word, "", 1).strip()}

    for word in ["crea modo", "crear modo", "agrega modo", "agregar modo", "nuevo modo"]:
        if text.startswith(word):
            return {"intent": "create_mode", "query": text.replace(word, "", 1).strip()}

    if text in ["modos", "lista modos", "ver modos", "mostrar modos"]:
        return {"intent": "list_modes", "query": ""}

    for word in ["activa modo", "activar modo", "modo"]:
        if text.startswith(word):
            return {"intent": "activate_mode", "query": text.replace(word, "", 1).strip()}

    # ── Buscar ────────────────────────────────────────────────────────────────
    for word in ["busca", "buscar", "googlea", "investiga"]:
        if text.startswith(word):
            query = text.replace(word, "", 1).strip()
            if query.startswith("en google"):
                query = query.replace("en google", "", 1).strip()
            return {"intent": "web_search", "query": query}

    # ── Abrir ─────────────────────────────────────────────────────────────────
    folder_words = {
        "descargas", "downloads", "documentos", "documents",
        "escritorio", "desktop", "imágenes", "imagenes",
        "pictures", "videos", "música", "musica", "music",
    }
    for word in ["abre", "abrí", "abrir", "abreme", "ábreme", "ejecuta", "lanza"]:
        if text.startswith(word):
            query = text.replace(word, "", 1).strip()
            return {"intent": "open_folder" if query in folder_words else "open_app", "query": query}

    return {"intent": "chat", "query": text}
