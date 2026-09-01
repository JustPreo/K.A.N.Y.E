import os
import signal
import sys
import threading
import time
from pathlib import Path

from core.app_resolver import scan_apps
from core.mode_actions import create_mode_interactive, delete_mode, edit_mode_interactive
from core.text_to_speech import speak
from core import agent
from core.text_normalizer import normalize_text
from core.hotkey_listener import wait_for_hotkey
from core.speech_to_text import listen_once, set_calibrated_threshold
from core.config_loader import get_config
from core.startup_checks import run_checks
from core.mic_calibrator import calibrate
import core.tray_icon as tray
import core.ambient as ambient
import core.system_monitor as monitor
import core.focus_mode as focus
import core.gui as gui


TEXT_MODE = "--text" in sys.argv
HIDDEN_START = "--hidden" in sys.argv   # usado por el autostart de Hyprland


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


def handle_chat(query: str) -> bool:
    tray.set_state("processing")
    answer = agent.run(query)
    print(f"K.A.N.Y.E.: {answer}\n")
    say(answer, cache=False)
    tray.set_state("idle")
    return True


def handle_command(command: str) -> bool:
    """Comandos de housekeeping instantáneo y los wizards de modo (que
    piden varios input() interactivos, así que no encajan en un solo tool
    call) se resuelven acá sin pasar por el LLM. Todo lo demás va al loop
    agéntico (core/agent.py), que decide solo qué herramientas usar."""
    text = command.lower().strip()

    if text in ["salir", "cerrar", "exit", "quit"]:
        say("Cerrando.")
        return False

    if text in ["borra historial", "borrar historial", "limpia historial",
                "limpiar historial", "olvida la conversación", "nueva conversación"]:
        agent.clear_history()
        say("Historial borrado.")
        print()
        return True

    for prefix in ["crea modo", "crear modo", "creá modo", "nuevo modo"]:
        if text.startswith(prefix):
            name = command[len(prefix):].strip()
            say("Modo creado." if create_mode_interactive(name) else "No se creó el modo.")
            print()
            return True

    for prefix in ["edita modo", "editar modo", "editá modo", "modifica modo", "modificar modo"]:
        if text.startswith(prefix):
            name = command[len(prefix):].strip()
            say("Modo editado." if edit_mode_interactive(name) else "No se editó el modo.")
            print()
            return True

    for prefix in ["elimina modo", "eliminar modo", "eliminá modo", "borra modo", "borrar modo"]:
        if text.startswith(prefix):
            name = command[len(prefix):].strip()
            say("Modo eliminado." if delete_mode(name) else "No se eliminó el modo.")
            print()
            return True

    return handle_chat(command)


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


def run_voice_mode(hotkey: str, start_visible: bool = False) -> None:
    running = True
    visible = start_visible
    while running:
        tray.set_state("idle")
        if not visible:
            gui.hide()
        print(f"Estado: esperando [{hotkey.upper()}]...")
        wait_for_hotkey(hotkey)
        gui.show()

        auto_listen = get_config().get("auto_listen_on_hotkey", True)
        if not auto_listen and not visible:
            # Primera pulsación con auto-listen desactivado: solo abre la
            # ventana. Escucha recién con la próxima pulsación o el botón.
            visible = True
            continue

        visible = False
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
        gui.start(start_hidden=HIDDEN_START)

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

    if config.get("startup_tts", True):
        speak("KANYE iniciado.", use_cache=True)
    gui.add_system("Sistema listo. Presioná el botón o Ctrl+F9 para hablar.")

    if TEXT_MODE:
        run_text_mode()
    else:
        run_voice_mode(hotkey, start_visible=not HIDDEN_START)


if __name__ == "__main__":
    main()
