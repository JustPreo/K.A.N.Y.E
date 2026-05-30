import subprocess


def open_application(app: dict) -> bool:
    try:
        subprocess.Popen([app["path"]])
        return True
    except Exception as error:
        print(f"Error al abrir la aplicación: {error}")
        return False