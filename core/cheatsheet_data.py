"""
Datos de la hoja de comandos (panel "» COMANDOS" en core/gui.py). Frases de
ejemplo en español que el usuario puede tipear o decir por voz — agrupadas
por la misma división de tools que core/tools.py.
"""

CATEGORIES: list[dict] = [
    {"title": "Apps y ventanas", "items": [
        "Abrí Spotify",
        "Cerrá Firefox",
        "Minimizá la ventana",
        "Maximizá la ventana",
    ]},
    {"title": "Archivos y carpetas", "items": [
        "Abrí la carpeta descargas",
        "Leé el archivo notas.txt",
        'Buscá "presupuesto" en informe.txt',
        "Hacé un backup de tesis.docx",
        'Reemplazá "borrador" por "final" en informe.txt',
        "¿Qué archivos tenés permiso de tocar?",
    ]},
    {"title": "Música y multimedia", "items": [
        'Pon "Flashing Lights" de Kanye West',
        "Pausá la música",
        "Siguiente canción",
        "Subí el volumen",
        "Silenciá",
    ]},
    {"title": "Modos de trabajo", "items": [
        "Activá el modo estudio",
        "Listá mis modos",
    ]},
    {"title": "Sitios web", "items": [
        "Abrí YouTube",
        "Guardá el sitio Notion con la url notion.so",
        "Buscá en internet recetas de baleadas",
    ]},
    {"title": "Dictado y teclado", "items": [
        "Escribí: hola mundo",
        "Dictame este párrafo en Word",
        "Detené el dictado",
        "Copiá",
        "Pegá",
        "Seleccioná todo",
        "Presioná enter",
        "Guardá el archivo",
    ]},
    {"title": "Mouse", "items": [
        "Mové el mouse arriba",
        "Hacé click",
        "Doble click",
        "Scrolleá abajo",
    ]},
    {"title": "Modo enfoque", "items": [
        "Activá el modo enfoque",
        "¿Cómo va el enfoque?",
        "Desactivá el enfoque",
    ]},
    {"title": "Ayuda remota", "items": [
        "Ayudame con esto que veo en pantalla",
    ]},
    {"title": "Notas", "items": [
        "Anotá que tengo que pagar la luz el viernes",
        "Listá mis notas",
        "Borrá la nota de la luz",
    ]},
    {"title": "Combinados", "items": [
        'Pon "Flashing Lights" y abrí Dolphin',
        "Activá el modo estudio y abrí mis notas de física",
        "Cerrá Spotify y activá el modo enfoque",
    ]},
]
