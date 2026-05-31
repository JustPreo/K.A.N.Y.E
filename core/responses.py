import random


RESPONSES = {
    "startup": [
        "K.A.N.Y.E. iniciado.",
        "Sistema listo.",
        "Listo para trabajar."
    ],

    "done": [
        "Listo.",
        "Hecho.",
        "Ya quedó.",
        "Entendido."
    ],

    "app_opened": [
        "Abriendo {name}.",
        "Listo. Abriendo {name}.",
        "{name} abierto."
    ],

    "app_not_found": [
        "No encontré esa aplicación.",
        "No encontré algo parecido.",
        "No pude encontrar esa app."
    ],

    "app_closed": [
        "Cerrando {name}.",
        "Listo. Cerrando {name}.",
        "{name} cerrado."
    ],

    "site_opened": [
        "Abriendo {name}.",
        "Listo. Abriendo {name}.",
        "Ya te abrí {name}."
    ],

    "music_playing": [
        "Reproduciendo {name}.",
        "Listo. Poniendo {name}.",
        "Buscando {name} en YouTube Music."
    ],

    "mode_activated": [
        "Modo {name} activado.",
        "Listo. Modo {name}.",
        "Activando modo {name}."
    ],

    "folder_opened": [
        "Carpeta abierta.",
        "Listo. Abrí la carpeta.",
        "Ya está abierta."
    ],

    "search_opened": [
        "Búsqueda abierta.",
        "Listo. Buscando eso.",
        "Ya abrí la búsqueda."
    ],

    "not_understood": [
        "No entendí el comando.",
        "No capté eso.",
        "No estoy seguro de qué querés hacer."
    ],

    "error": [
        "No pude hacerlo.",
        "Algo falló.",
        "No logré completar eso."
    ],

    "listening": [
        "Te escucho.",
        "Decime.",
        "Adelante."
    ],

    "closing": [
        "Cerrando.",
        "Apagando sistema.",
        "Nos vemos."
    ]
}


def response(key: str, **kwargs) -> str:
    options = RESPONSES.get(key, ["Listo."])
    selected = random.choice(options)

    try:
        return selected.format(**kwargs)
    except KeyError:
        return selected