import os
import signal
import sys
import threading
from pathlib import Path

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
from core.keyboard_actions import type_text, execute_shortcut
from core.responses import response
from core.config_loader import get_config
from core.startup_checks import run_checks
from core.mic_calibrator import calibrate
import core.tray_icon as tray
import core.ambient as ambient
import core.system_monitor as monitor
import core.focus_mode as focus
import core.gui as gui


LAST_INTERACTION = {"type": None}
TEXT_MODE = "--text" in sys.argv


def set_last_interaction(t: str) -> None:
    LAST_INTERACTION["type"] = t


# ─── Notificación compartida (inyectada en monitor y focus) ───────────────────

def _notify(title: str, body: str) -> None:
    try:
        from plyer import notification
        notification.notify(title=title, message=body, app_name="K.A.N.Y.E.", timeout=10)
        return
    except Exception:
        pass
    import subprocess
    if sys.platform.startswith("linux"):
        try:
            subprocess.run(
                ["notify-send", "-u", "normal", "-t", "10000", "-a", "K.A.N.Y.E.", title, body],
                capture_output=True,
            )
            return
        except Exception:
            pass
    print(f"\n  ╔══ {title} ══╗\n  ║ {body}\n  ╚{'═' * (len(title) + 6)}╝\n")


def say(message: str, cache: bool = True) -> None:
    print(f"K.A.N.Y.E.: {message}")
    tray.set_state("speaking")
    gui.set_state("speaking")
    gui.add_kanye(message)
    speak(message, use_cache=cache)
    tray.set_state("idle")
    gui.set_state("idle")


def is_clear_system_command(command: str) -> bool:
    text = command.lower().strip()
    starters = [
        "abre sitio", "abrir sitio", "abre página", "abre pagina",
        "abrir página", "abrir pagina",
        "guarda sitio", "guardar sitio", "agrega sitio", "agregar sitio",
        "guarda página", "guardar página", "agrega página", "agregar página",
        "cierra", "cerrar", "cerrá", "termina", "terminar", "mata",
        "pon", "pone", "reproduce", "toca", "pon música", "poner música",
        "busca música", "busca cancion", "busca canción",
        "abre", "abrí", "abrir", "ejecuta", "lanza",
        "busca", "buscar", "googlea", "investiga",
        "activa modo", "activar modo", "modo",
        "crea modo", "crear modo", "nuevo modo",
        "edita modo", "editar modo", "modifica modo",
        "elimina modo", "eliminar modo", "borra modo",
        "modos", "lista modos", "ver modos",
        "borra historial", "borrar historial",
        "desbloquea", "desbloquear", "desactiva focus",
        "escribe", "escribí", "escribir", "dictá", "tipea", "teclea",
        "presiona", "selecciona todo", "copia", "pega", "corta",
        "deshace", "rehace", "guarda el archivo",
        "salir", "exit", "quit",
    ]
    return any(text.startswith(s) for s in starters)


def handle_chat(query: str) -> bool:
    print(f"K.A.N.Y.E.: Conversando: {query}")
    tray.set_state("processing")
    answer = ask_llm(query)
    print(f"K.A.N.Y.E.: {answer}\n")
    say(answer, cache=False)
    set_last_interaction("chat")
    return True


def handle_media_control(action: str) -> bool:
    handlers = {
        "play_pause": (media_play_pause, "Listo.",           "No pude pausar o reanudar."),
        "next":       (media_next,       "Siguiente canción.", "No pude pasar la canción."),
        "previous":   (media_previous,   "Canción anterior.", "No pude regresar la canción."),
        "volume_up":  (volume_up,        "Subiendo volumen.", "No pude subir el volumen."),
        "volume_down":(volume_down,      "Bajando volumen.", "No pude bajar el volumen."),
        "mute":       (volume_mute,      "Silencio.",        "No pude silenciar."),
    }
    if action not in handlers:
        say("No entendí el control multimedia.")
    else:
        fn, ok_msg, fail_msg = handlers[action]
        say(ok_msg if fn() else fail_msg)
    print()
    set_last_interaction("command")
    return True


