import sys

from core.intent_router import detect_intent
from core.app_resolver import find_best_app_match, scan_apps
from core.system_actions import open_application
from core.web_search import search_google
from core.folder_actions import open_folder
from core.mode_actions import (
    activate_mode, create_mode_interactive,
    list_modes, delete_mode, edit_mode_interactive,
)
from core.text_to_speech import speak
from core.local_llm import ask_llm, clear_history
from core.text_normalizer import normalize_text
from core.hotkey_listener import wait_for_hotkey
from core.speech_to_text import listen_once, set_calibrated_threshold
from core.llm_intent import classify_with_llm
from core.file_actions import read_file, search_in_file, backup_file, replace_in_file
from core.music_actions import play_on_youtube_music
from core.media_actions import (
    media_play_pause, media_next, media_previous,
    volume_up, volume_down, volume_mute,
)
from core.process_actions import close_application
from core.site_actions import open_site, add_site
from core.responses import response
from core.config_loader import get_config
from core.startup_checks import run_checks
from core.mic_calibrator import calibrate
import core.tray_icon as tray


LAST_INTERACTION = {"type": None}
TEXT_MODE = "--text" in sys.argv


def set_last_interaction(t: str) -> None:
    LAST_INTERACTION["type"] = t


def say(message: str) -> None:
    print(f"K.A.N.Y.E.: {message}")
    tray.set_state("speaking")
    speak(message, use_cache=True)
    tray.set_state("idle")


def is_clear_system_command(command: str) -> bool:
    text = command.lower().strip()
    starters = [
        "abre sitio", "abrir sitio", "abre página", "abre pagina",
        "abrir página", "abrir pagina",
        "guarda sitio", "guardar sitio", "agrega sitio", "agregar sitio",
        "guarda página", "guardar página", "agrega página", "agregar página",
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
        "borra historial", "borrar historial", "limpia historial",
        "salir", "cerrar", "exit", "quit",
    ]
    return any(text.startswith(s) for s in starters)


def handle_chat(query: str) -> bool:
    print(f"K.A.N.Y.E.: Conversando: {query}")
    tray.set_state("processing")
    answer = ask_llm(query)
    print(f"K.A.N.Y.E.: {answer}\n")
    tray.set_state("speaking")
    speak(answer, use_cache=False)
    tray.set_state("idle")
    set_last_interaction("chat")
    return True


def handle_media_control(action: str) -> bool:
    handlers = {
        "play_pause": (media_play_pause, "Listo.", "No pude pausar o reanudar."),
        "next":       (media_next,       "Siguiente canción.", "No pude pasar la canción."),
        "previous":   (media_previous,   "Canción anterior.", "No pude regresar la canción."),
        "volume_up":  (volume_up,        "Subiendo volumen.", "No pude subir el volumen."),
        "volume_down":(volume_down,      "Bajando volumen.", "No pude bajar el volumen."),
        "mute":       (volume_mute,      "Silencio.", "No pude silenciar."),
    }
    if action not in handlers:
        say("No entendí el control multimedia.")
        set_last_interaction("command")
        return True

    fn, ok_msg, fail_msg = handlers[action]
    say(ok_msg if fn() else fail_msg)
    print()
    set_last_interaction("command")
    return True


