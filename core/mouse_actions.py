"""
Control de mouse por voz. Usa pyautogui, igual que keyboard_actions.py.

El LLM no ve la pantalla, así que no tiene sentido exponer movimiento a
coordenadas absolutas — se mueve relativo a la posición actual (direcciones)
para que un pedido como "mové el mouse a la derecha" sea algo que el agente
pueda ejecutar sin inventar coordenadas.
"""
import pyautogui

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.04

_DIRECTIONS = {
    "arriba": (0, -1), "up": (0, -1),
    "abajo": (0, 1), "down": (0, 1),
    "izquierda": (-1, 0), "left": (-1, 0),
    "derecha": (1, 0), "right": (1, 0),
}

_BUTTONS = {"izquierdo": "left", "left": "left",
            "derecho": "right", "right": "right",
            "medio": "middle", "middle": "middle"}


def move(direction: str, distance: int = 120) -> bool:
    delta = _DIRECTIONS.get(direction.lower().strip())
    if not delta:
        return False
    dx, dy = delta
    try:
        pyautogui.moveRel(dx * distance, dy * distance, duration=0.15)
        return True
    except Exception as error:
        print(f"K.A.N.Y.E.: Error moviendo el mouse: {error}")
        return False


def click(button: str = "left", double: bool = False) -> bool:
    btn = _BUTTONS.get(button.lower().strip(), "left")
    try:
        if double:
            pyautogui.doubleClick(button=btn)
        else:
            pyautogui.click(button=btn)
        return True
    except Exception as error:
        print(f"K.A.N.Y.E.: Error haciendo click: {error}")
        return False


def scroll(direction: str, amount: int = 5) -> bool:
    sign = 1 if direction.lower().strip() in ("arriba", "up") else -1
    try:
        pyautogui.scroll(sign * amount)
        return True
    except Exception as error:
        print(f"K.A.N.Y.E.: Error scrolleando: {error}")
        return False


def drag(direction: str, distance: int = 120) -> bool:
    """Mantiene el botón izquierdo mientras mueve — para seleccionar o arrastrar."""
    delta = _DIRECTIONS.get(direction.lower().strip())
    if not delta:
        return False
    dx, dy = delta
    try:
        pyautogui.dragRel(dx * distance, dy * distance, duration=0.2, button="left")
        return True
    except Exception as error:
        print(f"K.A.N.Y.E.: Error arrastrando: {error}")
        return False