def _listen_follow_up(prompt: str) -> str:
    """Escucha una respuesta de seguimiento (voz o texto)."""
    say(prompt)
    if TEXT_MODE:
        return input("  > ").strip()
    tray.set_state("listening")
    result = listen_once(timeout=6, phrase_time_limit=8)
    tray.set_state("processing")
    return result


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
            content = read_file(query[len(prefix):].strip(), workspace)
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
            done = backup_file(query[len(prefix):].strip(), workspace)
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
            say("Usa: reemplaza texto viejo por texto nuevo en archivo main.py.")
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
        extra: dict = {}
    else:
        result  = detect_intent(command)
        intent  = result["intent"]
        query   = result["query"]
        extra   = {k: v for k, v in result.items() if k not in ("intent", "query")}

    tray.set_state("processing")

    # ── Salir ─────────────────────────────────────────────────────────────────
    if intent == "exit":
        say("Cerrando.")
        return False

    # ── Historial ─────────────────────────────────────────────────────────────
    elif intent == "clear_history":
        clear_history()
        say("Historial borrado.")
        print()
        set_last_interaction("command")

    # ── Teclado — shortcut ────────────────────────────────────────────────────
    elif intent == "keyboard_shortcut":
        done = execute_shortcut(query)
        say("Listo." if done else "No pude ejecutar ese atajo.")
        print()
        set_last_interaction("command")

    # ── Teclado — escribir texto ──────────────────────────────────────────────
    elif intent == "keyboard_type":
        if not query:
            say("¿Qué quieres que escriba?")
            set_last_interaction("command")
            return True
        uppercase = extra.get("uppercase", False)
        done = type_text(query, uppercase=uppercase)
        say("Texto escrito." if done else "No pude escribir el texto.")
        print()
        set_last_interaction("command")

    # ── Focus OFF ─────────────────────────────────────────────────────────────
    elif intent == "focus_off":
        if not focus.is_active():
            say("No hay ningún modo focus activo.")
            set_last_interaction("command")
            return True

        focus.deactivate(forced=True)
        say("Focus desactivado.")
        print()
        set_last_interaction("command")

    # ── Focus STATUS ──────────────────────────────────────────────────────────
    elif intent == "focus_status":
        info = focus.time_info()
        say(info)
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
        say(response("app_closed", name=query) if close_application(query)
            else "No encontré ese programa abierto o no pude cerrarlo.")
        print()
        set_last_interaction("command")

    # ── Buscar ────────────────────────────────────────────────────────────────
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
        result = activate_mode(query)
        say(result if result else "No pude activar ese modo.")
        print()
        set_last_interaction("command")

    elif intent == "create_mode":
        if not query:
            say("Decime el nombre del modo.")
            set_last_interaction("command")
            return True
        say("Modo creado." if create_mode_interactive(query) else "No se creó el modo.")
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
        say(f"Buscando {query} en YouTube Music.")
        play_on_youtube_music(query)
        print()
        set_last_interaction("command")

    # ── Media control ─────────────────────────────────────────────────────────
    elif intent == "media_control":
        return handle_media_control(query)

    # ── Archivos ──────────────────────────────────────────────────────────────
    elif intent == "file_action":
        return handle_file_action(query)

    # ── Chat directo ──────────────────────────────────────────────────────────
    elif intent == "chat_direct":
        return handle_chat(query)

    # ── Sitios ────────────────────────────────────────────────────────────────
    elif intent == "open_site":
        if not query:
            say("Decime qué página querés abrir.")
            set_last_interaction("command")
            return True
        say(response("site_opened", name=query) if open_site(query)
            else "No encontré esa página guardada.")
        print()
        set_last_interaction("command")

    elif intent == "add_site":
        if not query:
            say("Decime el nombre del sitio.")
            set_last_interaction("command")
            return True
        url_raw = _listen_follow_up(f"¿Cuál es la URL de {query}?")
        if not url_raw:
            say("No escuché la URL.")
            set_last_interaction("command")
            return True
        say(f"Sitio '{query}' guardado." if add_site(query, url_raw)
            else "No pude guardar el sitio.")
        print()
        set_last_interaction("command")

    # ── Chat / ambiguo ────────────────────────────────────────────────────────
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


