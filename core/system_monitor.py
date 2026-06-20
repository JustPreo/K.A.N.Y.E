"""
Monitor del sistema con personalidad de K.A.N.Y.E.
Vigila CPU, RAM y batería. Cuando algo está mal, lo dice.
"""
import random
import threading
import time

import psutil
import ollama

from core.config_loader import get_config

_stop_event = threading.Event()

# Cuándo se envió la última alerta por métrica (epoch)
_last_alert: dict[str, float] = {"cpu": 0, "ram": 0, "battery": 0}
_cpu_high_since: float = 0.0

COOLDOWN = {
    "cpu":     300,   # 5 min
    "ram":     600,   # 10 min
    "battery": 900,   # 15 min
}

THRESHOLDS = {
    "cpu":      85,   # %
    "ram":      90,   # %
    "battery":  15,   # %
    "cpu_secs": 60,   # segundos continuos antes de alertar
}

_SYSTEM_PROMPT = """
Eres K.A.N.Y.E., asistente visionario y directo.
Generá UNA sola frase corta (máximo 25 palabras) comentando el problema de sistema indicado.
Estilo: directo, irónico, exigente. Sin tecnicismos innecesarios. Solo la frase, nada más.
"""

_FALLBACKS = {
    "cpu":     [
        "Tu CPU está en llamas. Eso no es productividad, eso es caos. Cerrá algo.",
        "El procesador está gritando. Menos tabs, más foco.",
        "CPU al límite. La mediocridad consume recursos. Limpiá el escritorio.",
    ],
    "ram":     [
        "La RAM está llena. Como una mente sin orden: todo ruido, nada de señal.",
        "Memoria saturada. Cerrá lo que no sirve, igual que en la vida.",
        "Sin RAM libre no hay visión clara. Libera espacio.",
    ],
    "battery": [
        "Batería crítica. Si se apaga, perdés el momentum. Conectá ahora.",
        "Menos del 15% de batería. La energía es todo. Conectate.",
        "La batería se muere. Igual que los proyectos sin ejecución. Conectá.",
    ],
}

# Función para notificar (importada al usar para evitar circular import)
_speak_fn = None
_notify_fn = None


def set_speak(fn) -> None:
    global _speak_fn
    _speak_fn = fn


def set_notify(fn) -> None:
    global _notify_fn
    _notify_fn = fn


def _alert(metric: str, stat_info: str) -> None:
    now = time.time()
    if now - _last_alert[metric] < COOLDOWN[metric]:
        return
    _last_alert[metric] = now

    phrase = _generate_comment(metric, stat_info)

    print(f"\nK.A.N.Y.E. [sistema]: {phrase}\n")

    if _notify_fn:
        _notify_fn("K.A.N.Y.E. — Sistema", phrase)

    if _speak_fn:
        _speak_fn(phrase, use_cache=False)


def _generate_comment(metric: str, stat_info: str) -> str:
    config = get_config()
    model  = config.get("chat_model", "phi4-mini")
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user",   "content": f"Problema: {stat_info}"},
            ],
            options={"temperature": 0.75, "num_predict": 60},
        )
        phrase = response["message"]["content"].strip().strip('"\'«»')
        return phrase if phrase else random.choice(_FALLBACKS[metric])
    except Exception:
        return random.choice(_FALLBACKS[metric])


def _check_cpu() -> None:
    global _cpu_high_since
    usage = psutil.cpu_percent(interval=1)
    if usage >= THRESHOLDS["cpu"]:
        if _cpu_high_since == 0:
            _cpu_high_since = time.time()
        elif time.time() - _cpu_high_since >= THRESHOLDS["cpu_secs"]:
            _cpu_high_since = 0
            _alert("cpu", f"CPU al {usage:.0f}% durante más de un minuto")
    else:
        _cpu_high_since = 0


def _check_ram() -> None:
    ram = psutil.virtual_memory()
    if ram.percent >= THRESHOLDS["ram"]:
        free_mb = ram.available // (1024 ** 2)
        _alert("ram", f"RAM al {ram.percent:.0f}% — solo {free_mb} MB libres")


def _check_battery() -> None:
    battery = psutil.sensors_battery()
    if battery and not battery.power_plugged and battery.percent <= THRESHOLDS["battery"]:
        _alert("battery", f"Batería al {battery.percent:.0f}% y sin cargador conectado")


def _loop() -> None:
    while not _stop_event.wait(timeout=30):
        try:
            _check_cpu()
            _check_ram()
            _check_battery()
        except Exception as error:
            print(f"K.A.N.Y.E. [monitor]: error — {error}")


def start() -> None:
    thread = threading.Thread(target=_loop, daemon=True, name="kanye-monitor")
    thread.start()


def stop() -> None:
    _stop_event.set()
