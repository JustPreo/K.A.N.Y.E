import sys


def is_windows() -> bool:
    return sys.platform == "win32"


def is_linux() -> bool:
    return sys.platform.startswith("linux")


def get_platform() -> str:
    return "windows" if is_windows() else "linux"