# ─── Bucles ───────────────────────────────────────────────────────────────────

def _get_command() -> str:
    if TEXT_MODE:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            return "salir"
        return normalize_text(raw)

    tray.set_state("listening")
    gui.set_state("listening")
    cmd = listen_once(timeout=6, phrase_time_limit=10)
    tray.set_state("processing")
    gui.set_state("processing")

    if not cmd:
        say("No escuché nada.")
        tray.set_state("idle")
        gui.set_state("idle")
        return ""

    cmd = normalize_text(cmd)
    print(f"Comando detectado: {cmd}")
    gui.add_user(cmd)
    return cmd


def run_voice_mode(hotkey: str) -> None:
    running = True
    while running:
        tray.set_state("idle")
        print(f"Estado: esperando [{hotkey.upper()}]...")
        wait_for_hotkey(hotkey)
        say("Te escucho.")
        cmd = _get_command()
        if cmd:
            running = handle_command(cmd)


def run_text_mode() -> None:
    print("K.A.N.Y.E. modo texto. Escribí tu comando (o 'salir' para cerrar).\n")
    running = True
    while running:
        cmd = _get_command()
        if cmd:
            running = handle_command(cmd)


# ─── Inicio ───────────────────────────────────────────────────────────────────

PID_FILE = Path("/tmp/kanye.pid") if sys.platform != "win32" else Path("kanye.pid")


def _check_single_instance() -> None:
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text())
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.5)
        except Exception:
            pass
    PID_FILE.write_text(str(os.getpid()))


def _cleanup_pid() -> None:
    try:
        PID_FILE.unlink(missing_ok=True)
    except Exception:
        pass
    try:
        from core.media_player import stop
        stop()
    except Exception:
        pass


def main() -> None:
    import atexit
    _check_single_instance()
    atexit.register(_cleanup_pid)

    config = get_config()
    hotkey = config.get("hotkey", "ctrl+f9")

    print("=" * 45)
    print("  K.A.N.Y.E.")
    print(f"  Modo: {'TEXTO (--text)' if TEXT_MODE else f'VOZ  |  [{hotkey.upper()}]'}")
    print("=" * 45 + "\n")

    run_checks()

    # Cache de apps en background
    threading.Thread(target=scan_apps, daemon=True).start()

    # Inyectar callbacks en módulos de fondo
    monitor.set_speak(speak)
    monitor.set_notify(_notify)
    focus.set_callbacks(
        on_expired=None,
        speak=speak,
        notify=_notify,
    )

    if not TEXT_MODE:
        tray.start(on_quit=lambda: sys.exit(0))
        gui.start()

        print("K.A.N.Y.E.: Calibrando micrófono...")
        set_calibrated_threshold(calibrate(duration=1.2))

    # Conectar media_player con la GUI
    import core.media_player as _mp
    _mp.set_on_change(gui.set_player_status)

    # Modo teclado: comando escrito en el GUI se procesa igual que voz
    def _on_kb_command(text: str) -> None:
        text = normalize_text(text)
        if text:
            handle_command(text)
    gui.set_kb_callback(_on_kb_command)

    # Inyectar set_mode en mode_actions para que la GUI refleje el modo activo
    import core.mode_actions as _ma
    _orig_activate = _ma.activate_mode
    def _activate_with_gui(name):
        result = _orig_activate(name)
        if result:
            gui.set_mode(name)
            ambient.set_mode(name)
        return result
    _ma.activate_mode = _activate_with_gui

    # Inyectar alertas del monitor en la GUI
    _orig_notify = _notify
    def _notify_with_gui(title, body):
        _orig_notify(title, body)
        gui.add_alert(f"{title}: {body}")
    monitor.set_notify(_notify_with_gui)
    focus.set_callbacks(on_expired=None, speak=speak, notify=_notify_with_gui)

    # Iniciar presencia ambiental y monitor de sistema
    ambient.start()
    monitor.start()

    speak("KANYE iniciado.", use_cache=True)
    gui.add_system("Sistema listo. Presioná el botón o Ctrl+F9 para hablar.")

    if TEXT_MODE:
        run_text_mode()
    else:
        run_voice_mode(hotkey)


if __name__ == "__main__":
    main()
