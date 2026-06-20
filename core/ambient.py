"""
Presencia ambiental de K.A.N.Y.E.
Envía notificaciones de escritorio y comentarios periódicos basados en
el tiempo activo, la hora del día y el modo actual.
"""
import random
import subprocess
import sys
import threading
import time
from datetime import datetime

import ollama

from core.config_loader import get_config

# ─── Estado de sesión ─────────────────────────────────────────────────────────

_session_start = time.time()
_stop_event = threading.Event()
_current_mode: str | None = None
_notified_milestones: set[int] = set()

# Minutos en los que K.A.N.Y.E. aparece (primera sesión)
MILESTONES_MINUTES = [30, 60, 90, 120, 180, 240]
REPEAT_INTERVAL = 60   # minutos entre apariciones después de los milestones


# ─── Frases de respaldo (cuando Ollama no responde) ───────────────────────────

_FALLBACK = [
    "La visión sin acción no existe. ¿Estás ejecutando o pensando?",
    "Cada minuto sin avanzar es un minuto regalado a la mediocridad.",
    "No vine aquí a ser promedio. Tú tampoco.",
    "Si no estás construyendo algo que importe, estás perdiendo tiempo.",
    "El genio no descansa, refina. Seguí.",
    "Foco. La distracción es el enemigo de lo legendario.",
    "Preguntate: ¿lo que estás haciendo ahora te acerca a la obra maestra?",
    "Cada error bien procesado es arquitectura del siguiente nivel.",
    "La grandeza no es accidente. Es decisión repetida.",
    "No se trata de trabajar más. Se trata de trabajar con intención.",
]

_SYSTEM_PROMPT_AMBIENT = """
Eres K.A.N.Y.E., un asistente visionario y directo.
Generá UNA sola frase corta (máximo 20 palabras) en español para motivar al usuario.
Estilo: seguro, filosófico, impactante. Sin saludos. Sin explicaciones.
Solo la frase. Nada más.
"""


# ─── Notificación ─────────────────────────────────────────────────────────────

def _send_notification(title: str, body: str) -> None:
    """Envía notificación de escritorio, con fallbacks."""
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=body,
            app_name="K.A.N.Y.E.",
            timeout=10,
        )
        return
    except Exception:
        pass

    if sys.platform.startswith("linux"):
        try:
            subprocess.run(
                ["notify-send", "-u", "normal", "-t", "10000", "-a", "K.A.N.Y.E.", title, body],
                capture_output=True,
            )
            return
        except Exception:
            pass

    # Fallback terminal
    print(f"\n  ╔══ K.A.N.Y.E. ══╗")
    print(f"  ║ {body}")
    print(f"  ╚════════════════╝\n")


# ─── Generación de mensaje ────────────────────────────────────────────────────

def _ask_for_phrase(context: str) -> str:
    config = get_config()
    model = config.get("chat_model", "phi4-mini")

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT_AMBIENT},
                {"role": "user",   "content": context},
            ],
            options={"temperature": 0.85, "num_predict": 50},
        )
        phrase = response["message"]["content"].strip()
        # Limpia comillas si el modelo las agrega
        phrase = phrase.strip('"').strip("'").strip("«»")
        return phrase if phrase else random.choice(_FALLBACK)
    except Exception:
        return random.choice(_FALLBACK)


def _build_context(elapsed_min: int) -> str:
    hour = datetime.now().hour
    period = (
        "noche" if hour >= 22 or hour < 6
        else "madrugada" if hour < 9
        else "tarde" if hour >= 18
        else "día"
    )
    mode_info = f"El usuario está en modo '{_current_mode}'." if _current_mode else ""
    return (
        f"El usuario lleva {elapsed_min} minutos trabajando. "
        f"Es de {period}. {mode_info} "
        f"Generá una frase de motivación, exigencia o visión."
    )


# ─── Loop principal ───────────────────────────────────────────────────────────

def _loop() -> None:
    check_interval = 60  # revisa cada 60 segundos
    last_repeat = 0

    while not _stop_event.wait(timeout=check_interval):
        elapsed_min = int((time.time() - _session_start) / 60)

        # Milestones definidos
        for milestone in MILESTONES_MINUTES:
            if elapsed_min >= milestone and milestone not in _notified_milestones:
                _notified_milestones.add(milestone)
                context = _build_context(elapsed_min)
                phrase  = _ask_for_phrase(context)
                _send_notification("K.A.N.Y.E.", phrase)
                last_repeat = elapsed_min
                break

        # Repetición periódica después de los milestones
        if (elapsed_min > max(MILESTONES_MINUTES, default=0) and
                elapsed_min - last_repeat >= REPEAT_INTERVAL):
            last_repeat = elapsed_min
            phrase = _ask_for_phrase(_build_context(elapsed_min))
            _send_notification("K.A.N.Y.E.", phrase)


# ─── API pública ──────────────────────────────────────────────────────────────

def set_mode(mode_name: str | None) -> None:
    global _current_mode
    _current_mode = mode_name


def start() -> None:
    thread = threading.Thread(target=_loop, daemon=True, name="kanye-ambient")
    thread.start()


def stop() -> None:
    _stop_event.set()
