import pyautogui


def media_play_pause() -> bool:
    try:
        pyautogui.press("playpause")
        return True
    except Exception as error:
        print(f"K.A.N.Y.E.: Error pausando/reanudando: {error}")
        return False


def media_next() -> bool:
    try:
        pyautogui.press("nexttrack")
        return True
    except Exception as error:
        print(f"K.A.N.Y.E.: Error pasando canción: {error}")
        return False


def media_previous() -> bool:
    try:
        pyautogui.press("prevtrack")
        return True
    except Exception as error:
        print(f"K.A.N.Y.E.: Error regresando canción: {error}")
        return False


def volume_up(steps: int = 3) -> bool:
    try:
        for _ in range(steps):
            pyautogui.press("volumeup")
        return True
    except Exception as error:
        print(f"K.A.N.Y.E.: Error subiendo volumen: {error}")
        return False


def volume_down(steps: int = 3) -> bool:
    try:
        for _ in range(steps):
            pyautogui.press("volumedown")
        return True
    except Exception as error:
        print(f"K.A.N.Y.E.: Error bajando volumen: {error}")
        return False


def volume_mute() -> bool:
    try:
        pyautogui.press("volumemute")
        return True
    except Exception as error:
        print(f"K.A.N.Y.E.: Error silenciando volumen: {error}")
        return False