import subprocess

from core.platform_utils import is_windows


def open_application(app: dict) -> bool:
    try:
        app_type = app.get("type")

        if app_type == "shortcut":
            # Windows .lnk shortcut
            subprocess.Popen([app["path"]])
            return True

        if app_type in ("builtin", "desktop"):
            subprocess.Popen(app["command"], shell=True)
            return True

        return False

    except Exception as error:
        print(f"K.A.N.Y.E.: Error al abrir la aplicación: {error}")
        return False
