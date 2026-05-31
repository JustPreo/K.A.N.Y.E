def normalize_text(text: str) -> str:
    """
    Corrige errores comunes del reconocimiento de voz.
    """
    if not text:
        return ""

    text = text.lower().strip()

    replacements = {
        # NBA / deportes
        "san antonio sports": "san antonio spurs",
        "san antonio esport": "san antonio spurs",
        "san antonio es por": "san antonio spurs",
        "los sports": "los spurs",
        "espurs": "spurs",

        # Wake word
        "kanie": "kanye",
        "kan ye": "kanye",
        "caña": "kanye",
        "canye": "kanye",

        # Apps comunes
        "visual estudio code": "visual studio code",
        "visual studio": "visual studio code",
        "bloc notas": "bloc de notas",
        "block de notas": "bloc de notas",

        # Comandos comunes
        "abrir": "abre",
        "ábreme": "abre",
        "abreme": "abre",
    }

    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)

    return text