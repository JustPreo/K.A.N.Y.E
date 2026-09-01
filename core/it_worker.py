"""
Modo "ayuda remota": screenshot → un modelo de visión (DeepSeek) decide UNA
acción concreta → se confirma con el usuario (core/gui.confirm_action) →
se ejecuta → nuevo screenshot → repite hasta terminar, cancelar, o llegar
al límite de pasos.

v1 no es autónomo a propósito: el modelo de visión (deepseek-v4-flash-
vision-exp) es genérico, no especializado en apuntar coordenadas exactas de
UI, así que cada acción se confirma antes de ejecutarla. Vive todo dentro
de un solo tool call (ver core/tools.py) — el loop agéntico normal
(core/agent.py) no se entera de los pasos intermedios, solo del resultado
final.
"""
import base64
import json
import re

from core.config_loader import get_config
from core import deepseek_client
from core import screen_actions
from core import mouse_actions
from core import keyboard_actions
from core import gui

_PROMPT_TEMPLATE = """Estás ayudando a resolver este problema en la computadora del usuario:
"{problem}"

Pasos ya ejecutados en este intento:
{history}

Mirá la captura de pantalla adjunta y decidí UNA sola acción siguiente.
Respondé ÚNICAMENTE con un objeto JSON, sin texto alrededor, con esta forma exacta:
{{"reasoning": "por qué, en una frase", "action": "click|type|key|scroll|done",
 "x": 0, "y": 0, "text": "", "key": "", "summary": ""}}

- "click": click en el punto (x, y) de la imagen (coordenadas en píxeles de la imagen tal cual se ve).
- "type": escribe el contenido de "text" (asume que ya hay foco en el campo correcto).
- "key": presiona la tecla o combinación en "key" (ej. "enter", "ctrl+s").
- "scroll": scrollea hacia abajo en el punto (x, y).
- "done": el problema ya está resuelto (o no se puede resolver así) — usá "summary" para explicar qué pasó, en español, con la personalidad de K.A.N.Y.E.
"""


def _extract_json(raw: str) -> dict | None:
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
    try:
        return json.loads(raw)
    except Exception:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except Exception:
            return None


def _describe(decision: dict) -> str:
    action = decision.get("action", "?")
    reasoning = decision.get("reasoning", "")
    if action == "click":
        detail = f"Click en ({decision.get('x')}, {decision.get('y')})"
    elif action == "type":
        detail = f"Escribir: \"{decision.get('text', '')}\""
    elif action == "key":
        detail = f"Presionar: {decision.get('key', '')}"
    elif action == "scroll":
        detail = f"Scroll en ({decision.get('x')}, {decision.get('y')})"
    else:
        detail = action
    return f"{detail}\n\n{reasoning}" if reasoning else detail


def _execute(decision: dict) -> bool:
    action = decision.get("action")
    if action == "click":
        return mouse_actions.click_at(int(decision.get("x", 0)), int(decision.get("y", 0)))
    if action == "type":
        return keyboard_actions.type_text(decision.get("text", ""))
    if action == "key":
        key = decision.get("key", "")
        if "+" in key:
            return keyboard_actions.hotkey(*key.split("+"))
        return keyboard_actions.press_key(key)
    if action == "scroll":
        mouse_actions.move_to(int(decision.get("x", 0)), int(decision.get("y", 0)))
        import pyautogui
        pyautogui.scroll(-5)
        return True
    return False


def run(problem: str) -> str:
    if not deepseek_client.is_configured():
        return ("Necesito una DeepSeek API key configurada para esto — "
                "andá a Configuración > Agente y agregala. Sin visión no puedo mirar la pantalla.")

    problem = (problem or "").strip()
    if not problem:
        return "Decime qué querés que resuelva mirando la pantalla."

    config = get_config()
    max_steps = config.get("it_worker_max_steps", 8)
    model = config.get("it_worker_model", "deepseek-v4-flash-vision-exp")

    history: list[str] = []

    for step in range(max_steps):
        image = screen_actions.capture()
        if image is None:
            return "No puedo capturar la pantalla en este escritorio (Wayland sin grim/wlroots, o algo falló)."

        image_b64 = base64.b64encode(image).decode("ascii")
        history_text = "\n".join(f"{i+1}. {h}" for i, h in enumerate(history)) or "(ninguno todavía)"
        prompt = _PROMPT_TEMPLATE.format(problem=problem, history=history_text)

        try:
            raw = deepseek_client.chat_vision(image_b64, prompt, model)
        except deepseek_client.DeepSeekError as error:
            return f"Falló la llamada al modelo de visión: {error}"

        decision = _extract_json(raw)
        if not decision or "action" not in decision:
            return "El modelo de visión no devolvió una acción entendible — probá de nuevo."

        if decision["action"] == "done":
            return decision.get("summary") or "Listo."

        target_xy = None
        if decision["action"] in ("click", "scroll"):
            target_xy = (int(decision.get("x", 0)), int(decision.get("y", 0)))

        approved = gui.confirm_action(image, _describe(decision), target_xy)
        if not approved:
            return f"Cancelado por el usuario en el paso {step + 1}."

        ok = _execute(decision)
        history.append(f"{decision['action']} — {'ok' if ok else 'falló'}: {decision.get('reasoning', '')}")

    return "Llegué al límite de pasos sin terminar — decime si seguimos."
