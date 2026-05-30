import subprocess


def open_application(app: dict) -> bool:
    try:
        if app.get("type") == "builtin":
            subprocess.Popen(app["command"], shell=True)
            return True

        if app.get("type") == "shortcut":
            subprocess.Popen([app["path"]])
            return True

        return False

    except Exception as error:
        print(f"Error al abrir la aplicación: {error}")
        return False