import os
import subprocess
from pathlib import Path


def get_folder_path(folder_name: str) -> Path | None:
    home = Path.home()
    folder_name = folder_name.lower().strip()

    folders = {
        "descargas": home / "Downloads",
        "downloads": home / "Downloads",

        "documentos": home / "Documents",
        "documents": home / "Documents",

        "escritorio": home / "Desktop",
        "desktop": home / "Desktop",

        "imágenes": home / "Pictures",
        "imagenes": home / "Pictures",
        "pictures": home / "Pictures",

        "videos": home / "Videos",

        "música": home / "Music",
        "musica": home / "Music",
        "music": home / "Music",
    }

    return folders.get(folder_name)


def open_folder(folder_name: str) -> bool:
    folder_path = get_folder_path(folder_name)

    if not folder_path:
        return False

    if not folder_path.exists():
        return False

    try:
        subprocess.Popen(["explorer", str(folder_path)])
        return True
    except Exception as error:
        print(f"Error al abrir carpeta: {error}")
        return False