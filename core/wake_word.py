from core.speech_to_text import listen_once
from core.text_normalizer import normalize_text

WAKE_WORDS = [
    "kanye",
    "kanie",
    "kan ye",
    "caña",
    "canye",
    "calle",
    "kanji"
]


def contains_wake_word(text: str) -> bool:
    """
    Revisa si el texto contiene alguna variante aceptada de la palabra de activación.
    """
    normalized_text = normalize_text(text)

    return any(wake_word in normalized_text for wake_word in WAKE_WORDS)


def remove_wake_word(text: str) -> str:
    """
    Quita la palabra de activación si el usuario dijo el comando en una sola frase.

    Ejemplo:
    - "kanye abre youtube" -> "abre youtube"
    - "oye kanye abre youtube" -> "abre youtube"
    """
    normalized_text = normalize_text(text)

    for wake_word in WAKE_WORDS:
        if normalized_text.startswith(wake_word):
            return normalized_text.replace(wake_word, "", 1).strip()

        marker = f" {wake_word} "
        if marker in normalized_text:
            return normalized_text.split(marker, 1)[1].strip()

    return ""


def wait_for_wake_word(timeout: int = 4, phrase_time_limit: int = 4) -> str:
    """
    Escucha frases cortas hasta detectar la palabra de activación.
    Devuelve el texto escuchado cuando detecta la palabra.
    """
    heard_text = listen_once(timeout=timeout, phrase_time_limit=phrase_time_limit)

    if not heard_text:
        return ""

    heard_text = normalize_text(heard_text)

    if contains_wake_word(heard_text):
        return heard_text

    return ""


def listen_command_after_wake(timeout: int = 6, phrase_time_limit: int = 10) -> str:
    """
    Escucha la orden después de que el asistente ya despertó.
    """
    command = listen_once(timeout=timeout, phrase_time_limit=phrase_time_limit)

    if not command:
        return ""

    return normalize_text(command)
