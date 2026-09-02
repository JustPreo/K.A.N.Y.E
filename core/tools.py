"""
Catálogo de tools que el agente (core/agent.py) puede invocar, y el
dispatcher que las ejecuta. Cada tool envuelve una función que ya existe
en core/*_actions.py — este módulo no reimplementa nada, solo le pone
un schema de function-calling encima y traduce el resultado a un string
corto que el LLM pueda leer.

Se usa `import core.X as X` (no `from core.X import func`) para que los
monkeypatches que main.py aplica sobre algunos módulos (ej.
mode_actions.activate_mode) sigan teniendo efecto acá.
"""
import json

import core.app_resolver as app_resolver
import core.system_actions as system_actions
import core.process_actions as process_actions
import core.folder_actions as folder_actions
import core.web_search as web_search
import core.music_actions as music_actions
import core.media_actions as media_actions
import core.mode_actions as mode_actions
import core.site_actions as site_actions
import core.file_actions as file_actions
import core.keyboard_actions as keyboard_actions
import core.mouse_actions as mouse_actions
import core.focus_mode as focus_mode
import core.notes_actions as notes_actions
import core.window_actions as window_actions
import core.it_worker as it_worker


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Abre una aplicación instalada en la computadora, o un sitio guardado si el nombre coincide con uno.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Nombre de la app o sitio a abrir, ej. 'firefox', 'spotify'."},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "close_app",
            "description": "Cierra un programa que esté corriendo actualmente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Nombre del proceso/programa a cerrar."},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_folder",
            "description": "Abre una carpeta común del sistema (descargas, documentos, escritorio, imágenes, videos, música).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nombre de la carpeta, ej. 'descargas', 'documentos'."},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Abre una búsqueda de Google en el navegador con el tema pedido.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Qué buscar."},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "play_music",
            "description": "Busca y reproduce una canción o artista en YouTube Music.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Canción, artista o álbum a reproducir."},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "media_control",
            "description": "Controla la reproducción multimedia actual (pausa, siguiente, anterior, volumen).",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["play_pause", "next", "previous", "volume_up", "volume_down", "mute"],
                    },
                },
                "required": ["action"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "activate_mode",
            "description": "Activa un modo de trabajo guardado por el usuario (abre sus apps/urls/carpetas configuradas).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nombre del modo, ej. 'estudio', 'gaming'."},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_modes",
            "description": "Lista los modos de trabajo guardados disponibles.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_site",
            "description": "Abre un sitio web guardado por nombre.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nombre del sitio guardado."},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_site",
            "description": "Guarda un nuevo sitio web con nombre y URL para poder abrirlo después por nombre.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nombre corto para el sitio."},
                    "url": {"type": "string", "description": "URL del sitio, tal como la dijo el usuario."},
                },
                "required": ["name", "url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Lee el contenido de un archivo de texto dentro de un proyecto (workspace) permitido.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Ruta del archivo relativa al proyecto."},
                    "workspace": {"type": "string", "description": "Nombre del proyecto configurado en workspaces.json. Por defecto 'kanye'."},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_in_file",
            "description": "Busca un texto exacto dentro de un archivo de un proyecto permitido.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "text": {"type": "string", "description": "Texto a buscar."},
                    "workspace": {"type": "string"},
                },
                "required": ["path", "text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "backup_file",
            "description": "Crea una copia de respaldo con timestamp de un archivo de un proyecto permitido.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "workspace": {"type": "string"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "replace_in_file",
            "description": "Reemplaza un texto exacto por otro dentro de un archivo de un proyecto permitido. Pide confirmación en la terminal antes de aplicar el cambio y hace backup automático.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old": {"type": "string", "description": "Texto exacto a reemplazar."},
                    "new": {"type": "string", "description": "Texto nuevo."},
                    "workspace": {"type": "string"},
                },
                "required": ["path", "old", "new"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file_path",
            "description": (
                "Lee el contenido de CUALQUIER archivo del sistema por su ruta completa "
                "(no solo dentro de un proyecto configurado). La primera vez que se toca un "
                "archivo o carpeta nuevo, le pide permiso al usuario antes de leerlo."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Ruta completa del archivo, ej. '/home/aaron/Documents/notas.txt' o '~/tesis.txt'."},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file_path",
            "description": (
                "Crea o sobreescribe un archivo en CUALQUIER ruta del sistema con el "
                "contenido dado. La primera vez que se toca esa ruta pide permiso al "
                "usuario. Hace backup automático si el archivo ya existía."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Ruta completa donde guardar el archivo."},
                    "content": {"type": "string", "description": "Contenido completo a escribir en el archivo."},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file_path",
            "description": (
                "Reemplaza un texto exacto por otro dentro de CUALQUIER archivo del sistema "
                "por su ruta completa. La primera vez que se toca esa ruta pide permiso al "
                "usuario, y hace backup automático antes de modificar."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Ruta completa del archivo."},
                    "old": {"type": "string", "description": "Texto exacto a reemplazar."},
                    "new": {"type": "string", "description": "Texto nuevo."},
                },
                "required": ["path", "old", "new"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_file_permissions",
            "description": "Lista los archivos y carpetas para los que el usuario ya autorizó acceso permanente ('siempre').",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "forget_file_permission",
            "description": "Olvida un permiso de archivo/carpeta guardado previamente, para que K.A.N.Y.E. vuelva a pedir autorización la próxima vez.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Texto que debe contener la ruta guardada a olvidar."},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "type_document",
            "description": (
                "Escribe un texto largo LETRA POR LETRA, en tiempo real, dentro de la app que "
                "tenga el foco (ej. Microsoft Word), como si alguien lo estuviera tecleando. "
                "Usalo para dictar documentos largos (tesis, informes, ensayos): primero "
                "redactá el texto completo como respuesta normal para que el usuario lo revise "
                "y lo apruebe, y SOLO cuando confirme explícitamente que lo escriba, llamá a "
                "esta tool con ese mismo texto ya aprobado. No la uses para textos cortos "
                "(para eso está type_text). No bloquea la conversación: corre en segundo plano "
                "y empieza después de una cuenta regresiva para que el usuario pueda darle foco "
                "a la ventana correcta."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Texto completo y ya aprobado a escribir."},
                    "cps": {"type": "number", "description": "Velocidad en caracteres por segundo. Default 18."},
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "stop_typing",
            "description": "Detiene el tipeo largo (type_document) que esté en curso.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Escribe texto en la aplicación con foco actualmente, como si se tipeara con el teclado.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "uppercase": {"type": "boolean", "description": "True si el usuario pidió escribirlo en mayúsculas."},
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "keyboard_shortcut",
            "description": (
                "Ejecuta un atajo de teclado reconocido. Frases válidas: "
                + ", ".join(sorted(keyboard_actions.SHORTCUT_COMMANDS.keys()))
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "La frase exacta del atajo, ej. 'copia', 'selecciona todo', 'guarda el archivo'."},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mouse_move",
            "description": "Mueve el cursor del mouse en una dirección relativa a su posición actual (el asistente no ve la pantalla, así que no puede apuntar a coordenadas exactas).",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {"type": "string", "enum": ["arriba", "abajo", "izquierda", "derecha"]},
                    "distance": {"type": "integer", "description": "Píxeles a mover. Default 120."},
                },
                "required": ["direction"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mouse_click",
            "description": "Hace click con el mouse en la posición actual del cursor.",
            "parameters": {
                "type": "object",
                "properties": {
                    "button": {"type": "string", "enum": ["izquierdo", "derecho", "medio"]},
                    "double": {"type": "boolean", "description": "True para doble click."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mouse_scroll",
            "description": "Scrollea la pantalla hacia arriba o abajo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {"type": "string", "enum": ["arriba", "abajo"]},
                    "amount": {"type": "integer", "description": "Intensidad del scroll. Default 5."},
                },
                "required": ["direction"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mouse_drag",
            "description": "Arrastra manteniendo el botón izquierdo apretado mientras mueve el mouse en una dirección (para seleccionar texto o arrastrar elementos).",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {"type": "string", "enum": ["arriba", "abajo", "izquierda", "derecha"]},
                    "distance": {"type": "integer", "description": "Píxeles a arrastrar. Default 120."},
                },
                "required": ["direction"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "focus_status",
            "description": "Devuelve si hay un modo focus activo y qué sitios tiene bloqueados.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "focus_off",
            "description": "Desactiva el modo focus activo y desbloquea los sitios.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "start_it_help",
            "description": (
                "Activa el modo de ayuda remota: mira la pantalla y ejecuta acciones paso a paso "
                "(con confirmación del usuario en cada una) para resolver un problema visual o "
                "repetitivo, tipo soporte técnico remoto. Usalo SOLO cuando el usuario pida "
                "explícitamente ayuda con algo que ve en pantalla — no para tareas normales que ya "
                "cubren las otras herramientas."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "problem": {"type": "string", "description": "Qué hay que resolver mirando la pantalla."},
                },
                "required": ["problem"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_note",
            "description": "Guarda una nota persistente para recordar algo más allá de esta conversación (sobrevive el reinicio del asistente).",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Lo que hay que recordar."},
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_notes",
            "description": "Lista todas las notas guardadas, o las que coinciden con una búsqueda.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Texto a buscar en las notas. Vacío para listar todas."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "minimize_window",
            "description": "Minimiza la ventana activa (la que tiene el foco).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "toggle_maximize_window",
            "description": "Maximiza la ventana activa, o la restaura a su tamaño anterior si ya estaba maximizada.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_note",
            "description": "Borra la nota o notas guardadas que coincidan con un texto.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Texto que debe contener la nota a borrar."},
                },
                "required": ["query"],
            },
        },
    },
]


def _tool_open_app(args: dict) -> str:
    query = args.get("query", "").strip()
    if not query:
        return "Necesito el nombre de la app a abrir."
    if site_actions.open_site(query):
        return f"Abrí el sitio guardado '{query}'."
    app = app_resolver.find_best_app_match(query)
    if not app:
        return f"No encontré ninguna app parecida a '{query}'."
    if system_actions.open_application(app):
        return f"Abrí la app '{app['name']}'."
    return f"Encontré la app '{app['name']}' pero no pude abrirla."


def _tool_close_app(args: dict) -> str:
    query = args.get("query", "").strip()
    if not query:
        return "Necesito el nombre del programa a cerrar."
    if process_actions.close_application(query):
        return f"Cerré '{query}'."
    return f"No encontré un programa abierto parecido a '{query}'."


def _tool_open_folder(args: dict) -> str:
    name = args.get("name", "").strip()
    if folder_actions.open_folder(name):
        return "Carpeta abierta."
    return f"No pude abrir la carpeta '{name}'."


def _tool_web_search(args: dict) -> str:
    query = args.get("query", "").strip()
    if not query:
        return "Necesito qué buscar."
    web_search.search_google(query)
    return f"Abrí la búsqueda de '{query}' en Google."


def _tool_play_music(args: dict) -> str:
    query = args.get("query", "").strip()
    if not query:
        return "Necesito el nombre de la canción o artista."
    music_actions.play_on_youtube_music(query)
    return f"Reproduciendo '{query}' en YouTube Music."


_MEDIA_ACTIONS = {
    "play_pause": media_actions.media_play_pause,
    "next": media_actions.media_next,
    "previous": media_actions.media_previous,
    "volume_up": media_actions.volume_up,
    "volume_down": media_actions.volume_down,
    "mute": media_actions.volume_mute,
}


def _tool_media_control(args: dict) -> str:
    action = args.get("action", "")
    fn = _MEDIA_ACTIONS.get(action)
    if not fn:
        return f"Acción de multimedia no reconocida: '{action}'."
    return "Hecho." if fn() else "No pude ejecutar ese control multimedia."


def _tool_activate_mode(args: dict) -> str:
    name = args.get("name", "").strip()
    if not name:
        return "Necesito el nombre del modo a activar."
    result = mode_actions.activate_mode(name)
    return result if result else f"No existe el modo '{name}'."


def _tool_list_modes(args: dict) -> str:
    modes = mode_actions.load_modes()
    if not modes:
        return "No hay modos guardados."
    return "Modos disponibles: " + ", ".join(modes.keys())


def _tool_open_site(args: dict) -> str:
    name = args.get("name", "").strip()
    if site_actions.open_site(name):
        return f"Abrí el sitio '{name}'."
    return f"No tengo guardado un sitio parecido a '{name}'."


def _tool_add_site(args: dict) -> str:
    name = args.get("name", "").strip()
    url = args.get("url", "").strip()
    if not name or not url:
        return "Necesito el nombre y la URL del sitio."
    return f"Sitio '{name}' guardado." if site_actions.add_site(name, url) else "No pude guardar el sitio."


def _tool_read_file(args: dict) -> str:
    path = args.get("path", "").strip()
    workspace = args.get("workspace", "kanye")
    content = file_actions.read_file(path, workspace)
    if content is None:
        return "No pude leer ese archivo."
    if len(content) > 1200:
        return content[:1200] + "\n... (truncado)"
    return content


def _tool_search_in_file(args: dict) -> str:
    path = args.get("path", "").strip()
    text = args.get("text", "").strip()
    workspace = args.get("workspace", "kanye")
    found = file_actions.search_in_file(path, text, workspace)
    return f"Encontré '{text}' en {path}." if found else f"No encontré '{text}' en {path}."


def _tool_backup_file(args: dict) -> str:
    path = args.get("path", "").strip()
    workspace = args.get("workspace", "kanye")
    return "Backup creado." if file_actions.backup_file(path, workspace) else "No pude crear el backup."


def _tool_replace_in_file(args: dict) -> str:
    path = args.get("path", "").strip()
    old = args.get("old", "")
    new = args.get("new", "")
    workspace = args.get("workspace", "kanye")
    changed = file_actions.replace_in_file(path, old, new, workspace)
    return "Archivo modificado." if changed else "No se modificó el archivo (el usuario canceló la confirmación o el texto no coincide exacto)."


def _tool_read_file_path(args: dict) -> str:
    path = args.get("path", "").strip()
    if not path:
        return "Necesito la ruta del archivo."
    content = file_actions.read_file_anywhere(path)
    if content is None:
        return "No pude leer ese archivo (no existe o el usuario no autorizó el acceso)."
    if len(content) > 1200:
        return content[:1200] + "\n... (truncado)"
    return content


def _tool_write_file_path(args: dict) -> str:
    path = args.get("path", "").strip()
    content = args.get("content", "")
    if not path:
        return "Necesito la ruta del archivo."
    ok = file_actions.write_file_anywhere(path, content)
    return f"Archivo guardado en {path}." if ok else "No pude guardar el archivo (permiso denegado o error de escritura)."


def _tool_edit_file_path(args: dict) -> str:
    path = args.get("path", "").strip()
    old = args.get("old", "")
    new = args.get("new", "")
    if not path:
        return "Necesito la ruta del archivo."
    changed = file_actions.replace_in_file_anywhere(path, old, new)
    return "Archivo modificado." if changed else "No se modificó el archivo (permiso denegado, el archivo no existe, o el texto no coincide exacto)."


def _tool_list_file_permissions(args: dict) -> str:
    allowed = file_actions.load_permissions()
    if not allowed:
        return "No tengo ningún permiso de archivo guardado todavía."
    return "Tengo acceso permanente a:\n" + "\n".join(f"- {p}" for p in allowed)


def _tool_forget_file_permission(args: dict) -> str:
    query = args.get("query", "").strip()
    if not query:
        return "Necesito saber qué permiso olvidar."
    count = file_actions.forget_permission(query)
    return f"Olvidé {count} permiso(s) guardado(s)." if count else f"No tenía ningún permiso guardado con '{query}'."


def _tool_type_document(args: dict) -> str:
    text = args.get("text", "")
    cps = args.get("cps", 18.0)
    if not text:
        return "Necesito el texto ya aprobado a escribir."
    if keyboard_actions.is_typing():
        return "Ya estoy escribiendo algo — decime que lo pare antes de arrancar otro."
    ok = keyboard_actions.start_typing(text, cps=cps)
    return "Empecé a escribir en unos segundos, dale foco a la ventana donde querés el texto." if ok else "No pude empezar a escribir."


def _tool_stop_typing(args: dict) -> str:
    return "Paré de escribir." if keyboard_actions.stop_typing() else "No había ningún tipeo en curso."


def _tool_type_text(args: dict) -> str:
    text = args.get("text", "")
    uppercase = bool(args.get("uppercase", False))
    if not text:
        return "Necesito el texto a escribir."
    return "Texto escrito." if keyboard_actions.type_text(text, uppercase=uppercase) else "No pude escribir el texto."


def _tool_keyboard_shortcut(args: dict) -> str:
    name = args.get("name", "")
    return "Listo." if keyboard_actions.execute_shortcut(name) else f"No reconozco el atajo '{name}'."


def _tool_focus_status(args: dict) -> str:
    return focus_mode.time_info()


def _tool_focus_off(args: dict) -> str:
    if not focus_mode.is_active():
        return "No hay ningún modo focus activo."
    return "Focus desactivado." if focus_mode.deactivate(forced=True) else "No pude desactivar el focus."


def _tool_mouse_move(args: dict) -> str:
    direction = args.get("direction", "")
    distance = args.get("distance", 120)
    if mouse_actions.move(direction, distance):
        return f"Moví el mouse hacia {direction}."
    return f"No reconozco la dirección '{direction}'."


def _tool_mouse_click(args: dict) -> str:
    button = args.get("button", "izquierdo")
    double = bool(args.get("double", False))
    if mouse_actions.click(button, double):
        return "Doble click hecho." if double else "Click hecho."
    return "No pude hacer click."


def _tool_mouse_scroll(args: dict) -> str:
    direction = args.get("direction", "")
    amount = args.get("amount", 5)
    if mouse_actions.scroll(direction, amount):
        return f"Scrolleé hacia {direction}."
    return f"No reconozco la dirección '{direction}'."


def _tool_mouse_drag(args: dict) -> str:
    direction = args.get("direction", "")
    distance = args.get("distance", 120)
    if mouse_actions.drag(direction, distance):
        return f"Arrastré hacia {direction}."
    return f"No reconozco la dirección '{direction}'."


def _tool_start_it_help(args: dict) -> str:
    problem = args.get("problem", "")
    return it_worker.run(problem)


def _tool_add_note(args: dict) -> str:
    text = args.get("text", "")
    return "Nota guardada." if notes_actions.add_note(text) else "Necesito el texto de la nota."


def _tool_list_notes(args: dict) -> str:
    query = args.get("query", "")
    notes = notes_actions.search_notes(query) if query else notes_actions.list_notes()
    if not notes:
        return "No hay notas guardadas." if not query else f"No encontré notas sobre '{query}'."
    return "\n".join(f"- {n['text']}" for n in notes)


def _tool_delete_note(args: dict) -> str:
    query = args.get("query", "")
    if not query:
        return "Necesito saber qué nota borrar."
    count = notes_actions.delete_notes(query)
    return f"Borré {count} nota(s)." if count else f"No encontré ninguna nota con '{query}'."


def _tool_minimize_window(args: dict) -> str:
    return "Ventana minimizada." if window_actions.minimize_active() else "No pude minimizar la ventana activa."


def _tool_toggle_maximize_window(args: dict) -> str:
    return "Listo." if window_actions.toggle_maximize_active() else "No pude maximizar/restaurar la ventana activa."


_DISPATCH = {
    "open_app": _tool_open_app,
    "close_app": _tool_close_app,
    "open_folder": _tool_open_folder,
    "web_search": _tool_web_search,
    "play_music": _tool_play_music,
    "media_control": _tool_media_control,
    "activate_mode": _tool_activate_mode,
    "list_modes": _tool_list_modes,
    "open_site": _tool_open_site,
    "add_site": _tool_add_site,
    "read_file": _tool_read_file,
    "search_in_file": _tool_search_in_file,
    "backup_file": _tool_backup_file,
    "replace_in_file": _tool_replace_in_file,
    "read_file_path": _tool_read_file_path,
    "write_file_path": _tool_write_file_path,
    "edit_file_path": _tool_edit_file_path,
    "list_file_permissions": _tool_list_file_permissions,
    "forget_file_permission": _tool_forget_file_permission,
    "type_document": _tool_type_document,
    "stop_typing": _tool_stop_typing,
    "type_text": _tool_type_text,
    "keyboard_shortcut": _tool_keyboard_shortcut,
    "focus_status": _tool_focus_status,
    "focus_off": _tool_focus_off,
    "mouse_move": _tool_mouse_move,
    "mouse_click": _tool_mouse_click,
    "mouse_scroll": _tool_mouse_scroll,
    "mouse_drag": _tool_mouse_drag,
    "start_it_help": _tool_start_it_help,
    "minimize_window": _tool_minimize_window,
    "toggle_maximize_window": _tool_toggle_maximize_window,
    "add_note": _tool_add_note,
    "list_notes": _tool_list_notes,
    "delete_note": _tool_delete_note,
}


def call_tool(name: str, args: dict) -> str:
    fn = _DISPATCH.get(name)
    if not fn:
        return f"Herramienta desconocida: '{name}'."
    try:
        return fn(args or {})
    except Exception as error:
        return f"Error ejecutando '{name}': {error}"