def _listen_for_url() -> str:
    """Escucha una segunda respuesta de voz o texto para la URL."""
    if TEXT_MODE:
        return input("  URL: ").strip()

    say("¿Cuál es la URL?")
    tray.set_state("listening")
    url_raw = listen_once(timeout=6, phrase_time_limit=8)
    tray.set_state("processing")
    return url_raw


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

    for prefix in ["lee archivo", "leer archivo"]:
        if text.startswith(prefix):
            file_path = query[len(prefix):].strip()
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

    for prefix in ["haz backup de archivo", "hacer backup de archivo"]:
        if text.startswith(prefix):
            file_path = query[len(prefix):].strip()
            done = backup_file(file_path, workspace)
            say("Backup creado." if done else "No pude crear el backup.")
            set_last_interaction("command")
            return True

    for prefix in ["busca en archivo", "buscar en archivo"]:
        if text.startswith(prefix):
            rest = query[len(prefix):].strip()
            if " el texto " not in rest:
                say("Usa el formato: busca en archivo main.py el texto KANYE.")
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
        intent, query = "chat_direct", command
    else:
        result = detect_intent(command)
        intent, query = result["intent"], result["query"]

    tray.set_state("processing")

    # ── Salir ─────────────────────────────────────────────────────────────────
    if intent == "exit":
        say("Cerrando.")
        return False

    # ── Borrar historial ──────────────────────────────────────────────────────
    elif intent == "clear_history":
        clear_history()
        say("Historial borrado.")
        print()
        set_last_interaction("command")

    # ── Abrir app ─────────────────────────────────────────────────────────────
    elif intent == "open_app":
        print(f"K.A.N.Y.E.: Buscando app: {query}")
        if open_site(query):
            say(f"Abriendo {query}.")
        else:
            app = find_best_app_match(query)
            if not app:
                say(response("app_not_found"))
            elif open_application(app):
                say(response("app_opened", name=app["name"]))
            else:
                say("Encontré la app, pero no pude abrirla.")
        print()
        set_last_interaction("command")

    # ── Cerrar app ────────────────────────────────────────────────────────────
    elif intent == "close_app":
        if not query:
            say("Decime qué programa querés cerrar.")
            set_last_interaction("command")
            return True
        if close_application(query):
            say(response("app_closed", name=query))
        else:
            say("No encontré ese programa abierto o no pude cerrarlo.")
        print()
        set_last_interaction("command")

    # ── Buscar en Google ──────────────────────────────────────────────────────
    elif intent == "web_search":
        print(f"K.A.N.Y.E.: Buscando: {query}")
        say(response("search_opened") if search_google(query) else "No pude hacer la búsqueda.")
        print()
        set_last_interaction("command")

    # ── Carpetas ──────────────────────────────────────────────────────────────
    elif intent == "open_folder":
        say(response("folder_opened") if open_folder(query) else "No pude abrir esa carpeta.")
        print()
        set_last_interaction("command")

    # ── Modos ─────────────────────────────────────────────────────────────────
    elif intent == "activate_mode":
        if not query:
            say("Decime qué modo querés activar.")
            set_last_interaction("command")
            return True
        say(response("mode_activated", name=query) if activate_mode(query) else "No pude activar ese modo.")
        print()
        set_last_interaction("command")

    elif intent == "create_mode":
        if not query:
            say("Decime el nombre del modo.")
            set_last_interaction("command")
            return True
        say("Modo creado correctamente." if create_mode_interactive(query) else "No se creó el modo.")
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
            set_last_interaction("command")
            return True
        say("Modo eliminado." if delete_mode(query) else "No se eliminó el modo.")
        print()
        set_last_interaction("command")

    elif intent == "edit_mode":
        if not query:
            say("Decime qué modo querés editar.")
            set_last_interaction("command")
            return True
        say("Modo editado." if edit_mode_interactive(query) else "No se editó el modo.")
        print()
        set_last_interaction("command")

    # ── Música ────────────────────────────────────────────────────────────────
    elif intent == "play_music":
        if not query:
            say("Decime qué canción querés escuchar.")
            set_last_interaction("command")
            return True
        print(f"K.A.N.Y.E.: Buscando en YouTube Music: {query}")
        play_on_youtube_music(query)
        say(response("music_playing", name=query))
        print()
        set_last_interaction("command")

    # ── Media control ─────────────────────────────────────────────────────────
    elif intent == "media_control":
        return handle_media_control(query)

    # ── Archivos ──────────────────────────────────────────────────────────────
    elif intent == "file_action":
        return handle_file_action(query)

    # ── Chat directo (venía de conversación) ──────────────────────────────────
    elif intent == "chat_direct":
        return handle_chat(query)

    # ── Abrir sitio guardado ──────────────────────────────────────────────────
    elif intent == "open_site":
        if not query:
            say("Decime qué página querés abrir.")
            set_last_interaction("command")
            return True
        if open_site(query):
            say(response("site_opened", name=query))
        else:
            say("No encontré esa página guardada.")
        print()
        set_last_interaction("command")

    # ── Guardar sitio nuevo por voz ───────────────────────────────────────────
    elif intent == "add_site":
        if not query:
            say("Decime el nombre del sitio que querés guardar.")
            set_last_interaction("command")
            return True

        url_raw = _listen_for_url()

        if not url_raw:
            say("No escuché la URL.")
            set_last_interaction("command")
            return True

        if add_site(query, url_raw):
            say(f"Sitio '{query}' guardado.")
        else:
            say("No pude guardar el sitio.")
        print()
        set_last_interaction("command")

    # ── Chat / intención ambigua (con LLM opcional) ───────────────────────────
    elif intent == "chat":
        config = get_config()
        if config.get("use_llm_classifier", True):
            print(f"K.A.N.Y.E.: Analizando con LLM: {query}")
            llm = classify_with_llm(query)
            llm_intent, llm_query = llm["intent"], llm["query"]
            print(f"K.A.N.Y.E.: LLM → {llm_intent} | {llm_query}")

            dispatch = {
                "activate_mode": f"activa modo {llm_query}",
                "open_app":      f"abre {llm_query}",
                "close_app":     f"cierra {llm_query}",
                "open_folder":   f"abre {llm_query}",
                "web_search":    f"busca {llm_query}",
                "play_music":    f"pon {llm_query}",
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

    tray.set_state("idle")
    return True


# ─── Bucles de ejecución ──────────────────────────────────────────────────────

def _listen_command() -> str:
    """Obtiene el próximo comando (voz o texto según modo)."""
    if TEXT_MODE:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            return "salir"
        return normalize_text(raw)

    tray.set_state("listening")
    command = listen_once(timeout=6, phrase_time_limit=10)
    tray.set_state("processing")

    if not command:
        say("No escuché nada.")
        tray.set_state("idle")
        return ""

    command = normalize_text(command)
    print(f"Comando detectado: {command}")
    return command


def run_voice_mode(config: dict) -> None:
    hotkey = config.get("hotkey", "ctrl+f9")
    running = True

    while running:
        tray.set_state("idle")
        print(f"Estado: esperando [{hotkey.upper()}]...")
        wait_for_hotkey(hotkey)

        say("Te escucho.")
        command = _listen_command()

        if not command:
            continue

        running = handle_command(command)


def run_text_mode() -> None:
    print("K.A.N.Y.E. modo texto. Escribí tu comando (o 'salir' para cerrar).\n")
    running = True
    while running:
        command = _listen_command()
        if command:
            running = handle_command(command)


def main() -> None:
    config = get_config()

    print("=" * 45)
    print("  K.A.N.Y.E.")
    if TEXT_MODE:
        print("  Modo: TEXTO (--text)")
    else:
        hotkey = config.get("hotkey", "ctrl+f9")
        print(f"  Modo: VOZ  |  Hotkey: [{hotkey.upper()}]")
    print("=" * 45 + "\n")

    # Verificaciones de sistema
    run_checks()

    # Calentar cache de apps en background
    import threading
    threading.Thread(target=scan_apps, daemon=True).start()

    if not TEXT_MODE:
        # Bandeja del sistema
        tray.start(on_quit=lambda: sys.exit(0))

        # Calibrar micrófono
        print("K.A.N.Y.E.: Calibrando micrófono (hablar en silencio)...")
        threshold = calibrate(duration=1.2)
        set_calibrated_threshold(threshold)

    speak("KANYE iniciado.", use_cache=True)

    if TEXT_MODE:
        run_text_mode()
    else:
        run_voice_mode(config)


if __name__ == "__main__":
    main()
