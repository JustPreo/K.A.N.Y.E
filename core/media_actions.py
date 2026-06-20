import subprocess

from core.platform_utils import is_windows


def _playerctl(command: str) -> bool:
    try:
        subprocess.run(
            ["playerctl", command],
            check=True,
            capture_output=True,
            timeout=5,
        )
        return True
    except FileNotFoundError:
        print("K.A.N.Y.E.: playerctl no instalado. Ejecutá: sudo apt install playerctl")
        return False
    except Exception as error:
        print(f"K.A.N.Y.E.: Error en playerctl: {error}")
        return False


def _pactl_volume(sign: str, percent: int = 5) -> bool:
    try:
        subprocess.run(
            ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{sign}{percent}%"],
            check=True,
            capture_output=True,
            timeout=5,
        )
        return True
    except FileNotFoundError:
        print("K.A.N.Y.E.: pactl no instalado. Instalá pulseaudio-utils.")
        return False
    except Exception as error:
        print(f"K.A.N.Y.E.: Error en pactl: {error}")
        return False


def _pactl_mute() -> bool:
    try:
        subprocess.run(
            ["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"],
            check=True,
            capture_output=True,
            timeout=5,
        )
        return True
    except Exception as error:
        print(f"K.A.N.Y.E.: Error silenciando: {error}")
        return False


def _pyautogui_press(key: str) -> bool:
    try:
        import pyautogui
        pyautogui.press(key)
        return True
    except Exception as error:
        print(f"K.A.N.Y.E.: Error en pyautogui: {error}")
        return False


def media_play_pause() -> bool:
    if is_windows():
        return _pyautogui_press("playpause")
    return _playerctl("play-pause")


def media_next() -> bool:
    if is_windows():
        return _pyautogui_press("nexttrack")
    return _playerctl("next")


def media_previous() -> bool:
    if is_windows():
        return _pyautogui_press("prevtrack")
    return _playerctl("previous")


def volume_up(steps: int = 5) -> bool:
    if is_windows():
        for _ in range(steps // 2 or 1):
            _pyautogui_press("volumeup")
        return True
    return _pactl_volume("+", steps)


def volume_down(steps: int = 5) -> bool:
    if is_windows():
        for _ in range(steps // 2 or 1):
            _pyautogui_press("volumedown")
        return True
    return _pactl_volume("-", steps)


def volume_mute() -> bool:
    if is_windows():
        return _pyautogui_press("volumemute")
    return _pactl_mute()
