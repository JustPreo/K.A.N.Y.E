from pathlib import Path
from datetime import datetime
import shutil
import json


CONFIG_WORKSPACES = Path("config") / "workspaces.json"


def load_workspaces() -> dict:
    if not CONFIG_WORKSPACES.exists():
        return {
            "kanye": str(Path.cwd())
        }

    try:
        with open(CONFIG_WORKSPACES, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as error:
        print(f"K.A.N.Y.E.: Error leyendo workspaces.json: {error}")
        return {
            "kanye": str(Path.cwd())
        }


def get_workspace_root(workspace_name: str = "kanye") -> Path | None:
    workspaces = load_workspaces()
    workspace_name = workspace_name.lower().strip()

    if workspace_name not in workspaces:
        print(f"K.A.N.Y.E.: No existe el proyecto permitido '{workspace_name}'.")
        return None

    root = Path(workspaces[workspace_name]).resolve()

    if not root.exists():
        print(f"K.A.N.Y.E.: La carpeta del proyecto '{workspace_name}' no existe.")
        return None

    return root


def safe_path(file_path: str, workspace_name: str = "kanye") -> Path | None:
    """
    Convierte una ruta en una ruta segura dentro de un workspace permitido.
    Evita modificar archivos fuera del proyecto elegido.
    """
    try:
        root = get_workspace_root(workspace_name)

        if not root:
            return None

        path = (root / file_path).resolve()

        if not str(path).startswith(str(root)):
            print("K.A.N.Y.E.: No puedo acceder a archivos fuera del proyecto permitido.")
            return None

        return path

    except Exception as error:
        print(f"K.A.N.Y.E.: Error resolviendo ruta: {error}")
        return None


def read_file(file_path: str, workspace_name: str = "kanye") -> str | None:
    path = safe_path(file_path, workspace_name)

    if not path or not path.exists():
        print("K.A.N.Y.E.: No encontré ese archivo.")
        return None

    if not path.is_file():
        print("K.A.N.Y.E.: Esa ruta no es un archivo.")
        return None

    try:
        return path.read_text(encoding="utf-8")
    except Exception as error:
        print(f"K.A.N.Y.E.: Error leyendo archivo: {error}")
        return None


def backup_file(file_path: str, workspace_name: str = "kanye") -> bool:
    path = safe_path(file_path, workspace_name)

    if not path or not path.exists():
        print("K.A.N.Y.E.: No encontré ese archivo para hacer backup.")
        return False

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.with_suffix(path.suffix + f".bak_{timestamp}")

    try:
        shutil.copy2(path, backup_path)
        print(f"K.A.N.Y.E.: Backup creado en {backup_path}")
        return True
    except Exception as error:
        print(f"K.A.N.Y.E.: Error creando backup: {error}")
        return False


def search_in_file(file_path: str, search_text: str, workspace_name: str = "kanye") -> bool:
    content = read_file(file_path, workspace_name)

    if content is None:
        return False

    if search_text in content:
        print(f"K.A.N.Y.E.: Encontré '{search_text}' en {file_path}.")
        return True

    print(f"K.A.N.Y.E.: No encontré '{search_text}' en {file_path}.")
    return False


def replace_in_file(
    file_path: str,
    old_text: str,
    new_text: str,
    workspace_name: str = "kanye"
) -> bool:
    path = safe_path(file_path, workspace_name)

    if not path or not path.exists():
        print("K.A.N.Y.E.: No encontré ese archivo.")
        return False

    try:
        content = path.read_text(encoding="utf-8")

        if old_text not in content:
            print("K.A.N.Y.E.: No encontré el texto exacto a reemplazar.")
            return False

        print("\nK.A.N.Y.E.: Cambio propuesto:")
        print(f"Proyecto: {workspace_name}")
        print(f"Archivo: {file_path}")
        print(f"Reemplazar: {old_text}")
        print(f"Por: {new_text}")

        confirm = input("\n¿Confirmas el cambio? sí/no: ").lower().strip()

        if confirm not in ["si", "sí", "s"]:
            print("K.A.N.Y.E.: Cambio cancelado.")
            return False

        backup_ok = backup_file(file_path, workspace_name)

        if not backup_ok:
            print("K.A.N.Y.E.: No hice el cambio porque falló el backup.")
            return False

        new_content = content.replace(old_text, new_text, 1)
        path.write_text(new_content, encoding="utf-8")

        print("K.A.N.Y.E.: Archivo actualizado correctamente.")
        return True

    except Exception as error:
        print(f"K.A.N.Y.E.: Error reemplazando texto: {error}")
        return False